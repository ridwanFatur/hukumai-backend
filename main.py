from fastapi import FastAPI
import logging
from fastapi.middleware.cors import CORSMiddleware

from api import auth, chat_session, user
from utils.config import CORS_ORIGINS
from models import *

app = FastAPI(
	title="Hukum AI",
    version="1.0.0", 
    redirect_slashes=False,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "App is Ready"}

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(chat_session.router)