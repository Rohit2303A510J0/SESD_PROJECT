from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from app.database import get_db_connection
from app.auth import get_current_user

router = APIRouter(prefix="/favorites", tags=["Favorites"])

# ---------------- Pydantic Models ----------------
class FavoriteCreate(BaseModel):
    attraction_id: int


class FavoriteResponse(BaseModel):
    id: int
    attraction_id: int
    attraction_name: str
    country: str
    image1: str
    created_at: str


# ---------------- Endpoints ----------------
@router.post("/", response_model=FavoriteResponse)
def add_favorite(favorite: FavoriteCreate, current_user: dict = Depends(get_current_user)):
    """
    Add a favorite attraction for the current user.
    """
    user_id = current_user["user_id"]
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Prevent duplicate favorites
        cur.execute("""
            SELECT id FROM favorites WHERE user_id = %s AND attraction_id = %s;
        """, (user_id, favorite.attraction_id))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Attraction already in favorites")

        # Insert new favorite
        cur.execute("""
            INSERT INTO favorites (user_id, attraction_id)
            VALUES (%s, %s)
            RETURNING id, attraction_id, created_at;
        """, (user_id, favorite.attraction_id))
        row = cur.fetchone()
        conn.commit()

        # Fetch attraction details for response
        cur.execute("""
            SELECT name, country, image1
            FROM attractions
            WHERE id = %s;
        """, (favorite.attraction_id,))
        attraction = cur.fetchone()

        if not attraction:
            raise HTTPException(status_code=404, detail="Attraction not found")

        return {
            "id": row[0],
            "attraction_id": row[1],
            "attraction_name": attraction[0],
            "country": attraction[1],
            "image1": attraction[2],
            "created_at": row[2].isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding favorite: {str(e)}")
    finally:
        cur.close()
        conn.close()


@router.get("/", response_model=List[FavoriteResponse])
def get_favorites(current_user: dict = Depends(get_current_user)):
    """
    Get all favorite attractions for the current user.
    """
    user_id = current_user["user_id"]
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT f.id, f.attraction_id, a.name, a.country, a.image1, f.created_at
            FROM favorites f
            JOIN attractions a ON f.attraction_id = a.id
            WHERE f.user_id = %s
            ORDER BY f.created_at DESC;
        """, (user_id,))
        rows = cur.fetchall()

        favorites = [
            {
                "id": r[0],
                "attraction_id": r[1],
                "attraction_name": r[2],
                "country": r[3],
                "image1": r[4],
                "created_at": r[5].isoformat()
            }
            for r in rows
        ]
        return favorites
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching favorites: {str(e)}")
    finally:
        cur.close()
        conn.close()


@router.delete("/{attraction_id}")
def delete_favorite(attraction_id: int, current_user: dict = Depends(get_current_user)):
    """
    Delete a favorite attraction for the current user.
    """
    user_id = current_user["user_id"]
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            DELETE FROM favorites
            WHERE user_id = %s AND attraction_id = %s
            RETURNING id;
        """, (user_id, attraction_id))
        deleted = cur.fetchone()

        if not deleted:
            raise HTTPException(status_code=404, detail="Favorite not found")

        conn.commit()
        return {"message": f"Favorite attraction {attraction_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting favorite: {str(e)}")
    finally:
        cur.close()
        conn.close()
