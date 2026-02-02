from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from app.models.user import User
from app.models.friend_request import FriendRequest, FriendRequestStatus
from app.models.friend import Friend
from app.models.group import Group, GroupType
from app.models.group_member import GroupMember
from typing import List
import uuid


def create_friend_request(db: Session, sender: User, receiver_id: uuid.UUID) -> FriendRequest:
    """Create a friend request"""
    if sender.id == receiver_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot send friend request to yourself"
        )
    
    receiver = db.query(User).filter(User.id == receiver_id).first()
    if not receiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    existing_request = db.query(FriendRequest).filter(
        ((FriendRequest.sender_id == sender.id) & (FriendRequest.receiver_id == receiver_id)) |
        ((FriendRequest.sender_id == receiver_id) & (FriendRequest.receiver_id == sender.id))
    ).filter(FriendRequest.status == FriendRequestStatus.PENDING).first()
    
    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Friend request already exists"
        )
    
    existing_friendship = db.query(Friend).filter(
        ((Friend.user_id == sender.id) & (Friend.friend_id == receiver_id)) |
        ((Friend.user_id == receiver_id) & (Friend.friend_id == sender.id))
    ).first()
    
    if existing_friendship:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already friends"
        )
    
    friend_request = FriendRequest(
        sender_id=sender.id,
        receiver_id=receiver_id,
        status=FriendRequestStatus.PENDING
    )
    
    db.add(friend_request)
    db.commit()
    db.refresh(friend_request)
    return friend_request


def accept_friend_request(db: Session, current_user: User, request_id: uuid.UUID) -> dict:
    """Accept a friend request and create DIRECT group"""
    friend_request = db.query(FriendRequest).filter(FriendRequest.id == request_id).first()
    
    if not friend_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friend request not found"
        )
    
    if friend_request.receiver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to accept this request"
        )
    
    if friend_request.status != FriendRequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Friend request already processed"
        )
    
    friend_request.status = FriendRequestStatus.ACCEPTED
    
    friend1 = Friend(
        user_id=friend_request.sender_id,
        friend_id=friend_request.receiver_id
    )
    friend2 = Friend(
        user_id=friend_request.receiver_id,
        friend_id=friend_request.sender_id
    )
    
    db.add(friend1)
    db.add(friend2)
    
    sender = db.query(User).filter(User.id == friend_request.sender_id).first()
    receiver = db.query(User).filter(User.id == friend_request.receiver_id).first()
    
    direct_group = Group(
        name=f"{sender.name} & {receiver.name}",
        created_by=current_user.id,
        type=GroupType.DIRECT,
        is_archived=False
    )
    
    db.add(direct_group)
    db.flush()
    
    member1 = GroupMember(group_id=direct_group.id, user_id=sender.id)
    member2 = GroupMember(group_id=direct_group.id, user_id=receiver.id)
    
    db.add(member1)
    db.add(member2)
    
    db.commit()
    db.refresh(friend_request)
    
    return {
        "message": "Friend request accepted",
        "direct_group_id": str(direct_group.id)
    }


def reject_friend_request(db: Session, current_user: User, request_id: uuid.UUID) -> FriendRequest:
    """Reject a friend request"""
    friend_request = db.query(FriendRequest).filter(FriendRequest.id == request_id).first()
    
    if not friend_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friend request not found"
        )
    
    if friend_request.receiver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to reject this request"
        )
    
    if friend_request.status != FriendRequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Friend request already processed"
        )
    
    friend_request.status = FriendRequestStatus.REJECTED
    db.commit()
    db.refresh(friend_request)
    return friend_request


def get_friends(db: Session, current_user: User) -> List[dict]:
    """Get list of friends for current user"""
    friends = db.query(Friend, User).join(
        User, Friend.friend_id == User.id
    ).filter(Friend.user_id == current_user.id).all()
    
    result = []
    for friend, user in friends:
        result.append({
            "user_id": friend.user_id,
            "friend_id": friend.friend_id,
            "friend_name": user.name,
            "friend_email": user.email,
            "created_at": friend.created_at
        })
    
    return result


def remove_friend(db: Session, current_user: User, friend_id: uuid.UUID) -> dict:
    """Remove a friend and delete the DIRECT group"""
    # Find the friendship (bidirectional)
    friendship1 = db.query(Friend).filter(
        Friend.user_id == current_user.id,
        Friend.friend_id == friend_id
    ).first()
    
    friendship2 = db.query(Friend).filter(
        Friend.user_id == friend_id,
        Friend.friend_id == current_user.id
    ).first()
    
    if not friendship1 and not friendship2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friendship not found"
        )
    
    # Find and delete the DIRECT group
    from app.models.group_member import GroupMember
    from app.models.expense import Expense
    from app.models.expense_item import ExpenseItem
    from app.models.split import Split
    
    # Find DIRECT group with both users
    direct_group = db.query(Group).filter(
        Group.type == GroupType.DIRECT
    ).join(
        GroupMember, Group.id == GroupMember.group_id
    ).filter(
        GroupMember.user_id.in_([current_user.id, friend_id])
    ).group_by(Group.id).having(
        func.count(GroupMember.user_id) == 2
    ).first()
    
    if direct_group:
        # Delete all related data
        expenses = db.query(Expense).filter(Expense.group_id == direct_group.id).all()
        for expense in expenses:
            items = db.query(ExpenseItem).filter(ExpenseItem.expense_id == expense.id).all()
            for item in items:
                db.query(Split).filter(Split.expense_item_id == item.id).delete()
            db.query(ExpenseItem).filter(ExpenseItem.expense_id == expense.id).delete()
        
        db.query(Expense).filter(Expense.group_id == direct_group.id).delete()
        db.query(GroupMember).filter(GroupMember.group_id == direct_group.id).delete()
        db.delete(direct_group)
    
    # Delete friendships
    if friendship1:
        db.delete(friendship1)
    if friendship2:
        db.delete(friendship2)
    
    db.commit()
    
    return {"message": "Friend removed successfully"}


def get_direct_group(db: Session, current_user: User, friend_id: uuid.UUID) -> dict:
    """Get the DIRECT group for a specific friend"""
    # Verify friendship exists
    friendship = db.query(Friend).filter(
        Friend.user_id == current_user.id,
        Friend.friend_id == friend_id
    ).first()
    
    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friendship not found"
        )
    
    # Find DIRECT group with both users
    direct_group = db.query(Group).filter(
        Group.type == GroupType.DIRECT
    ).join(
        GroupMember, Group.id == GroupMember.group_id
    ).filter(
        GroupMember.user_id.in_([current_user.id, friend_id])
    ).group_by(Group.id).having(
        func.count(GroupMember.user_id) == 2
    ).first()
    
    if not direct_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DIRECT group not found for this friendship"
        )
    
    return {
        "group_id": direct_group.id,
        "group_name": direct_group.name,
        "created_at": direct_group.created_at
    }
