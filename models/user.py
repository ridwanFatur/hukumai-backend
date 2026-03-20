from sqlalchemy import Column, Integer, String
from db.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import DateTime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tokens = relationship("UserToken", back_populates="user", uselist=False)
    sessions = relationship("ChatSession", back_populates="user")