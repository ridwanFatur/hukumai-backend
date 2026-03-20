from fastapi import APIRouter, Depends, Request
from db.database import get_db
from dependencies.auth_middleware import get_current_user
from models.user_token import UserToken
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/api/user",
    tags=["user"],
    dependencies=[Depends(get_current_user)]
)


@router.get("/")
async def fetch_user(request: Request):
    return {
        "user": request.state.user
    }

@router.get("/token")
async def fetch_user_token(request: Request, db: Session = Depends(get_db)):
    user = request.state.user
    user_token = db.query(UserToken).filter(UserToken.user_id == user.id).first()
    if not user_token:
        return {
            "total_tokens": 0
        }

    return {
        "total_tokens": user_token.total_tokens,
        "updated_at": user_token.updated_at
    }