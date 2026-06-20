import logging
from fastapi import APIRouter, WebSocket
from services.connection_manager import manager


router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/alerts/{user_id}")
async def alerts_status_change(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    try:
        await websocket.receive_text() 
    except Exception:
        manager.disconnect(user_id)
