import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Try different connection methods
print("Testing database connection...")

# Method 1: Using environment variable
try:
    db_url = os.getenv("DATABASE_URL")
    print(f"DATABASE_URL from env: {db_url}")
except Exception as e:
    print(f"Error getting DATABASE_URL: {e}")

# Method 2: Direct connection
try:
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        user="snapsplit_user",
        password="snapsplit_password",
        dbname="snapsplit_db"
    )
    print("✓ Direct connection successful!")
    conn.close()
except Exception as e:
    print(f"✗ Direct connection failed: {e}")

# Method 3: Using connection string
try:
    conn = psycopg2.connect("postgresql://snapsplit_user:snapsplit_password@127.0.0.1:5432/snapsplit_db")
    print("✓ Connection string successful!")
    conn.close()
except Exception as e:
    print(f"✗ Connection string failed: {e}")

# Method 4: Without password (trust auth)
try:
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        user="snapsplit_user",
        dbname="snapsplit_db"
    )
    print("✓ Trust auth connection successful!")
    conn.close()
except Exception as e:
    print(f"✗ Trust auth failed: {e}")
