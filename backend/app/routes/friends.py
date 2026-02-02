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
    """Send a friend request by email"""
    # Look up receiver by email
    receiver = db.query(User).filter(User.email == request_data.friend_email).first()
    if not receiver:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {request_data.friend_email} not found"
        )
    
    return friend_service.create_friend_request(db, current_user, receiver.id)


@router.post("/request/{request_id}/accept", status_code=status.HTTP_200_OK)
def accept_friend_request(
    request_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Accept a friend request and create DIRECT group"""
    return friend_service.accept_friend_request(db, current_user, request_id)


@router.post("/request/{request_id}/reject", response_model=FriendRequestResponse)
def reject_friend_request(
    request_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reject a friend request"""
    return friend_service.reject_friend_request(db, current_user, request_id)


@router.get("/requests", response_model=List[dict])
def get_pending_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get pending friend requests for current user"""
    from app.models.friend_request import FriendRequest, FriendRequestStatus
    
    # Get requests where current user is the receiver
    requests = db.query(FriendRequest, User).join(
        User, FriendRequest.sender_id == User.id
    ).filter(
        FriendRequest.receiver_id == current_user.id,
        FriendRequest.status == FriendRequestStatus.PENDING
    ).all()
    
    result = []
    for request, sender in requests:
        result.append({
            "id": request.id,
            "sender_id": request.sender_id,
            "sender_name": sender.name,
            "sender_email": sender.email,
            "created_at": request.created_at
        })
    
    return result


@router.get("", response_model=List[FriendResponse])
def get_friends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of friends"""
    return friend_service.get_friends(db, current_user)


@router.get("/{friend_id}/direct-group")
def get_direct_group(
    friend_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the DIRECT group for a specific friend"""
    return friend_service.get_direct_group(db, current_user, friend_id)


@router.delete("/{friend_id}", status_code=status.HTTP_200_OK)
def remove_friend(
    friend_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a friend"""
    return friend_service.remove_friend(db, current_user, friend_id)
