#Code for scoring logic
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from pydantic import BaseModel, Field

#item classes

#Property class to be sent for scoring / with input fields
#per FastAPI documentation, Field is more robust.
class PropertyItem(BaseModel):
    surface_reelle_bati: float = Field(description="Surface area of the building in square meters.")
    nombre_pieces_principales: float = Field(description="Number of main rooms.")
    code_departement: str = Field(description="Department code (e.g. '75').")
    type_local: str = Field(description="Type of property: 'Maison' or 'Appartement'.")
    nombre_lots: float = Field(description="Number of lots.")
    surface_terrain: float = Field(description="Surface area of the land in square meters.")

MODEL_PATH = Path(__file__).resolve().parents[1] / "model_storage"


#functions for score

def load_latest_model():
    """
    Loads the latest trained model.
    """
    models = sorted(MODEL_PATH.glob("model_*.pkl"))

    if not models:
        raise FileNotFoundError(f"No model found at {MODEL_PATH}")
    with open(models[-1], "rb") as f:
        return pickle.load(f)
    
def handle_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handles the formatting of the loaded property data as a DataFrame.
    """
    numeric_cols = ["surface_reelle_bati", "nombre_pieces_principales", "nombre_lots", "surface_terrain"]
    
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["code_departement"] = df["code_departement"].astype(str)
    df["type_local"] = df["type_local"].astype(str)
    df["price_per_sqm"] = df["surface_reelle_bati"] / df["nombre_pieces_principales"]

    return df

def score(property: PropertyItem) -> dict:
    """
    Takes a property item estimates its property value as a dictionnary.
    Uses the lastest model trained.
    """

    model = load_latest_model()
    df = handle_df(pd.DataFrame([property.model_dump()]))
    pred = np.expm1(model.predict(df)[0])
    return {
        "predicted_price": round(float(pred), 2),
        "confidence_interval": { #for debug or feature 
            "low": round(float(pred * 0.80), 2),
            "high": round(float(pred * 1.20), 2),
        }
    }

def score_batch(df: pd.DataFrame) -> list:
    """
    Takes a dataframe of property items and estimates a list of their property values (returns a dictionnary).
    Uses the lastest model trained.
    """
    model = load_latest_model()
    df = handle_df(df)
    preds = np.expm1(model.predict(df))

    # NOTE The price range is computed as +/- 20% around the predicted value.
    # This is a simplification and not a statistically derived confidence interval
    # a proper approach would require quantile regression or bootstrapping
    # The range is consistent with the observed average error
    # on the test set and should be read as a rough indicative bracket not a guarantee.

    list_of_pred = [
        {
            "predicted_price": round(float(p), 2),
            "confidence_interval": {
                "low": round(float(p * 0.80), 2),
                "high": round(float(p * 1.20), 2),
            }
        }
        for p in preds
    ]
    return list_of_pred