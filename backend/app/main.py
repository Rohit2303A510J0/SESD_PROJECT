from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.models import create_tables
from app.auth import router as auth_router   # ✅ Auth routes
from app.location import router as location_router  # ✅ Location routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        create_tables()
        print("✅ Tables checked/created successfully")
    except Exception as e:
        print("⚠️ Could not create tables:", e)
    yield

app = FastAPI(title="Travel Snapshot API", lifespan=lifespan)

# ✅ Include the routers
app.include_router(auth_router)
app.include_router(location_router)  # Added location service

@app.get("/")
def root():
    return {"message": "Backend is running 🚀"}
