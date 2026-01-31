import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing database connection...")
print("=" * 50)

# Try different connection methods
connection_strings = [
    # Method 1: From .env
    os.getenv("DATABASE_URL"),
    # Method 2: Direct with localhost
    "postgresql://snapsplit_user:snapsplit_password@localhost:5432/snapsplit_db",
    # Method 3: Direct with 127.0.0.1
    "postgresql://snapsplit_user:snapsplit_password@127.0.0.1:5432/snapsplit_db",
]

for i, conn_str in enumerate(connection_strings, 1):
    print(f"\n{i}. Testing: {conn_str}")
    try:
        conn = psycopg2.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users;")
        count = cursor.fetchone()[0]
        print(f"   ✅ SUCCESS! Connected. Users in DB: {count}")
        cursor.close()
        conn.close()
        break
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

print("\n" + "=" * 50)
