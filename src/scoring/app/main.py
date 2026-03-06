#Per FastAPI Documentation:
import io
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File
from scoring import score, PropertyItem, score_batch

REQUIRED_COLUMNS = [
    "surface_reelle_bati",
    "nombre_pieces_principales",
    "code_departement",
    "type_local",
    "nombre_lots",
    "surface_terrain"
    ]

# Beginning of APP
app = FastAPI(title="Property Value Estimator")

@app.get("/test")
def test_service():
    return {"status": "service is ok"}


@app.post("/score")
async def score_endpoint(req: PropertyItem):
    try:
        return score(req)
    except FileNotFoundError as e: #no prop item submitted
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e: #error with property item
        raise HTTPException(status_code=500, detail=str(e))
    
# for scoring a full CSV of property items
@app.post("/score/batch")
async def score_batch_endpoint(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File format must be CSV")
    contents = await file.read()

    df = pd.read_csv(io.StringIO(contents.decode("utf-8")), low_memory=False)

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns] #seaches for missing columns
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing columns in your submitted CSV: {missing}")
    try:
        return {"predictions": score_batch(df), "count": len(df)}
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
