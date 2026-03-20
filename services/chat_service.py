from sqlalchemy.orm import Session
from models.chat_session import ChatSession
import time

def generate_title_background(session_id: int, prompt: str, db_session: Session):
    time.sleep(5)
    generated_title = f"Generated title for '{prompt[:20]}...'"
    chat_session = db_session.query(ChatSession).filter(ChatSession.id == session_id).first()
    if chat_session:
        chat_session.title = generated_title
        db_session.commit()