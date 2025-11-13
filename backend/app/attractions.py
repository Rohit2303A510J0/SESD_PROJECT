from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from app.database import get_db_connection
import requests
import os

router = APIRouter(prefix="/attractions", tags=["Attractions"])

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
UNSPLASH_URL = "https://api.unsplash.com/search/photos"


# ---------------- Pydantic model ----------------
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
    status: Optional[str] = "available"


# ---------------- Helper: Fetch Unsplash images ----------------
def fetch_images_from_unsplash(query: str, per_page: int = 4):
    if not UNSPLASH_ACCESS_KEY:
        return []
    try:
        response = requests.get(
            UNSPLASH_URL,
            headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"},
            params={"query": query, "per_page": per_page}
        )
        if response.status_code != 200:
            return []

        data = response.json()
        return [img["urls"]["regular"] for img in data.get("results", [])]
    except Exception:
        return []


# ---------------- Add Attraction ----------------
@router.post("/")
def add_attraction(attraction: AttractionCreate):
    """
    Add a new attraction to the database.
    If no images are provided, fetch from Unsplash automatically.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id FROM attractions WHERE country=%s AND name=%s;", (attraction.country, attraction.name))
        existing = cur.fetchone()
        if existing:
            return JSONResponse({"message": "Attraction already exists", "id": existing[0]})

        # Fetch Unsplash images if not given
        images = [attraction.image1, attraction.image2, attraction.image3, attraction.image4]
        if not any(images):
            fetched_images = fetch_images_from_unsplash(attraction.name)
            images = fetched_images + [None] * (4 - len(fetched_images))

        cur.execute("""
            INSERT INTO attractions (country, name, lat, lng, description, image1, image2, image3, image4, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (
            attraction.country, attraction.name, attraction.lat, attraction.lng,
            attraction.description, images[0], images[1], images[2], images[3], attraction.status
        ))

        new_id = cur.fetchone()[0]
        conn.commit()
        return JSONResponse({"message": "Attraction added successfully", "id": new_id})

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding attraction: {str(e)}")

    finally:
        cur.close()
        conn.close()


# ---------------- Get Attractions by Country ----------------
@router.get("/{country_name}")
def get_attractions(country_name: str):
    """
    Fetch all attractions for a specific country.
    Returns a clear JSON even if no data exists.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT id, name, lat, lng, description, image1, image2, image3, image4, status
            FROM attractions
            WHERE country=%s;
        """, (country_name,))
        rows = cur.fetchall()

        if not rows:
            return JSONResponse({
                "country": country_name,
                "attractions": [],
                "message": "No attractions available yet for this country"
            })

        attractions = []
        for r in rows:
            attractions.append({
                "id": r[0],
                "name": r[1],
                "lat": r[2],
                "lng": r[3],
                "description": r[4],
                "images": [img for img in r[5:9] if img],
                "status": r[9]
            })

        return JSONResponse({"country": country_name, "attractions": attractions})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching attractions: {str(e)}")

    finally:
        cur.close()
        conn.close()


# ---------------- Delete Attraction ----------------
@router.delete("/{attraction_id}")
def delete_attraction(attraction_id: int):
    """
    Delete an attraction by ID.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id FROM attractions WHERE id=%s;", (attraction_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Attraction not found")

        cur.execute("DELETE FROM attractions WHERE id=%s RETURNING id;", (attraction_id,))
        deleted = cur.fetchone()
        conn.commit()

        return JSONResponse({"message": f"Attraction {deleted[0]} deleted successfully", "id": deleted[0]})

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting attraction: {str(e)}")

    finally:
        cur.close()
        conn.close()
