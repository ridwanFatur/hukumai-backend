from fastapi import Depends, Request, HTTPException, status
import jwt
from jwt import PyJWTError
from sqlalchemy.orm import Session
from db.database import get_db
from services.user_service import get_user
from utils.config import ALGORITHM, SECRET_KEY


def parse_jwt_for_user_id(request: Request):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    if token.startswith("Bearer "):
        token = token[7:]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id


async def get_current_user_id(request: Request):
    user_id = parse_jwt_for_user_id(request)
    request.state.user_id = user_id


async def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = parse_jwt_for_user_id(request)
    user = get_user(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    request.state.user = user
