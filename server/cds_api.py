from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
import json
import glob
import os

app = FastAPI(title="Personalized Adaptive Hypothermia - CDS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "outputs" / "cds"

def latest_scorecards_path():
    pattern = str(OUTPUT_DIR / "cds_scorecards_*.json")
    files = glob.glob(pattern)
    if not files:
        return None
    # sort by filename timestamp descending
    files.sort(reverse=True)
    return files[0]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/cds/scorecards/latest")
def get_latest_scorecards():
    p = latest_scorecards_path()
    if p is None:
        raise HTTPException(status_code=404, detail="No CDS scorecards found")
    try:
        with open(p, "r") as f:
            data = json.load(f)
        return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read scorecards: {e}")

@app.get("/cds/scorecards/{filename}")
def get_scorecards_by_filename(filename: str):
    target = OUTPUT_DIR / filename
    if not target.exists():
        raise HTTPException(status_code=404, detail="Requested file not found")
    try:
        with open(target, "r") as f:
            data = json.load(f)
        return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read requested file: {e}")

@app.get("/cds/patient/{patient_id}")
def get_patient_scorecard(patient_id: str):
    p = latest_scorecards_path()
    if p is None:
        raise HTTPException(status_code=404, detail="No CDS scorecards found")
    with open(p, "r") as f:
        data = json.load(f)
    items = data.get("items", [])
    matches = [sc for sc in items if str(sc.get("patient_id")) == str(patient_id)]
    if not matches:
        raise HTTPException(status_code=404, detail="Patient not found in latest scorecards")
    return JSONResponse(content=matches[0])

if __name__ == "__main__":
    import uvicorn
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    uvicorn.run(app, host="0.0.0.0", port=8000)
