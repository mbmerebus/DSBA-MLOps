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

from logger import get_logger
logger = get_logger("auth")



app = FastAPI(title="Auth Service")


# NOTE CORS POLICY — DEVELOPMENT ONLY
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

SECRET_KEY = os.getenv("JWT_SECRET")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET environment variable is not set.")

# NOTE 24h expiry is a balance between user convenience and session security.
# A shorter window would require frequent re-authentication and longer increases exposure
# if a token is compromised.
# NOTE Expiry time should be modified according to service provider security policy
TOKEN_EXPIRY_HOURS = 24



# NOTE auth has its own redis db file so there can be not data corruption by other services
# it validates the separation of concerns principles of microservice architecture
# NOTE Default points to the redis-auth container name as defined in docker-compose for dev purpose.
# Change this to the actual host if deploying outside of Docker Compose.
r = redis.Redis(host=os.getenv("REDIS_HOST", "redis-auth"), port=6379, decode_responses=True)
security = HTTPBearer()



@app.post("/register")
def register(credentials: UserCredentials):
    if r.exists(f"user:{credentials.username}"):
        raise HTTPException(status_code=400, detail="User already exists.")
    
    # NOTE bcrypt is used because it is a one-way hashing algorithm designed to be slow,
    # it makes brute force attacks computationally expensive even with direct database access.
    hashed = bcrypt.hashpw(credentials.password.encode(), bcrypt.gensalt()).decode()
    r.set(f"user:{credentials.username}", hashed)
    logger.info("New user registered: %s", credentials.username)
    return {"message": "User registered successfully."}


@app.post("/login")
def login(credentials: UserCredentials):
    stored_hash = r.get(f"user:{credentials.username}")
    if not stored_hash or not bcrypt.checkpw(credentials.password.encode(), stored_hash.encode()): #hash decode
        logger.warning("Failed login attempt for: %s", credentials.username)
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    token = jwt.encode(
        {"sub": credentials.username, "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)},
        SECRET_KEY,
        algorithm="HS256"
    )
    r.setex(f"session:{token}", timedelta(hours=TOKEN_EXPIRY_HOURS), credentials.username)
    logger.info("Login successful: %s", credentials.username)
    return {"access_token": token, "token_type": "bearer"}


@app.post("/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if not r.exists(f"session:{token}"):
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    r.delete(f"session:{token}")
    logger.info(f"User logged out — session invalidated. Token {token}")
    return {"message": "Logged out successfully."}

@app.get("/validate")
def validate(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    username = r.get(f"session:{token}")
    if not username:
        logger.warning("Invalid or expired token for: %s", username)
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    logger.info("Valid token for: %s", username)
    return {"username": username}
