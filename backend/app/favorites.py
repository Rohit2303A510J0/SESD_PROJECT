from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from app.database import get_db_connection
from app.auth import get_current_user  # We’ll reuse your /auth/me logic

router = APIRouter(prefix="/favorites", tags=["Favorites"])

# ---------------- Pydantic Models ----------------
class FavoriteCreate(BaseModel):
    place_name: str
    place_type: Optional[str] = None  # e.g., "attraction", "city"
    country_code: Optional[str] = None
    image_url: Optional[str] = None
    map_url: Optional[str] = None

class FavoriteResponse(BaseModel):
    id: int
    place_name: str
    place_type: Optional[str]
    country_code: Optional[str]
    image_url: Optional[str]
    map_url: Optional[str]

# ---------------- Endpoints ----------------
@router.post("/", response_model=FavoriteResponse)
def add_favorite(favorite: FavoriteCreate, current_user: dict = Depends(get_current_user)):
    """
    Add a favorite place for the current user.
    """
    user_id = current_user["user_id"]
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO favorites (user_id, place_name, place_type, country_code, image_url, map_url)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, place_name, place_type, country_code, image_url, map_url;
        """, (
            user_id,
            favorite.place_name,
            favorite.place_type,
            favorite.country_code,
            favorite.image_url,
            favorite.map_url
        ))

        row = cur.fetchone()
        conn.commit()

        return {
            "id": row[0],
            "place_name": row[1],
            "place_type": row[2],
            "country_code": row[3],
            "image_url": row[4],
            "map_url": row[5]
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding favorite: {str(e)}")
    finally:
        cur.close()
        conn.close()

@router.get("/", response_model=List[FavoriteResponse])
def get_favorites(current_user: dict = Depends(get_current_user)):
    """
    Get all favorites for the current user.
    """
    user_id = current_user["user_id"]
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT id, place_name, place_type, country_code, image_url, map_url
            FROM favorites
            WHERE user_id=%s;
        """, (user_id,))
        rows = cur.fetchall()

        favorites = []
        for r in rows:
            favorites.append({
                "id": r[0],
                "place_name": r[1],
                "place_type": r[2],
                "country_code": r[3],
                "image_url": r[4],
                "map_url": r[5]
            })
        return favorites
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching favorites: {str(e)}")
    finally:
        cur.close()
        conn.close()

@router.delete("/{favorite_id}")
def delete_favorite(favorite_id: int, current_user: dict = Depends(get_current_user)):
    """
    Delete a favorite place by its ID for the current user.
    """
    user_id = current_user["user_id"]
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id FROM favorites WHERE id=%s AND user_id=%s;", (favorite_id, user_id))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Favorite not found")

        cur.execute("DELETE FROM favorites WHERE id=%s AND user_id=%s;", (favorite_id, user_id))
        conn.commit()
        return {"message": f"Favorite {favorite_id} deleted successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting favorite: {str(e)}")
    finally:
        cur.close()
        conn.close()
