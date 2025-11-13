from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.models import create_tables
from app.auth import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs once when the app starts
    try:
        create_tables()
        print("✅ Tables checked/created successfully")
    except Exception as e:
        print("⚠️ Could not create tables:", e)
    yield
    # (You can add shutdown logic here later if needed)

app = FastAPI(title="Travel Snapshot API", lifespan=lifespan)

# Include authentication routes
app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "Backend is running 🚀"}
