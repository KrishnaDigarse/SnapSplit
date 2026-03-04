from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.core.config import settings
from app.routes import auth, friends, groups, expenses, settlements, ai_expenses, ws
import logging
import sys

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Expense splitting application API"
)

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# SECURITY: Restrict CORS to specific origins instead of wildcard
# In production, only allow your actual frontend domain
allowed_origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",  # Vite dev server
]

# Add frontend URL from environment if configured
if settings.FRONTEND_URL and settings.FRONTEND_URL not in allowed_origins:
    allowed_origins.append(settings.FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.core.middleware import RequestLoggingMiddleware
app.add_middleware(RequestLoggingMiddleware)

app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(friends.router, prefix=settings.API_V1_STR)
app.include_router(groups.router, prefix=settings.API_V1_STR)
app.include_router(expenses.router, prefix=settings.API_V1_STR)
app.include_router(settlements.router, prefix=settings.API_V1_STR)
app.include_router(ai_expenses.router, prefix=settings.API_V1_STR)
app.include_router(ws.router)  # Mounts at /ws


@app.on_event("startup")
async def startup_event():
    """Create database tables on startup"""
    from app.database import engine, Base
    from app.models import (
        User, FriendRequest, Friend, Group, GroupMember,
        Expense, ExpenseItem, Split, Settlement, GroupBalance
    )
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")


@app.get("/")
async def root():
    return {"message": "SnapSplit API is running", "version": settings.VERSION}


@app.get("/health")
async def health_check():
    """
    Comprehensive health check endpoint.
    Verifies database and Redis connectivity.
    """
    health_status = {
        "status": "healthy",
        "version": settings.VERSION,
        "checks": {}
    }
    
    # Check database connectivity
    try:
        from app.database import SessionLocal
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
    
    # Check Redis connectivity
    try:
        import redis
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
    
    return health_status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Force reload for route updates
