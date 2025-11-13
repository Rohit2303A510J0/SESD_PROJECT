from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from app.database import get_db_connection
import requests
import os

router = APIRouter(prefix="/attractions", tags=["Attractions"])

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
UNSPLASH_URL = "https://api.unsplash.com/search/photos"

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

# ---------------- Helper to fetch images ----------------
def fetch_images_from_unsplash(query: str, per_page: int = 4):
    if not UNSPLASH_ACCESS_KEY:
        return []
    try:
        response = requests.get(
            UNSPLASH_URL,
            headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"},
            params={"query": query, "per_page": per_page}
        )
        data = response.json()
        images = [result["urls"]["regular"] for result in data.get("results", [])]
        return images
    except Exception:
        return []

# ---------------- Endpoints ----------------
@router.post("/")
def add_attraction(attraction: AttractionCreate):
    """
    Add a new attraction to the database.
    If images are not provided, fetch 4 images from Unsplash using the attraction name.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Check if attraction already exists
        cur.execute("SELECT id, image1 FROM attractions WHERE country=%s AND name=%s;", (attraction.country, attraction.name))
        existing = cur.fetchone()
        if existing:
            return {"message": "Attraction already exists", "id": existing[0]}

        # Fetch images if not provided
        images = [attraction.image1, attraction.image2, attraction.image3, attraction.image4]
        if not any(images):
            fetched_images = fetch_images_from_unsplash(attraction.name)
            images = fetched_images + [None]*(4 - len(fetched_images))  # pad to 4

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


# ---------------- DELETE Attraction ----------------
@router.delete("/{attraction_id}")
def delete_attraction(attraction_id: int):
    """
    Delete an attraction by its ID.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id FROM attractions WHERE id=%s;", (attraction_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Attraction not found")

        cur.execute("DELETE FROM attractions WHERE id=%s;", (attraction_id,))
        conn.commit()
        return {"message": f"Attraction {attraction_id} deleted successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting attraction: {str(e)}")
    finally:
        cur.close()
        conn.close()
