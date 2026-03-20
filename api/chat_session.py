from fastapi import APIRouter, BackgroundTasks, Depends, Request
from dependencies.auth_middleware import get_current_user
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from models.chat_message import ChatMessage
from models.chat_session import ChatSession
from models.user import User
from pydantic import BaseModel
from typing import List, Optional
from fastapi import Query
from datetime import datetime
from sqlalchemy import desc
from services.chat_service import generate_ai_response, generate_title_background, handle_send_message

router = APIRouter(
    prefix="/api/chat-session",
    tags=["chat-session"],
    dependencies=[Depends(get_current_user)]
)

class ChatSessionCreate(BaseModel):
    prompt: str

class ChatSessionOut(BaseModel):
    id: int
    user_id: int
    title: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
        
    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            user_id=obj.user_id,
            title=obj.title,
            created_at=obj.created_at.isoformat(),
            updated_at=obj.updated_at.isoformat()
        )
                
@router.post("/", response_model=ChatSessionOut)
async def create_chat_session(
    session_in: ChatSessionCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    user: User = request.state.user
    new_session = ChatSession(
        user_id=user.id,
        title="New Chat"
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    handle_send_message(
        db,
        new_session,
        session_in.prompt,
        background_tasks,
        user_id=user.id
    )
    
    background_tasks.add_task(generate_title_background, user.id, new_session.id, session_in.prompt)

    return new_session

@router.get("/", response_model=List[ChatSessionOut])
async def get_chat_sessions(
    request: Request, 
    db: Session = Depends(get_db),
    title: Optional[str] = Query(None)
):
    user: User = request.state.user
    query = db.query(ChatSession).filter(ChatSession.user_id == user.id)

    if title:
        query = query.filter(ChatSession.title.ilike(f"%{title}%")) 

    sessions = query.order_by(desc(ChatSession.created_at)).limit(30).all()
    return sessions

class SendMessageRequest(BaseModel):
    session_id: int
    content: str
    
@router.post("/send-message")
async def send_message(
    payload: SendMessageRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    user: User = request.state.user
    session = db.query(ChatSession).filter(
        ChatSession.id == payload.session_id,
        ChatSession.user_id == user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    message = handle_send_message(
        db,
        session,
        payload.content,
        background_tasks,
        user.id
    )

    return {
        "message": "Message sent",
        "data": message
    }
    
class ChatMessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class ChatSessionDetailOut(BaseModel):
    id: int
    user_id: int
    title: Optional[str]
    is_thinking: bool
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageOut]

    model_config = {
        "from_attributes": True
    }
    
@router.get("/{session_id}", response_model=ChatSessionDetailOut)
async def get_chat_session_detail(
    session_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user: User = request.state.user

    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return session