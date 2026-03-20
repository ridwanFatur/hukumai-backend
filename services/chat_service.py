import json

from fastapi import BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.chat_message import ChatMessage
from models.chat_session import ChatSession
import time
from utils.connection_manager import ws_manager
import asyncio

def generate_title_background(user_id: int, session_id: int, prompt: str):
    db = SessionLocal()
    try:
        time.sleep(5)
        generated_title = f"Generated title for '{prompt[:20]}...'"
        chat_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if chat_session:
            chat_session.title = generated_title
            db.commit()
            payload = {
				"action": "update_history",
				"session_id": session_id,
				"title": generated_title
			}
            if ws_manager.loop:
                asyncio.run_coroutine_threadsafe(
					ws_manager.send_to_user(user_id, json.dumps(payload)),
					ws_manager.loop
                )
    finally:
        db.close()
            
def handle_send_message(
    db: Session,
    session: ChatSession,
    content: str,
    background_tasks: BackgroundTasks, 
    user_id: int
):
    if session.is_thinking:
        raise HTTPException(
            status_code=400,
            detail="AI is still thinking, please wait"
        )
        
    # set thinking
    session.is_thinking = True
    db.commit()  
     
    message = ChatMessage(
        session_id=session.id,
        role="user",
        content=content
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    
    background_tasks.add_task(
        generate_ai_response,
        session.id,
        content,
        user_id
    )
    return message
    
                         
def generate_ai_response(session_id: int, user_message: str, user_id: int):
    db = SessionLocal()
    try:
        time.sleep(5)
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            return
        ai_response = f"Response for: {user_message}"
        message = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=ai_response
        )
        db.add(message)
        session.is_thinking = False
        
        db.commit()
        db.refresh(message)
        
        # Notify
        payload = {
				"action": "update_message",
				"session_id": session_id,
				"message": ai_response,
				"message_id": message.id,
			}
        if ws_manager.loop:
            asyncio.run_coroutine_threadsafe(
				ws_manager.send_to_user(user_id, json.dumps(payload)),
				ws_manager.loop
			)
    finally:
        db.close()