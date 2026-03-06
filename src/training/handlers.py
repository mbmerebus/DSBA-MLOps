import pandas as pd
import pickle
import numpy as np

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.preprocessing import OrdinalEncoder




def load_and_prune_data(file_path: str) -> pd.DataFrame:
    """Load the raw data and prune it to keep only the relevant columns"""
    keep = [
        "surface_reelle_bati",
        "nombre_pieces_principales",
        "code_departement",
        "type_local",
        "valeur_fonciere",
        "nombre_lots",
        "surface_terrain"
    ]

    df = pd.read_csv(file_path, usecols=keep, low_memory=False)   # pandas will ignore missing cols

    numeric_cols = ["surface_reelle_bati", "nombre_pieces_principales", "valeur_fonciere", "nombre_lots", "surface_terrain"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["code_departement"] = df["code_departement"].astype(str)
    df["type_local"] = df["type_local"].astype(str)

    df["price_per_sqm"] = df["valeur_fonciere"] / df["surface_reelle_bati"]

    df = df.dropna(subset=keep)

    return df


def preprocess_data(df):
    """
    Preprocess data: 
    - separate features and target
    - set up the preprocessor for categorical and numerical features
    """

    df = df[df["valeur_fonciere"] < df["valeur_fonciere"].quantile(0.90)] #remove outliers
    #NOTE : focus on maison and appartement is made to remove more "exotic" data
    #and thus improve MSE score
    df = df[df["type_local"].isin(["Maison", "Appartement"])] 
    
    X = df.drop("valeur_fonciere", axis=1) #features
    y = np.log1p(df["valeur_fonciere"]) #target

    #handling for categorical and numerical features
    numeric_features = ["surface_reelle_bati", "nombre_pieces_principales", "nombre_lots", "surface_terrain", "price_per_sqm"]
    categorical_features = ["code_departement", "type_local"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), categorical_features),
        ]
    )
    return X, y, preprocessor


def save_model(model, path_model: str):
    """Save the trained model to a file"""
    import os
    dir_name = os.path.dirname(path_model)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(path_model, "wb") as f:
        pickle.dump(model, f)