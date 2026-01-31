from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.friend import FriendRequestCreate, FriendRequestResponse, FriendResponse
from app.services import friend_service
from typing import List
import uuid

router = APIRouter(prefix="/friends", tags=["Friends"])


@router.post("/request", response_model=FriendRequestResponse, status_code=status.HTTP_201_CREATED)
def send_friend_request(
    request_data: FriendRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a friend request"""
    return friend_service.create_friend_request(db, current_user, request_data.receiver_id)


@router.post("/accept/{request_id}", status_code=status.HTTP_200_OK)
def accept_friend_request(
    request_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Accept a friend request and create DIRECT group"""
    return friend_service.accept_friend_request(db, current_user, request_id)


@router.post("/reject/{request_id}", response_model=FriendRequestResponse)
def reject_friend_request(
    request_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reject a friend request"""
    return friend_service.reject_friend_request(db, current_user, request_id)


@router.get("", response_model=List[FriendResponse])
def get_friends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of friends"""
    return friend_service.get_friends(db, current_user)
