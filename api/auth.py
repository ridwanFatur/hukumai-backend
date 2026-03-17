from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import jwt
from db.database import get_db
from services.google_service import get_google_user_details
from services.user_service import get_or_create_user
from datetime import datetime, timedelta, timezone

from utils.config import ALGORITHM, GOOGLE_CLIENT_ID, SECRET_KEY


router = APIRouter(
    prefix="/api/auth",
    tags=["auth"]
)


class AuthRequest(BaseModel):
    auth_code: str
    
@router.post("/login")
async def login(auth: AuthRequest, db: Session = Depends(get_db)):
    google_account = get_google_user_details(auth.auth_code)
    email = google_account["email"]
    name = google_account["name"]
    user, is_created = get_or_create_user(db, email, name)
    payload = {
        "user_id": user.id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "user": user,
        "status": "created" if is_created else "existing",
        "token": token
    }


@router.get("/google/config")
async def get_google_config():
    return {
        "client_id": GOOGLE_CLIENT_ID
    }