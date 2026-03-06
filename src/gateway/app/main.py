from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Gateway")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

AUTH_SERVICE = os.getenv("AUTH_SERVICE_URL", "http://auth:8001")
SCORING_SERVICE = os.getenv("SCORING_SERVICE_URL", "http://scoring-api:8000")
security = HTTPBearer()





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
    _save_to_history(username, result, body)
    return result


@app.post("/score/batch")
async def score_batch(file: UploadFile = File(...), username: str = Depends(require_auth)):
    contents = await file.read()
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{SCORING_SERVICE}/score/batch",
            files={"file": (file.filename, contents, "text/csv")}
        )
    return resp.json()


@app.get("/history")
async def history(username: str = Depends(require_auth)):
    import redis
    import json
    r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, decode_responses=True)
    entries = r.lrange(f"history:{username}", 0, 49)
    return {"history": [json.loads(e) for e in entries]}


def _save_to_history(username: str, result: dict, input_data: dict):
    import redis
    import json
    from datetime import datetime
    r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, decode_responses=True)
    entry = json.dumps({"input": input_data, "result": result, "timestamp": datetime.utcnow().isoformat()})
    r.lpush(f"history:{username}", entry)
    r.ltrim(f"history:{username}", 0, 49)
