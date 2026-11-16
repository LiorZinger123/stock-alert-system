import logging
from fastapi import APIRouter, WebSocket
from services.wb_connection_manager import ws_connection_manager


router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/{user_id}")
async def alerts_status_change(websocket: WebSocket, user_id: int):
    await ws_connection_manager.connect(websocket, user_id)
    try:
        await websocket.receive_text() 
    except Exception:
        ws_connection_manager.disconnect(user_id)
