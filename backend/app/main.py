from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.models import create_tables
from app.auth import router as auth_router        # ✅ Auth routes
from app.location import router as location_router  # ✅ Location routes
from app.images import router as images_router      # ✅ Images service
from app.weather import router as weather_router    # ✅ Weather service
from app.attractions import router as attractions_router  # ✅ Attractions service

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
app.include_router(location_router)
app.include_router(images_router)
app.include_router(weather_router)
app.include_router(attractions_router)  # Add attractions routes

@app.get("/")
def root():
    return {"message": "Backend is running 🚀"}
