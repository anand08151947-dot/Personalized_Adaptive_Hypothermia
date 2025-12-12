"""
Feature engineering utilities for neonatal therapeutic hypothermia time-series data.

This module provides reusable functions to engineer domain-specific features
from raw vital signs and lab measurements. These utilities mirror the logic
used in Phase2_Data_Preprocessing.ipynb and can be imported in notebooks,
scripts, and inference services.

Functions provided:
- engineer_patient_timeseries_features(df): Per-patient rolling stats & gradients
- add_clinical_labels(df): Derived risk flags and outcomes used for training
- standardize_numeric_features(df, exclude_cols): StandardScaler transformation
- build_feature_matrix(df, feature_cols): Return X matrix aligned to model features

All functions avoid one-letter variable names and are designed for clarity.
"""

from __future__ import annotations

from typing import List, Tuple, Dict
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


def engineer_patient_timeseries_features(df: pd.DataFrame,
                                         patient_id_col: str = "patient_id",
                                         time_col: str = "timestamp") -> pd.DataFrame:
    """
    Create time-series features per patient including temperature gradients,
    heart rate rolling statistics, blood pressure derived metrics, and metabolic indicators.

    Assumes df contains columns:
    - rectal_temp, heart_rate, systolic_bp, diastolic_bp, spo2, ph, lactate

    Returns a new DataFrame with added feature columns.
    """
    df = df.sort_values([patient_id_col, time_col]).copy()

    feature_frames = []
    for patient_id, group in df.groupby(patient_id_col):
        g = group.copy()

        # Temperature gradients: 5-min (1 step), 30-min (6 steps), 1-hour (12 steps)
        g["temp_grad_5m"] = g["rectal_temp"].diff(1)
        g["temp_grad_30m"] = g["rectal_temp"].diff(6)
        g["temp_grad_1h"] = g["rectal_temp"].diff(12)

        # Heart rate rolling window (5 samples ≈ 25 minutes if 5-min sampling)
        window = 5
        g["hr_roll_mean"] = g["heart_rate"].rolling(window, min_periods=1).mean()
        g["hr_roll_std"] = g["heart_rate"].rolling(window, min_periods=1).std().fillna(0.0)
        g["hr_roll_min"] = g["heart_rate"].rolling(window, min_periods=1).min()
        g["hr_roll_max"] = g["heart_rate"].rolling(window, min_periods=1).max()
        # Simple HRV proxy: rolling std
        g["hrv_proxy"] = g["hr_roll_std"]

        # Blood pressure derived metrics
        g["map_mmHg"] = (g["systolic_bp"] + 2.0 * g["diastolic_bp"]) / 3.0
        g["pulse_pressure"] = g["systolic_bp"] - g["diastolic_bp"]

        # Metabolic indicators
        g["lactate_elev"] = g["lactate"] - 2.0
        g["ph_dev_abs"] = (g["ph"] - 7.40).abs()

        feature_frames.append(g)

    out = pd.concat(feature_frames, axis=0).reset_index(drop=True)
    return out


def add_clinical_labels(df: pd.DataFrame,
                        target_temp_low: float = 32.0,
                        target_temp_high: float = 33.5) -> pd.DataFrame:
    """
    Add clinically meaningful labels used by downstream models.

    Labels:
    - temp_undershoot_risk: rectal_temp < target_low - 0.5
    - temp_overshoot_risk: rectal_temp > target_high + 0.5
    - seizure_risk_high: heuristic combining lactate/ph/HRV
    - cardiac_distress_flag: MAP < 35 and pulse_pressure < 20
    - renal_dysfunction_risk: hypotension + hypoxemia + metabolic acidosis
    """
    df = df.copy()

    df["temp_undershoot_risk"] = (df["rectal_temp"] < (target_temp_low - 0.5)).astype(int)
    df["temp_overshoot_risk"] = (df["rectal_temp"] > (target_temp_high + 0.5)).astype(int)

    seizure_cond = (
        (df["lactate"] > 4.0) |
        (df["ph"] < 7.30) |
        (df.get("hrv_proxy", pd.Series(0, index=df.index)) > 25.0)
    )
    df["seizure_risk_high"] = seizure_cond.astype(int)

    df["cardiac_distress_flag"] = ((df["map_mmHg"] < 35.0) & (df["pulse_pressure"] < 20.0)).astype(int)

    renal_cond = (
        (df["map_mmHg"] < 35.0) &
        (df["spo2"] < 92.0) &
        (df["ph"] < 7.30)
    )
    df["renal_dysfunction_risk"] = renal_cond.astype(int)

    return df


def standardize_numeric_features(df: pd.DataFrame,
                                 exclude_cols: List[str] | None = None) -> Tuple[pd.DataFrame, Dict[str, float], Dict[str, float]]:
    """
    Standardize numeric columns (mean=0, std=1) while excluding identifiers
    or categorical columns.

    Returns standardized DataFrame along with mean and std per column for reproducibility.
    """
    if exclude_cols is None:
        exclude_cols = []

    df = df.copy()
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c not in exclude_cols]

    scaler = StandardScaler()
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

    means = {c: float(m) for c, m in zip(numeric_cols, scaler.mean_)}
    stds = {c: float(s) for c, s in zip(numeric_cols, scaler.scale_)}
    return df, means, stds


def build_feature_matrix(df: pd.DataFrame, feature_cols: List[str]) -> np.ndarray:
    """
    Construct the feature matrix X in the exact order expected by trained models.
    Missing columns will raise a KeyError to avoid silent misalignment.
    """
    for col in feature_cols:
        if col not in df.columns:
            raise KeyError(f"Required feature '{col}' not found in DataFrame")
    X = df[feature_cols].to_numpy(dtype=float)
    return X
