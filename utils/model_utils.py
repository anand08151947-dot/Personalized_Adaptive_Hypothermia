"""
Model training and evaluation utilities for the Personalized Adaptive Hypothermia project.

This module consolidates common ML tasks used in Phase 3 and future phases:
- split_train_test: deterministic train/test split
- train_temperature_models: train RF, GradientBoosting, MLP regressors
- evaluate_regression: RMSE, MAE, R2 metrics
- save_models: persist models and metadata to disk
- load_model_and_features: helper to load model and feature list for inference

Designed for clarity and minimal external dependencies.
"""

from __future__ import annotations

from typing import Dict, Tuple, List
import os
import json
import pickle
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor


def split_train_test(X: np.ndarray, y: np.ndarray, test_size: float = 0.2, random_state: int = 42):
    return train_test_split(X, y, test_size=test_size, random_state=random_state)


def train_temperature_models(X_train: np.ndarray, y_train: np.ndarray, random_state: int = 42) -> Dict[str, object]:
    """
    Train three competing regression models for temperature prediction.
    Returns a dict of model_name -> fitted estimator.
    """
    models = {}

    rf = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=random_state)
    rf.fit(X_train, y_train)
    models["random_forest"] = rf

    gb = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=random_state)
    gb.fit(X_train, y_train)
    models["gradient_boosting"] = gb

    mlp = MLPRegressor(hidden_layer_sizes=(128, 64, 32), learning_rate_init=0.001, max_iter=500, early_stopping=True, random_state=random_state)
    mlp.fit(X_train, y_train)
    models["mlp"] = mlp

    return models


def evaluate_regression(model, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
    """
    Compute RMSE, MAE, and R2 for a regression model.
    """
    preds = model.predict(X_test)
    rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
    mae = float(mean_absolute_error(y_test, preds))
    r2 = float(r2_score(y_test, preds))
    return {"rmse": rmse, "mae": mae, "r2": r2}


def select_best_model(metrics: Dict[str, Dict[str, float]], by: str = "rmse") -> str:
    """
    Select best model key by a metric (default: lowest RMSE).
    """
    if by not in {"rmse", "mae", "r2"}:
        raise ValueError("Selection metric must be one of {'rmse','mae','r2'}")

    if by == "r2":
        return max(metrics.items(), key=lambda kv: kv[1]["r2"])[0]
    else:
        return min(metrics.items(), key=lambda kv: kv[1][by])[0]


def save_models(models: Dict[str, object], feature_cols: List[str], results: Dict[str, Dict[str, float]], output_dir: str = "models") -> None:
    """
    Persist all models and metadata:
    - models/temperature_model_<name>.pkl for each variant
    - models/temperature_optimization_model.pkl for the selected best
    - models/temperature_model_results.json with metrics
    - models/temperature_model_features.json with feature list order
    """
    os.makedirs(output_dir, exist_ok=True)

    # Save individual variants
    for name, model in models.items():
        with open(os.path.join(output_dir, f"temperature_model_{name}.pkl"), "wb") as f:
            pickle.dump(model, f)

    # Decide best by RMSE if present in results
    best_name = select_best_model(results, by="rmse") if results else "gradient_boosting"

    # Save best as optimization model
    with open(os.path.join(output_dir, "temperature_optimization_model.pkl"), "wb") as f:
        pickle.dump(models[best_name], f)

    # Save metrics and feature columns
    with open(os.path.join(output_dir, "temperature_model_results.json"), "w") as f:
        json.dump(results, f, indent=2)

    with open(os.path.join(output_dir, "temperature_model_features.json"), "w") as f:
        json.dump(feature_cols, f, indent=2)


def load_model_and_features(model_path: str = "models/temperature_optimization_model.pkl",
                            feature_path: str = "models/temperature_model_features.json") -> Tuple[object, List[str]]:
    """
    Helper to load model + feature ordering for inference services.
    """
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    with open(feature_path, "r") as f:
        feature_cols = json.load(f)
    return model, feature_cols
