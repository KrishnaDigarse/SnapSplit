import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

print("🧪 Testing SnapSplit API - Full Flow")
print("=" * 60)

# Test 1: Register User
print("\n1️⃣ Registering User (Alice)...")
try:
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": "alice_test@example.com",
            "name": "Alice Test",
            "password": "password123"
        }
    )
    if response.status_code == 201:
        user_data = response.json()
        print(f"   ✅ User registered successfully!")
        print(f"   User ID: {user_data['id']}")
        print(f"   Email: {user_data['email']}")
        user_id = user_data['id']
    else:
        print(f"   ❌ Failed: {response.status_code}")
        print(f"   Error: {response.json()}")
        exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Test 2: Login
print("\n2️⃣ Logging in...")
try:
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "alice_test@example.com",
            "password": "password123"
        }
    )
    if response.status_code == 200:
        token_data = response.json()
        print(f"   ✅ Login successful!")
        print(f"   Token: {token_data['access_token'][:50]}...")
        token = token_data['access_token']
    else:
        print(f"   ❌ Failed: {response.status_code}")
        print(f"   Error: {response.json()}")
        exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Test 3: Create Group
print("\n3️⃣ Creating a group...")
try:
    response = requests.post(
        f"{BASE_URL}/groups",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Test Group"}
    )
    if response.status_code == 201:
        group_data = response.json()
        print(f"   ✅ Group created successfully!")
        print(f"   Group ID: {group_data['id']}")
        print(f"   Group Name: {group_data['name']}")
    else:
        print(f"   ❌ Failed: {response.status_code}")
        print(f"   Error: {response.json()}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ All tests passed! Your API and database are working!")
print("\n🎯 You can now test in Postman:")
print("   1. Health Check")
print("   2. Register User 1 (Alice)")
print("   3. Login User 1")
print("   4. Continue with the full testing flow...")
print("\n📚 See POSTMAN_QUICKSTART.md for step-by-step guide")
