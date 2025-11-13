from fastapi import APIRouter, Depends, HTTPException, Header
from app.database import get_db_connection
import jwt, os

router = APIRouter(prefix="/favorites", tags=["Favorites"])

JWT_SECRET = os.getenv("JWT_SECRET", "secret123")
ALGORITHM = "HS256"


def get_current_user(authorization: str = Header(...)):
    """Extract user_id from Bearer token"""
    try:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


# ----------- GET Favorites -----------
@router.get("/")
def get_favorites(user_id: int = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT f.id, a.name, a.description, a.image1
            FROM favorites f
            JOIN attractions a ON f.attraction_id = a.id
            WHERE f.user_id = %s;
        """, (user_id,))
        rows = cur.fetchall()
        favorites = []
        for row in rows:
            favorites.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "image": row[3],
            })
        return {"favorites": favorites}
    finally:
        cur.close()
        conn.close()


# ----------- ADD Favorite -----------
@router.post("/{attraction_id}")
def add_favorite(attraction_id: int, user_id: int = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Check if already favorited
        cur.execute(
            "SELECT id FROM favorites WHERE user_id=%s AND attraction_id=%s;",
            (user_id, attraction_id)
        )
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Already in favorites")

        # Insert favorite
        cur.execute(
            "INSERT INTO favorites (user_id, attraction_id) VALUES (%s, %s) RETURNING id;",
            (user_id, attraction_id)
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        return {"message": "Added to favorites", "id": new_id}
    finally:
        cur.close()
        conn.close()


# ----------- DELETE Favorite -----------
@router.delete("/{favorite_id}")
def remove_favorite(favorite_id: int, user_id: int = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "DELETE FROM favorites WHERE id=%s AND user_id=%s RETURNING id;",
            (favorite_id, user_id)
        )
        deleted = cur.fetchone()
        if not deleted:
            raise HTTPException(status_code=404, detail="Favorite not found")
        conn.commit()
        return {"message": "Removed successfully", "id": deleted[0]}
    finally:
        cur.close()
        conn.close()
