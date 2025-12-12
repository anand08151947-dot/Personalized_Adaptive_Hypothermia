"""
Generate mock live patient data and produce a fresh CDS scorecard file.

Usage (from repo root):
  python server/mock_live_feed.py --patients 5

The resulting JSON is written to outputs/cds/, and the API will serve the newest file.
"""

import argparse
import json
import os
import pickle
from datetime import datetime
from typing import List

import numpy as np
import pandas as pd


# --- Load models and feature lists ---
ROOT = os.path.dirname(os.path.dirname(__file__))
MODELS_DIR = os.path.join(ROOT, "models")


def safe_load(path: str):
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except Exception:
        return None


with open(os.path.join(MODELS_DIR, "temperature_optimization_model.pkl"), "rb") as f:
    temp_model = pickle.load(f)
with open(os.path.join(MODELS_DIR, "temperature_model_features.json"), "r") as f:
    temp_features: List[str] = json.load(f)

seizure_model = safe_load(os.path.join(MODELS_DIR, "seizure_model_logreg.pkl")) or \
                safe_load(os.path.join(MODELS_DIR, "seizure_model_rf.pkl")) or \
                safe_load(os.path.join(MODELS_DIR, "seizure_model_gb.pkl"))
sepsis_model = safe_load(os.path.join(MODELS_DIR, "sepsis_model_rf.pkl"))
cardiac_model = safe_load(os.path.join(MODELS_DIR, "cardiac_model_rf.pkl"))
renal_model = safe_load(os.path.join(MODELS_DIR, "renal_model_rf.pkl"))

with open(os.path.join(MODELS_DIR, "prognosis_model_logreg.pkl"), "rb") as f:
    prognosis_model = pickle.load(f)
with open(os.path.join(MODELS_DIR, "prognosis_feature_columns.json"), "r") as f:
    prognosis_features: List[str] = json.load(f)


# --- Config ---
CDS_CONFIG = {
    "seizure": {"high": 0.70, "medium": 0.40},
    "sepsis": {"high": 0.65, "medium": 0.35},
    "cardiac": {"high": 0.60, "medium": 0.30},
    "renal": {"high": 0.60, "medium": 0.30},
    "prognosis": {"poor_outcome_prob_high": 0.65, "poor_outcome_prob_medium": 0.40},
    "temperature_adjustment_degC": {"max": 1.0, "medium": 0.5},
}

RISK_LABELS = {"high": "HIGH", "medium": "MED", "low": "LOW"}


# --- Helpers ---
def categorize(prob: float, high: float, medium: float) -> str:
    if prob >= high:
        return RISK_LABELS["high"]
    if prob >= medium:
        return RISK_LABELS["medium"]
    return RISK_LABELS["low"]


def compute_temp_adjustment(row: pd.Series) -> float:
    try:
        delta = float(temp_model.predict(row[temp_features].values.reshape(1, -1))[0])
    except Exception:
        delta = 0.0
    return max(0.0, delta)


def compute_event_probability(model, row: pd.Series, cols: List[str]):
    if model is None:
        return None
    try:
        prob = float(model.predict_proba(row[cols].values.reshape(1, -1))[0, 1])
        return prob
    except Exception:
        return None


