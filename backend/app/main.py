from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.models import create_tables
from app.auth import router as auth_router        # ✅ Auth routes
from app.location import router as location_router  # ✅ Location routes
from app.images import router as images_router      # ✅ Images service
from app.weather import router as weather_router    # ✅ Weather service
from app.attractions import router as attractions_router  # ✅ Attractions service
from app.favorites import router as favorites_router
from database import get_db_connection

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
app.include_router(favorites_router)

@app.get("/")
def root():
    return {"message": "Backend is running 🚀"}

@app.delete("/drop_table")
def drop_table(table_name: str):
    """
    Drop a table by name. ⚠️ Use carefully.
    Example: /drop_table?table_name=attractions
    """
    # Optional: simple safety check
    allowed_tables = ["users", "favorites", "attractions"]  # only allow known tables
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
