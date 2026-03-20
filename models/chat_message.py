from sqlalchemy import Column, Integer, String, Text
from db.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from sqlalchemy import Column, Integer, ForeignKey, DateTime

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    
    role = Column(String) 
    content = Column(Text)
    
    tokens_usage = Column(Integer, nullable=True) 
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )  
    session = relationship("ChatSession", back_populates="messages")