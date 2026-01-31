from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import List
from app.models.group import GroupType


class GroupCreate(BaseModel):
    name: str


class GroupMemberAdd(BaseModel):
    user_id: UUID4


class GroupResponse(BaseModel):
    id: UUID4
    name: str
    created_by: UUID4 | None
    type: GroupType
    is_archived: bool
    created_at: datetime
    member_count: int | None = None
    
    class Config:
        from_attributes = True


class GroupMemberResponse(BaseModel):
    user_id: UUID4
    user_name: str
    user_email: str
    joined_at: datetime


class GroupDetailResponse(GroupResponse):
    members: List[GroupMemberResponse]
