from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timedelta
from app.database import get_db_connection
from pydantic import BaseModel
import bcrypt
import jwt
import os

router = APIRouter(prefix="/auth", tags=["Auth"])

JWT_SECRET = os.environ["JWT_SECRET"] # fallback for local
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 6


# ---------- MODELS ----------
class RegisterRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenInput(BaseModel):
    access_token: str


# ---------- REGISTER ----------
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: RegisterRequest):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE email = %s;", (user.email,))
    if cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    cur.execute("INSERT INTO users (email, password_hash) VALUES (%s, %s);", (user.email, hashed_pw))
    conn.commit()

    cur.close()
    conn.close()
    return {"message": "User registered successfully ✅"}


# ---------- LOGIN ----------
@router.post("/login")
def login_user(user: LoginRequest):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, password_hash FROM users WHERE email = %s;", (user.email,))
    user_data = cur.fetchone()
    cur.close()
    conn.close()

    if not user_data:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    user_id, password_hash = user_data
    if not bcrypt.checkpw(user.password.encode("utf-8"), password_hash.encode("utf-8")):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Generate JWT token
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {"user_id": user_id, "exp": expire.timestamp()}
    token = jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_at": expire.isoformat(),
    }


# ---------- GET CURRENT USER ----------
@router.post("/me")
def get_current_user(token_input: TokenInput):
    """
    Decode access token and return user info.
    Used in Swagger or internal calls.
    """
    jwt_token = token_input.access_token.strip()

    try:
        payload = jwt.decode(jwt_token, JWT_SECRET, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return {"user_id": user_id}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
