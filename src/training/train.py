#Here is the logic for training the model that will be loaded in the scoring service

import json
import pandas as pd
from datetime import datetime
import handlers
import os
import numpy as np

from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import cross_val_score


def train_model(path_df: str, path_model: str) -> Pipeline:
    """
    This function takes a dataframe, keeps only the relevant columns and trains a model.
    Model used is HistGradient Boosting Regressor from sklearn.
    """
    print(os.path.abspath(path_model))
    #preprocessing
    df = handlers.load_and_prune_data(path_df)
    X,y, preprocessor = handlers.preprocess_data(df)

    #train test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "regressor", 
                HistGradientBoostingRegressor(max_iter=1000, max_depth=8, learning_rate=0.02, random_state=42)
            ),
        ]
    )
    model.fit(X_train, y_train)

    #eval
    y_pred = np.expm1(model.predict(X_test))
    y_test_actual = np.expm1(y_test)
    ##MSE
    mse = mean_squared_error(y_test_actual, y_pred)
    print(f"Mean Squared Error: {mse}")
    ##RMSE
    scores = cross_val_score(model, X, y, cv=5, scoring="neg_mean_squared_error")
    rmse_log = np.sqrt(-scores.mean())
    print(f"Cross Validation RMSE (with log scale): {rmse_log:.4f}")

    #saving
    handlers.save_model(model, path_model)
    return model

