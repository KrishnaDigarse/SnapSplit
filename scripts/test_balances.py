import logging
import sys
import os

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app.database import SessionLocal
from app.models.user import User
from app.models.group import Group, GroupType
from app.models.group_member import GroupMember
from app.services import group_service
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_direct_group_members():
    db = SessionLocal()
    try:
        # 1. Find a DIRECT group
        direct_group = db.query(Group).filter(Group.type == GroupType.DIRECT).first()
        
        if not direct_group:
            logger.info("No DIRECT group found. Cannot test.")
            return

        logger.info(f"Testing with DIRECT Group ID: {direct_group.id}")
        
        # 2. Get a member of this group to act as current_user
        member_record = db.query(GroupMember).filter(GroupMember.group_id == direct_group.id).first()
        current_user = db.query(User).filter(User.id == member_record.user_id).first()
        
        logger.info(f"Acting as user: {current_user.name} ({current_user.id})")
        
        # 3. Call get_group_detail
        group_detail = group_service.get_group_detail(db, current_user, direct_group.id)
        
        # 4. Check members
        members = group_detail.get('members', [])
        logger.info(f"Found {len(members)} members:")
        for m in members:
            logger.info(f"- {m['user_name']} ({m['user_id']})")
            
        if len(members) < 2:
            logger.error("FAIL: Direct group should have at least 2 members")
        else:
            logger.info("SUCCESS: Members retrieved correctly")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_direct_group_members()
