from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routes import auth, friends, groups, expenses, settlements, ai_expenses

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Expense splitting application API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(friends.router, prefix=settings.API_V1_STR)
app.include_router(groups.router, prefix=settings.API_V1_STR)
app.include_router(expenses.router, prefix=settings.API_V1_STR)
app.include_router(settlements.router, prefix=settings.API_V1_STR)
app.include_router(ai_expenses.router, prefix=settings.API_V1_STR)


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
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
