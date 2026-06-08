import logging
from helpers.security import get_current_user_id
from fastapi import APIRouter, status, Depends, Request


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("", status_code=status.HTTP_200_OK)
async def verify_user(request: Request, user_id: int = Depends(get_current_user_id)):
    user_payload = request.state.user
    username = user_payload.get("username")
    
    return {
        "user_id": user_id,
        "username": username
    }
