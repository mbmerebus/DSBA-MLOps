import pandas as pd
import pickle
import numpy as np
import os

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
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

    df = pd.read_csv(file_path, usecols=keep, low_memory=False)   # ignore unspecified cols

    numeric_cols = ["surface_reelle_bati", "nombre_pieces_principales", "valeur_fonciere", "nombre_lots", "surface_terrain"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["code_departement"] = df["code_departement"].astype(str)
    df["type_local"] = df["type_local"].astype(str)

    df = df.dropna(subset=numeric_cols)
    df = df[df["code_departement"] != "nan"]
    df = df[df["type_local"] != "nan"]

    return df


def preprocess_data(df):
    """
    Preprocess data: 
    - separate features and target
    - set up the preprocessor for categorical and numerical features
    """

    # NOTE 90th percentile is used instead of 95th because testing showed the 95th let in too much
    # variance from exceptional properties (large estates, luxury assets, especially in Paris-75) without meaningfully
    # improving coverage of typical use cases. Most often than not it decreases the model performance (high MSE)
    df = df[df["valeur_fonciere"] < df["valeur_fonciere"].quantile(0.90)] #remove outliers


    #NOTE : focus on `maison` and `appartement` is made to remove more "exotic" data that may
    # not have enough rows linked to it.
    # not enough rows means the model will not be able to learn from the patter well and
    # will increase MSE score (which we don't want as it is error squared)
    df = df[df["type_local"].isin(["Maison", "Appartement"])]

    # we don't want the model to learn the target.
    X = df.drop("valeur_fonciere", axis=1) #features

    # NOTE log1p is applied to the target because property values follow a strongly right-skewed
    # distribution. The log transformation normalizes it, which improves model performance.
    # predictions must be reversed with expm1 before being returned to the user.
    y = np.log1p(df["valeur_fonciere"]) #target

    numeric_features = [
        "surface_reelle_bati",
        "nombre_pieces_principales",
        "nombre_lots",
        "surface_terrain"
    ]
    
    categorical_features = ["code_departement", "type_local"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), categorical_features),
        ]
    )
    return X, y, preprocessor

#NOTE: The model is currently saved localy and then loaded inside the scoring service container.
# In production, the .pkl model file should be stored in an Object Storage service like S3 or GCS
# That means also modifiying the function so it pushes into this storage instead of local
def save_model(model, path_model: str):
    """Save the trained model to a file in 'scoring/model_storage' """

    dir_name = os.path.dirname(path_model)

    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(path_model, "wb") as f:
        pickle.dump(model, f)