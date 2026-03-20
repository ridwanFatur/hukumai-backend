import asyncio

from fastapi import WebSocket
from typing import Dict

import jwt

from utils.config import ALGORITHM, SECRET_KEY


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.loop = None

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        if self.loop is None:
            self.loop = asyncio.get_running_loop() 

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_to_user(self, user_id: int, message: str):
        websocket = self.active_connections.get(user_id)

        if websocket:
            await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)
            
async def verify_websocket_token(websocket: WebSocket, user_id: int) -> dict | None:
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_user_id = payload.get("user_id")

        if token_user_id != user_id:
            await websocket.close(code=1008)
            return None

        return payload
    except jwt.PyJWTError:
        await websocket.close(code=1008)
        return None

ws_manager = ConnectionManager()