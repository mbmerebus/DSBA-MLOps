#Per FastAPI Documentation:
import io
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File
from scoring import score, PropertyItem, score_batch

from logger import get_logger
logger = get_logger("scoring")

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
        result = score(req)
        logger.info("Single property scored — predicted: %s", result["predicted_price"])
        return result
    except FileNotFoundError as e: #no prop item submitted
        logger.error("Model not found: %s", e)
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e: #error with property item
        logger.error("Scoring error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
    
# for scoring a full CSV of property items
@app.post("/score/batch")
async def score_batch_endpoint(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        logger.warning("Invalid file format submitted: %s", file.filename)
        raise HTTPException(status_code=400, detail="File format must be CSV")
    contents = await file.read()

    df = pd.read_csv(io.StringIO(contents.decode("utf-8")), low_memory=False)

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns] #seaches for missing columns
    if missing:
        logger.warning("Missing columns in submitted CSV: %s", missing)
        raise HTTPException(status_code=400, detail=f"Missing columns in your submitted CSV: {missing}")
    try:
        results = {"predictions": score_batch(df), "count": len(df)}
        logger.info("Batch scored — %d properties", len(df))
        return results
    except FileNotFoundError as e:
        logger.error("Model not found: %s", e)
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error("Batch scoring error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))