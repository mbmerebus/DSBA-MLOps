from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import redis
import jwt
import bcrypt
import uuid
from datetime import datetime, timedelta
import os
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(title="Auth Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.getenv("JWT_SECRET", "changeme_in_production")
TOKEN_EXPIRY_HOURS = 24

r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, decode_responses=True)
security = HTTPBearer()


class UserCredentials(BaseModel):
    username: str
    password: str


@app.post("/register")
def register(credentials: UserCredentials):
    if r.exists(f"user:{credentials.username}"):
        raise HTTPException(status_code=400, detail="User already exists.")
    hashed = bcrypt.hashpw(credentials.password.encode(), bcrypt.gensalt()).decode()
    r.set(f"user:{credentials.username}", hashed)
    return {"message": "User registered successfully."}


@app.post("/login")
def login(credentials: UserCredentials):
    stored_hash = r.get(f"user:{credentials.username}")
    if not stored_hash or not bcrypt.checkpw(credentials.password.encode(), stored_hash.encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    token = jwt.encode(
        {"sub": credentials.username, "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)},
        SECRET_KEY,
        algorithm="HS256"
    )
    r.setex(f"session:{token}", timedelta(hours=TOKEN_EXPIRY_HOURS), credentials.username)
    return {"access_token": token, "token_type": "bearer"}


@app.post("/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if not r.exists(f"session:{token}"):
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    r.delete(f"session:{token}")
    return {"message": "Logged out successfully."}


@app.get("/validate")
def validate(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    username = r.get(f"session:{token}")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    return {"username": username}
