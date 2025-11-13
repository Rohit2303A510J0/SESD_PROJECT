from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import app modules
from app.models import create_tables
from app.auth import router as auth_router
from app.location import router as location_router
from app.images import router as images_router
from app.weather import router as weather_router
from app.attractions import router as attractions_router
from app.favorites import router as favorites_router
from app.database import get_db_connection


# -------- Lifespan: Create Tables at Startup --------
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        create_tables()
        print("✅ Tables checked/created successfully")
    except Exception as e:
        print("⚠️ Could not create tables:", e)
    yield


# -------- App Setup --------
app = FastAPI(title="Travel Snapshot API", lifespan=lifespan)


# -------- CORS Middleware --------
# Replace the GitHub Pages URL below with your actual one, e.g.
# "https://yourusername.github.io"
origins = [
    "https://yourusername.github.io",  # your frontend (GitHub Pages)
    "https://your-frontend-domain.netlify.app",  # optional future
    "https://your-app-name.onrender.com",  # self for API testing
    "http://localhost:8000",  # local testing
    "http://127.0.0.1:8000",
    "*"  # ⚠️ can be used temporarily while testing
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # for production, replace with your exact GitHub Pages domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------- Include Routers --------
app.include_router(auth_router)
app.include_router(location_router)
app.include_router(images_router)
app.include_router(weather_router)
app.include_router(attractions_router)
app.include_router(favorites_router)


# -------- Root Route --------
@app.get("/")
def root():
    return {"message": "🌍 Travel Snapshot Backend is running 🚀"}


# -------- Drop Table (Admin Utility) --------
@app.delete("/drop_table")
def drop_table(table_name: str):
    """
    Drop a table by name. ⚠️ Use carefully.
    Example: /drop_table?table_name=attractions
    """
    allowed_tables = ["users", "favorites", "attractions"]
    if table_name not in allowed_tables:
        return {"error": f"Table '{table_name}' is not allowed to be dropped."}

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
        conn.commit()
        return {"message": f"Table '{table_name}' dropped successfully"}
    except Exception as e:
        conn.rollback()
        return {"error": f"Failed to drop table '{table_name}': {str(e)}"}
    finally:
        cur.close()
        conn.close()
