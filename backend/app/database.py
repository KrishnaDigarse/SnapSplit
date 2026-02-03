import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# TEMPORARY: Switched to PostgreSQL for Load Testing
# To switch back to SQLite, restore from backup or git
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://snapsplit_user:password@localhost:5432/snapsplit_db")

# Connection Pooling Configuration
# pool_size=10: Maintain 10 open connections to be reused (reduces handshake overhead)
# max_overflow=20: Allow up to 20 additional connections during spikes
# pool_timeout=30: Wait 30s for a connection before giving up
# pool_recycle=1800: Recycle connections every 30 mins to prevent stale connections
# pool_pre_ping=True: Check connection health before handing it out
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
