from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.models.group import Group, GroupType
from app.models.group_member import GroupMember
from app.models.expense import Expense
from app.models.expense_item import ExpenseItem
from app.models.split import Split
from app.schemas.group import GroupCreate, GroupMemberAdd
from typing import List
import uuid


def create_group(db: Session, current_user: User, group_data: GroupCreate) -> Group:
    """Create a new group"""
    group = Group(
        name=group_data.name,
        created_by=current_user.id,
        type=GroupType.GROUP,
        is_archived=False
    )
    
    db.add(group)
    db.flush()
    
    creator_member = GroupMember(
        group_id=group.id,
        user_id=current_user.id
    )
    db.add(creator_member)
    
    db.commit()
    db.refresh(group)
    return group


def add_member_to_group(db: Session, current_user: User, group_id: uuid.UUID, member_data: GroupMemberAdd) -> dict:
    """Add a member to a group"""
    group = db.query(Group).filter(Group.id == group_id).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    if group.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only group creator can add members"
        )
    
    user_to_add = db.query(User).filter(User.id == member_data.user_id).first()
    if not user_to_add:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    existing_member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == member_data.user_id
    ).first()
    
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member"
        )
    
    new_member = GroupMember(
        group_id=group_id,
        user_id=member_data.user_id
    )
    
    db.add(new_member)
    db.commit()
    
    return {"message": "Member added successfully"}


def get_groups(db: Session, current_user: User) -> List[dict]:
    """Get all groups for current user (excluding DIRECT groups)"""
    groups = db.query(Group).join(
        GroupMember, Group.id == GroupMember.group_id
    ).filter(
        GroupMember.user_id == current_user.id,
        Group.type == GroupType.GROUP,
        Group.is_archived == False
    ).all()
    
    result = []
    for group in groups:
        member_count = db.query(GroupMember).filter(GroupMember.group_id == group.id).count()
        result.append({
            "id": group.id,
            "name": group.name,
            "created_by": group.created_by,
            "type": group.type,
            "is_archived": group.is_archived,
            "created_at": group.created_at,
            "member_count": member_count
        })
    
    return result


def get_group_detail(db: Session, current_user: User, group_id: uuid.UUID) -> dict:
    """Get detailed information about a group"""
    group = db.query(Group).filter(Group.id == group_id).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    is_member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id
    ).first()
    
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )
    
    members = db.query(GroupMember, User).join(
        User, GroupMember.user_id == User.id
    ).filter(GroupMember.group_id == group_id).all()
    
    member_list = []
    for member, user in members:
        member_list.append({
            "user_id": user.id,
            "user_name": user.name,
            "user_email": user.email,
            "joined_at": member.joined_at
        })
    
    return {
        "id": group.id,
        "name": group.name,
        "created_by": group.created_by,
        "type": group.type,
        "is_archived": group.is_archived,
        "created_at": group.created_at,
        "member_count": len(member_list),
        "members": member_list
    }


def delete_group(db: Session, current_user: User, group_id: uuid.UUID) -> dict:
    """Delete a group (creator only)"""
    group = db.query(Group).filter(Group.id == group_id).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    if group.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only group creator can delete the group"
        )
    
    # Delete all related data
    # 1. Delete splits
    expenses = db.query(Expense).filter(Expense.group_id == group_id).all()
    for expense in expenses:
        items = db.query(ExpenseItem).filter(ExpenseItem.expense_id == expense.id).all()
        for item in items:
            db.query(Split).filter(Split.expense_item_id == item.id).delete()
        db.query(ExpenseItem).filter(ExpenseItem.expense_id == expense.id).delete()
    
    # 2. Delete expenses
    db.query(Expense).filter(Expense.group_id == group_id).delete()
    
    # 3. Delete group members
    db.query(GroupMember).filter(GroupMember.group_id == group_id).delete()
    
    # 4. Delete group
    db.delete(group)
    db.commit()
    
    return {"message": "Group deleted successfully"}


def remove_member_from_group(db: Session, current_user: User, group_id: uuid.UUID, user_id: uuid.UUID) -> dict:
    """Remove a member from group (creator only)"""
    group = db.query(Group).filter(Group.id == group_id).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    if group.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only group creator can remove members"
        )
    
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove yourself from the group"
        )
    
    member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not a member of this group"
        )
    
    db.delete(member)
    db.commit()
    
    return {"message": "Member removed successfully"}


def leave_group(db: Session, current_user: User, group_id: uuid.UUID) -> dict:
    """Leave a group (non-creators only)"""
    group = db.query(Group).filter(Group.id == group_id).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    if group.created_by == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group creators cannot leave the group. You must delete the group instead."
        )
    
    member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not a member of this group"
        )
    
    db.delete(member)
    db.commit()
    
    return {"message": "Left group successfully"}
