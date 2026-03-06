#Per FastAPI Documentation:
from fastapi import FastAPI, Path
from typing import Optional
from .scoring import score, AppartmentItem

# Beginning of APP
app = FastAPI(title="Let's Score your Appartment !")


@app.post("/score")
async def score_endpoint(req: Optional[AppartmentItem] = None):

    #NOTE if no request is sent or valid we fallback on a default appartment for test purpose.
    if req is None:
        req = AppartmentItem(
            adress="Rue des Mariniers",
            roomAmount=2,
            surface=14.8,
        )
    return {"score": score(req)}