import json

from sqlalchemy.orm import Session
from models.chat_session import ChatSession
import time
from utils.connection_manager import ws_manager
import asyncio

def generate_title_background(user_id: int, session_id: int, prompt: str, db_session: Session):
    time.sleep(5)
    generated_title = f"Generated title for '{prompt[:20]}...'"
    chat_session = db_session.query(ChatSession).filter(ChatSession.id == session_id).first()
    if chat_session:
        chat_session.title = generated_title
        db_session.commit()
        payload = {
			"action": "reload_history"
		}
        if ws_manager.loop:
            asyncio.run_coroutine_threadsafe(
                ws_manager.send_to_user(user_id, json.dumps(payload)),
                ws_manager.loop
            )