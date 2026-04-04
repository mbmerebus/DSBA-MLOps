from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

app = FastAPI(title="Gateway")

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

#adresses to services
AUTH_SERVICE = os.getenv("AUTH_SERVICE_URL", "http://auth:8001")
SCORING_SERVICE = os.getenv("SCORING_SERVICE_URL", "http://scoring-api:8000")
HISTORY_SERVICE = os.getenv("HISTORY_SERVICE_URL", "http://history:8003")
security = HTTPBearer() #services communicate through http


async def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{AUTH_SERVICE}/validate",
            headers={"Authorization": f"Bearer {token}"}
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    return resp.json()["username"]


@app.post("/score")
async def score(request: Request, username: str = Depends(require_auth)):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{SCORING_SERVICE}/score", json=body)
    result = resp.json()
    async with httpx.AsyncClient() as client:
        await client.post(f"{HISTORY_SERVICE}/estimates", json={
            "username": username,
            "input": body,
            "result": result
        })
    return result


@app.post("/score/batch")
#NOTE: opens a file search window
async def score_batch(file: UploadFile = File(...), username: str = Depends(require_auth)):
    contents = await file.read()
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            f"{SCORING_SERVICE}/score/batch",
            files={"file": (file.filename, contents, "text/csv")}
        )
    return resp.json()


#User estimates history handling
@app.get("/history")
async def history(username: str = Depends(require_auth)):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{HISTORY_SERVICE}/estimates/{username}")
    return resp.json()


@app.get("/history/{estimate_id}")
async def get_estimate(estimate_id: str, username: str = Depends(require_auth)):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{HISTORY_SERVICE}/estimates/{username}/{estimate_id}")
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Estimate not found.")
    return resp.json()