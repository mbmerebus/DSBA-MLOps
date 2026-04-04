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


# CORS POLICY — DEVELOPMENT ONLY
# Cross-Origin Resource Sharing (CORS) controls which domains are allowed to make
# requests to this API.
# (allow_origins=["*"]) is intentionally permissive to allow the frontend to communicate
#  with the backend during local development.
#
# WARNING: This must not be used in production. In a production environment, this should
# be restricted to the specific domain serving the frontend, and validated by a security
# expert before any deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserCredentials(BaseModel):
    username: str
    password: str

#if env file is found we get the secret key inside, else notify user
SECRET_KEY = os.getenv("JWT_SECRET")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET environment variable is not set.")
TOKEN_EXPIRY_HOURS = 24

#auth has its own redis db file
r = redis.Redis(host=os.getenv("REDIS_HOST", "redis-auth"), port=6379, decode_responses=True)
security = HTTPBearer()




# register and login/logout part
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
