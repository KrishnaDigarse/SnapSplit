from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.group import GroupCreate, GroupMemberAdd, GroupResponse, GroupDetailResponse
from app.services import group_service
from typing import List
import uuid

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new group"""
    return group_service.create_group(db, current_user, group_data)


@router.post("/{group_id}/add-member", status_code=status.HTTP_200_OK)
def add_member(
    group_id: uuid.UUID,
    member_data: GroupMemberAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a member to a group (creator only)"""
    return group_service.add_member_to_group(db, current_user, group_id, member_data)


@router.get("", response_model=List[GroupResponse])
def get_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all groups (excluding DIRECT groups)"""
    return group_service.get_groups(db, current_user)


@router.get("/{group_id}", response_model=GroupDetailResponse)
def get_group(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get group details"""
    return group_service.get_group_detail(db, current_user, group_id)
