from fastapi import APIRouter, BackgroundTasks, Depends, Request
from dependencies.auth_middleware import get_current_user
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from models.chat_session import ChatSession
from models.user import User
from pydantic import BaseModel
from typing import List, Optional
from fastapi import Query
from datetime import datetime

from services.chat_service import generate_title_background

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
        title="Untitled"
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    background_tasks.add_task(generate_title_background, new_session.id, session_in.prompt, db)

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

    sessions = query.limit(30).all()
    return sessions