from app.models.group import Group, GroupType
from app.schemas.group import GroupResponse
import uuid
import datetime

def test_pydantic_validation():
    # Create a dummy Group object (simualting ORM object)
    g = Group(
        id=uuid.uuid4(),
        name="Test Group",
        created_by=uuid.uuid4(),
        type=GroupType.GROUP,
        is_archived=False,
        created_at=datetime.datetime.utcnow()
    )
    
    # Check if we can validate it
    try:
        # Pydantic v2 use model_validate, v1 use from_orm
        try:
            resp = GroupResponse.model_validate(g)
            print("Validation Success (v2)!")
            print(resp)
        except AttributeError:
             resp = GroupResponse.from_orm(g)
             print("Validation Success (v1)!")
             print(resp)
             
    except Exception as e:
        print(f"Validation FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pydantic_validation()
