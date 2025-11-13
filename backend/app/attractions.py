from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.database import get_db_connection

router = APIRouter(prefix="/attractions", tags=["Attractions"])

# ---------------- Pydantic models ----------------
class AttractionCreate(BaseModel):
    country: str
    name: str
    lat: float
    lng: float
    description: Optional[str] = None
    image1: Optional[str] = None
    image2: Optional[str] = None
    image3: Optional[str] = None
    image4: Optional[str] = None
    status: Optional[str] = "available"  # default

# ---------------- Endpoints ----------------
@router.post("/")
def add_attraction(attraction: AttractionCreate):
    """
    Add a new attraction to the database.
    Can be used directly from Swagger UI.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO attractions (country, name, lat, lng, description, image1, image2, image3, image4, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (
            attraction.country, attraction.name, attraction.lat, attraction.lng,
            attraction.description, attraction.image1, attraction.image2,
            attraction.image3, attraction.image4, attraction.status
        ))

        new_id = cur.fetchone()[0]
        conn.commit()
        return {"message": "Attraction added successfully", "id": new_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding attraction: {str(e)}")
    finally:
        cur.close()
        conn.close()

@router.get("/{country_name}")
def get_attractions(country_name: str):
    """
    Get all attractions for a given country.
    If no attractions exist, returns work_in_progress message.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT name, lat, lng, description, image1, image2, image3, image4, status FROM attractions WHERE country=%s;", (country_name,))
        rows = cur.fetchall()

        if not rows:
            return {"message": "Work in progress for this country"}

        attractions = []
        for r in rows:
            attractions.append({
                "name": r[0],
                "lat": r[1],
                "lng": r[2],
                "description": r[3],
                "images": [img for img in r[4:8] if img],  # only non-empty images
                "status": r[8]
            })

        return {"country": country_name, "attractions": attractions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching attractions: {str(e)}")
    finally:
        cur.close()
        conn.close()
