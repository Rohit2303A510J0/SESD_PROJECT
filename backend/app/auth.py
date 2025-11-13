from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi import Header
from datetime import datetime, timedelta
from app.database import get_db_connection
import bcrypt
import jwt
import os

print("✅ Auth router loaded")


router = APIRouter(prefix="/auth", tags=["Auth"])

JWT_SECRET = os.getenv("JWT_SECRET", "secret123")  # fallback for local
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# -------- REGISTER --------
@router.post("/register")
def register_user(email: str, password: str):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE email = %s;", (email,))
    if cur.fetchone():
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

    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    user_id, password_hash = user

    if not bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8")):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = jwt.encode(
        {"user_id": user_id, "exp": datetime.utcnow() + timedelta(hours=6)},
        JWT_SECRET,
        algorithm="HS256"
    )

    cur.close()
    conn.close()

    return {"access_token": token, "token_type": "bearer"}

# -------- GET CURRENT USER --------
@router.get("/me")
def get_current_user(authorization: str = Header(None)):
    """
    Returns current user info from Bearer token.
    Example header:
    Authorization: Bearer <token>
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.split(" ")[1]

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return {"user_id": payload["user_id"]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
