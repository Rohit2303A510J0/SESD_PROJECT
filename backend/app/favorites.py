from fastapi import APIRouter, HTTPException, Depends
from app.database import get_db_connection
from app.auth import get_current_user
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/favorites", tags=["Favorites"])


class FavoriteRequest(BaseModel):
    attraction_id: int


class FavoriteResponse(BaseModel):
    id: int
    attraction_id: int
    attraction_name: str
    country: str
    image1: str | None
    created_at: str


# -------- ADD TO FAVORITES --------
@router.post("/", status_code=201)
def add_favorite(req: FavoriteRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Check if already favorited
        cur.execute("SELECT id FROM favorites WHERE user_id = %s AND attraction_id = %s;", (user_id, req.attraction_id))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Already added to favorites")

        cur.execute("INSERT INTO favorites (user_id, attraction_id) VALUES (%s, %s);", (user_id, req.attraction_id))
        conn.commit()
        return {"message": "Attraction added to favorites"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding favorite: {str(e)}")
    finally:
        cur.close()
        conn.close()


# -------- GET ALL FAVORITES --------
@router.get("/", response_model=List[FavoriteResponse])
def get_favorites(current_user: dict = Depends(get_current_user)):
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

        return [
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching favorites: {str(e)}")
    finally:
        cur.close()
        conn.close()


# -------- DELETE FAVORITE --------
@router.delete("/{attraction_id}")
def delete_favorite(attraction_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM favorites WHERE user_id = %s AND attraction_id = %s;", (user_id, attraction_id))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Favorite not found")
        conn.commit()
        return {"message": "Favorite removed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting favorite: {str(e)}")
    finally:
        cur.close()
        conn.close()
