import requests
import uuid

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_create_group():
    # Login first (or assume we have a token? No, we need to login)
    # Actually, let's use the local script style with direct DB access if API implies auth complexity, 
    # BUT API testing is better to verify the full stack.
    # I'll create a user if needed or just use credentials if I know them.
    # I'll use direct DB to verify integrity if API fails.
    
    # Let's try to just hit the HEALTH check or list groups if possible.
    # But groups require auth.
    
    # I'll try to import app and run service function directly? 
    # No, keep it separate to avoid import issues messing up the test script itself.
    
    # I will modify to use `requests` but I need a token.
    # If I can't easily get a token, I'll use the service layer test.
    
    pass

# Better approach: Service Layer Test
# This verifies if the code itself runs without crashing due to imports.

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.user import User
from app.schemas.group import GroupCreate
from app.services.group_service import create_group
from app.models.group import Group

# Setup DB - Use absolute path and CORRECT db name
SQLALCHEMY_DATABASE_URL = "sqlite:///c:/Users/krish/Documents/Project/SnapSplit/backend/snapsplit.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def run_test():
    try:
        print("Checking User...")
        user = db.query(User).first()
        if not user:
            print("No user found to create group with.")
            # Create dummy user
            user = User(name="Test User", email=f"test_{uuid.uuid4()}@example.com", password_hash="hash")
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created temp user {user.email}")
            
        print(f"Attempting to create group with user {user.id}")
        group_data = GroupCreate(name=f"Test Group {uuid.uuid4()}")
        
        group = create_group(db, user, group_data)
        print(f"Group created successfully: {group.name} (ID: {group.id})")
        
        # Verify it works
        assert group.id is not None
        assert group.name == group_data.name
        
    except Exception as e:
        print(f"FAILED to create group: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
