from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.websockets.manager import manager
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSockets"])

# Internal schema for notifications
class NotificationPayload(BaseModel):
    user_id: str
    message: dict

async def get_current_user_ws(
    token: str = Query(...),
    db: Session = Depends(get_db)
) -> User:
    """Authenticate WebSocket connection via query param token"""
    payload = decode_access_token(token)
    
    if payload is None:
        # WebSocket cannot raise HTTP exceptions during handshake easily in some frameworks, 
        # but FastAPI handles it by closing with 1008 Policy Violation usually if dep fails
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
        
    return user

@router.websocket("")
async def websocket_endpoint(
    websocket: WebSocket,
    current_user: User = Depends(get_current_user_ws)
):
    user_id = str(current_user.id)
    await manager.connect(websocket, user_id)
    try:
        while True:
            # We just keep the connection open. Use receive_text to handle pings if needed.
            # For now, we only push data from server to client.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(websocket, user_id)

@router.post("/notify", status_code=202)
async def send_notification(payload: NotificationPayload):
    """
    Internal endpoint to trigger WebSocket broadcasts.
    In a real system, verify source specific key or ensure network isolation.
    """
    await manager.broadcast_to_user(payload.user_id, payload.message)
    return {"status": "sent"}
