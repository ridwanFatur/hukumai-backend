from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.user import User
from models.user_token import UserToken
from utils.email_utils import is_valid_email


def get_or_create_user(db: Session, email: str, name: str):
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user, False

    if not is_valid_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Email Format"
        )

    new_user = User(name=name, email=email)
    db.add(new_user)
    db.flush()

    user_token = UserToken(
        user_id=new_user.id,
        total_tokens=3
    )
    db.add(user_token)

    db.commit()
    db.refresh(new_user)

    return new_user, True


def get_user(db: Session, id: int) -> User:
    user = db.query(User).filter(User.id == id).first()
    if user:
        return user

    return None
