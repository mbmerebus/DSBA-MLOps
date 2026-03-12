import redis
import json
import os
import uuid as uuid_lib
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="History Service")
#CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

#History calls its own redis db file
r = redis.Redis(host=os.getenv("REDIS_HOST", "redis-history"), port=6379, decode_responses=True)


class Estimate(BaseModel):
    username: str
    input: dict
    result: dict


@app.post("/estimates")
def save_estimate(estimate: Estimate):
    estimate_id = str(uuid_lib.uuid4())
    entry = {
        "id": estimate_id,
        "input": estimate.input,
        "result": estimate.result,
        "timestamp": datetime.now().isoformat()
    }
    r.set(f"estimate:{estimate.username}:{estimate_id}", json.dumps(entry))
    r.zadd(f"estimates:{estimate.username}", {estimate_id: datetime.now().timestamp()})
    return {"id": estimate_id}


@app.get("/estimates/{username}")
def get_estimates(username: str):
    estimate_ids = r.zrevrange(f"estimates:{username}", 0, 49)
    estimates = []
    for eid in estimate_ids:
        raw = r.get(f"estimate:{username}:{eid}")
        if raw:
            estimates.append(json.loads(raw))
    return {"history": estimates}


@app.get("/estimates/{username}/{estimate_id}")
def get_estimate(username: str, estimate_id: str):
    raw = r.get(f"estimate:{username}:{estimate_id}")
    if not raw:
        raise HTTPException(status_code=404, detail="Estimate not found.")
    return json.loads(raw)