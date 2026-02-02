from pydantic import BaseModel, UUID4, EmailStr
from datetime import datetime
from app.models.friend_request import FriendRequestStatus


class FriendRequestCreate(BaseModel):
    friend_email: EmailStr


class FriendRequestResponse(BaseModel):
    id: UUID4
    sender_id: UUID4
    receiver_id: UUID4
    status: FriendRequestStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


class FriendResponse(BaseModel):
    user_id: UUID4
    friend_id: UUID4
    friend_name: str
    friend_email: str
    created_at: datetime
