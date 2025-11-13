from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.models import create_tables
from app.auth import router as auth_router   # ✅ this line loads your auth routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        create_tables()
        print("✅ Tables checked/created successfully")
    except Exception as e:
        print("⚠️ Could not create tables:", e)
    yield

app = FastAPI(title="Travel Snapshot API", lifespan=lifespan)

# ✅ include the authentication router here
app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "Backend is running 🚀"}
