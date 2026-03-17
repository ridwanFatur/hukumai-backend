from fastapi import APIRouter, Depends, Request
from dependencies.auth_middleware import get_current_user

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
