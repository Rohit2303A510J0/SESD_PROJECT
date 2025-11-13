from fastapi import APIRouter, HTTPException, Header, status
from datetime import datetime, timedelta
from app.database import get_db_connection
import bcrypt
import jwt
import os

print("✅ Auth router loaded")

router = APIRouter(prefix="/auth", tags=["Auth"])

JWT_SECRET = os.getenv("JWT_SECRET", "secret123")  # fallback for local
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 6


# -------- REGISTER --------
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(email: str, password: str):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE email = %s;", (email,))
    if cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    cur.execute("INSERT INTO users (email, password_hash) VALUES (%s, %s);", (email, hashed_pw))
    conn.commit()
    cur.close()
    conn.close()

    return {"message": "User registered successfully"}


# -------- LOGIN --------
@router.post("/login")
def login_user(email: str, password: str):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, password_hash FROM users WHERE email = %s;", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    user_id, password_hash = user

    if not bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8")):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Generate JWT token
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {"user_id": user_id, "exp": expire.timestamp()}  # store exp as timestamp
    token = jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)

    return {"access_token": token, "token_type": "bearer", "expires_at": expire.isoformat()}


# -------- GET CURRENT USER --------
@router.get("/me")
def get_current_user(authorization: str = Header(default=None, alias="Authorization")):
    """
    Get current user info from Bearer token.
    Works with Render / Swagger UI.
    Header: Authorization: Bearer <access_token>
    """
    if not authorization:
        raise HTTPException(status_code=400, detail="Authorization header missing")

    # Remove "Bearer " prefix and strip extra spaces
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Invalid authorization header format")

    token = authorization.replace("Bearer ", "").strip()

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return {"user_id": user_id}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
