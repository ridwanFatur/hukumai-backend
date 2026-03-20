from fastapi import APIRouter, Depends, Request
from dependencies.auth_middleware import get_current_user
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from models.chat_session import ChatSession
from models.user import User
from pydantic import BaseModel
from typing import List, Optional
from fastapi import Query

router = APIRouter(
    prefix="/api/chat-session",
    tags=["chat-session"],
    dependencies=[Depends(get_current_user)]
)

class ChatSessionCreate(BaseModel):
    title: Optional[str] = None

class ChatSessionOut(BaseModel):
    id: int
    user_id: int
    title: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True

class ChatMessageOut(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    created_at: str

    class Config:
        orm_mode = True

class ChatSessionDetailOut(BaseModel):
    id: int
    user_id: int
    title: Optional[str]
    created_at: str
    updated_at: str
    messages: List[ChatMessageOut] = []

    class Config:
        orm_mode = True
                
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

    sessions = query.all()
    return sessions

@router.post("/", response_model=ChatSessionOut)
async def create_chat_session(
    session_in: ChatSessionCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    user: User = request.state.user
    new_session = ChatSession(
        user_id=user.id,
        title=session_in.title
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@router.delete("/{session_id}", response_model=dict)
async def delete_chat_session(session_id: int, request: Request, db: Session = Depends(get_db)):
    user: User = request.state.user
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == user.id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found")
    db.delete(session)
    db.commit()
    return {"detail": "Chat session deleted successfully"}

@router.get("/{session_id}", response_model=ChatSessionDetailOut)
async def get_chat_session_detail(session_id: int, request: Request, db: Session = Depends(get_db)):
    user: User = request.state.user
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user.id
    ).first()

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found")
    return session