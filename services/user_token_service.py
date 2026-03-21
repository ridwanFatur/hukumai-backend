from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models import UserToken

def check_tokens(db: Session, user_id: int):
    user_token = db.query(UserToken).filter(UserToken.user_id == user_id).first()
    if not user_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User token not found"
        )
    if user_token.total_tokens <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
				"message": "Insufficient tokens",
            	"error_code": "insufficient_tokens",
			}
        )
    return user_token

def deduct_tokens(db: Session, user_id: int, amount: int = 1):
    user_token = check_tokens(db, user_id)
    
    if user_token.total_tokens < amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough tokens to deduct"
        )
    
    user_token.total_tokens -= amount
    db.add(user_token)
    db.commit()
    db.refresh(user_token)
    return user_token