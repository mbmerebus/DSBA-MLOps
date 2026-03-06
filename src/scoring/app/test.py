import pickle
import numpy as np
import pandas as pd
from pathlib import Path

model = pickle.load(open("src/scoring/model_storage/model_20260306_215327.pkl", "rb"))

df = pd.DataFrame([{
    "surface_reelle_bati": 65,
    "nombre_pieces_principales": 3,
    "code_departement": "75",
    "type_local": "Appartement",
    "nombre_lots": 1,
    "surface_terrain": 0,
    "price_per_sqm": 65 / 3,
    "code_postal": "75001"
}])

raw = model.predict(df)[0]
print(f"Raw output: {raw}")
print(f"After expm1: {np.expm1(raw)}")

import pandas as pd
df = pd.read_csv("inputs/full.csv", usecols=["code_postal"], low_memory=False)
df = df.dropna(subset=["code_postal"])
df["code_postal"] = df["code_postal"].astype(float).astype(int).astype(str).str.zfill(5)
print(df["code_postal"].value_counts().head(20))