import time
import requests
import os

API_BASE = os.environ.get("CDS_API_BASE", "http://localhost:8000")

def fetch_latest_scorecards():
    url = f"{API_BASE}/cds/scorecards/latest"
    r = requests.get(url, timeout=5)
    r.raise_for_status()
    return r.json()

def print_brief(items, max_items=3):
    print(f"Received {len(items)} scorecards. Showing up to {max_items}:")
    for sc in items[:max_items]:
        pid = sc.get("patient_id")
        risks = sc.get("risk_levels")
        temp_adj = sc.get("temperature_adjustment_degC")
        print(f"- {pid}: seizure={risks.get('seizure')} sepsis={risks.get('sepsis')} cardiac={risks.get('cardiac')} renal={risks.get('renal')} prognosis={risks.get('prognosis')} tempΔ={temp_adj}°C")

if __name__ == "__main__":
    while True:
        try:
            data = fetch_latest_scorecards()
            items = data.get("items", [])
            print_brief(items)
        except Exception as e:
            print("Error fetching CDS data:", e)
        time.sleep(10)