def build_scorecard(patient_id: str, row: pd.Series) -> dict:
    temp_delta = compute_temp_adjustment(row)

    seizure_prob = compute_event_probability(seizure_model, row, prognosis_features)
    sepsis_prob = compute_event_probability(sepsis_model, row, prognosis_features)
    cardiac_prob = compute_event_probability(cardiac_model, row, prognosis_features)
    renal_prob = compute_event_probability(renal_model, row, prognosis_features)
    prognosis_prob = compute_event_probability(prognosis_model, row, prognosis_features)

    risks = {
        "seizure": categorize(seizure_prob or 0.0, CDS_CONFIG["seizure"]["high"], CDS_CONFIG["seizure"]["medium"]),
        "sepsis": categorize(sepsis_prob or 0.0, CDS_CONFIG["sepsis"]["high"], CDS_CONFIG["sepsis"]["medium"]),
        "cardiac": categorize(cardiac_prob or 0.0, CDS_CONFIG["cardiac"]["high"], CDS_CONFIG["cardiac"]["medium"]),
        "renal": categorize(renal_prob or 0.0, CDS_CONFIG["renal"]["high"], CDS_CONFIG["renal"]["medium"]),
        "prognosis": categorize(prognosis_prob or 0.0, CDS_CONFIG["prognosis"]["poor_outcome_prob_high"], CDS_CONFIG["prognosis"]["poor_outcome_prob_medium"]),
    }

    recommendations = []
    if risks["seizure"] == "HIGH":
        recommendations.append("Initiate continuous EEG; review antiseizure therapy.")
    elif risks["seizure"] == "MED":
        recommendations.append("Increase neuro checks frequency; consider EEG if symptomatic.")

    if risks["sepsis"] == "HIGH":
        recommendations.append("Sepsis bundle: cultures, antibiotics, fluids per protocol.")
    elif risks["sepsis"] == "MED":
        recommendations.append("Trend lactate; monitor vitals and labs closely.")

    if risks["cardiac"] == "HIGH":
        recommendations.append("Cardiac consult; optimize MAP and rhythm management.")
    elif risks["cardiac"] == "MED":
        recommendations.append("Increase telemetry vigilance; review medications impacting QT/MAP.")

    if risks["renal"] == "HIGH":
        recommendations.append("Renal consult; adjust nephrotoxic meds; optimize fluids.")
    elif risks["renal"] == "MED":
        recommendations.append("Monitor urine output and creatinine; adjust dosing.")

    if risks["prognosis"] == "HIGH":
        recommendations.append("Discuss goals of care; consider advanced monitoring/support.")
    elif risks["prognosis"] == "MED":
        recommendations.append("Ensure multidisciplinary review; reassess trajectory in 12h.")

    if temp_delta >= CDS_CONFIG["temperature_adjustment_degC"]["max"]:
        recommendations.append("Strongly consider temperature reduction by ~1.0°C.")
    elif temp_delta >= CDS_CONFIG["temperature_adjustment_degC"]["medium"]:
        recommendations.append("Consider temperature reduction by ~0.5°C.")
    else:
        recommendations.append("Maintain current temperature; continue monitoring.")

    return {
        "patient_id": patient_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "probabilities": {
            "seizure": seizure_prob,
            "sepsis": sepsis_prob,
            "cardiac": cardiac_prob,
            "renal": renal_prob,
            "prognosis_poor_outcome": prognosis_prob,
        },
        "risk_levels": risks,
        "temperature_adjustment_degC": round(temp_delta, 2),
        "recommendations": recommendations,
    }


def run_cds(df: pd.DataFrame, id_col: str = "patient_id"):
    return [build_scorecard(str(row[id_col]), row) for _, row in df.iterrows()]


def save_outputs(scorecards, out_dir=os.path.join(ROOT, "outputs", "cds")):
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_path = os.path.join(out_dir, f"cds_scorecards_{ts}.json")
    with open(out_path, "w") as f:
        json.dump({"generated_at": ts, "items": scorecards}, f, indent=2)
    print(f"Saved {len(scorecards)} scorecards to {out_path}")
    return out_path


def make_mock_dataframe(n_patients: int) -> pd.DataFrame:
    np.random.seed(int(datetime.utcnow().timestamp()) % 1_000_000)
    data = {c: np.random.normal(0, 1, size=n_patients) for c in prognosis_features}
    data["patient_id"] = [f"LIVE-{i+1:03d}" for i in range(n_patients)]

    # Add minimal temp feature columns if they exist
    for col in temp_features:
        if col not in data:
            data[col] = np.random.normal(0, 1, size=n_patients)

    return pd.DataFrame(data)


def main():
    parser = argparse.ArgumentParser(description="Generate mock live CDS scorecards")
    parser.add_argument("--patients", type=int, default=5, help="Number of mock patients")
    args = parser.parse_args()

    df = make_mock_dataframe(args.patients)
    scorecards = run_cds(df)
    save_outputs(scorecards)


if __name__ == "__main__":
    main()