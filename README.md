# Personalized Adaptive Hypothermia (PAH)

**An intelligent clinical decision support system for neonatal therapeutic hypothermia treatment.**

This project implements a complete ML pipeline to transform therapeutic hypothermia devices from static cooling systems into personalized, predictive intelligence platforms. It includes data generation, preprocessing, model training, clinical decision support (CDS) inference, and a production-ready API with interactive React dashboard.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ 
- Node.js 16+ (for React dashboard)
- Git
- ~500MB disk space (for data, models, outputs)

### Setup (5 Minutes)

```bash
# Clone repository
git clone <your-repo-url>.git
cd Personalized_Adaptive_Hypothermia

# Create Python environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # Windows
# or: source .venv/bin/activate       # macOS/Linux

# Install Python dependencies
pip install -r requirements.txt
```

### Run the Full System

**Terminal 1 - Execute ML Pipeline:**
```bash
# This generates all models and CDS scorecards
cd notebooks
jupyter nbconvert --to notebook --execute Phase1_Data_Generation.ipynb
jupyter nbconvert --to notebook --execute Phase2_Data_Preprocessing.ipynb
jupyter nbconvert --to notebook --execute Phase3_Temperature_Optimization_Model.ipynb
jupyter nbconvert --to notebook --execute Phase4_Seizure_and_Complication_Prediction.ipynb
jupyter nbconvert --to notebook --execute Phase5_Prognostic_Assessment_Model.ipynb
jupyter nbconvert --to notebook --execute Phase6_Ensemble_and_Clinical_Decision_Support.ipynb
```

**Terminal 2 - Start CDS API Server:**
```bash
python server/cds_api.py
# API available at http://localhost:8000
# Health check: http://localhost:8000/health
```

**Terminal 3 - Start React Dashboard:**
```bash
cd dashboard
npm install                    # First time only
npm run dev
# Dashboard available at http://localhost:3000
```

**Terminal 4 (Optional) - Bedside Polling Client:**
```bash
python bedside/cds_client.py
# Polls API every 2 seconds and displays patient summaries
```

**Generate Mock Live Data (Optional):**
```bash
# Generate and display 5 random patient scorecards
python server/mock_live_feed.py --patients 5
```

## 📁 Project Structure

```
Personalized_Adaptive_Hypothermia/
├── notebooks/                                    # ML Pipeline (6 Phases)
│   ├── Phase1_Data_Generation.ipynb            # Synthetic 50 patients, 43,200 records
│   ├── Phase2_Data_Preprocessing.ipynb         # Normalization, 51 features
│   ├── Phase3_Temperature_Optimization_Model.ipynb    # RandomForest, R²=0.9282
│   ├── Phase4_Seizure_and_Complication_Prediction.ipynb  # 4 classifiers
│   ├── Phase5_Prognostic_Assessment_Model.ipynb       # LogisticRegression, AUC=1.0
│   └── Phase6_Ensemble_and_Clinical_Decision_Support.ipynb # CDS inference
│
├── utils/                                        # Shared utilities
│   ├── feature_engineering.py                  # Feature transformations
│   ├── models.py                               # Model training wrappers
│   └── data_generation.py                      # Synthetic data creation
│
├── server/                                       # Backend (FastAPI)
│   ├── cds_api.py                              # RESTful API server (port 8000)
│   └── mock_live_feed.py                       # Mock patient generator
│
├── dashboard/                                    # Frontend (React + TypeScript)
│   ├── src/
│   │   ├── App.tsx                             # Main dashboard component
│   │   ├── types.ts                            # TypeScript interfaces
│   │   ├── api.ts                              # API client
│   │   ├── index.css                           # Global styles
│   │   └── components/
│   │       ├── PatientCard.tsx                 # Patient summary cards
│   │       ├── RiskChart.tsx                   # Risk visualization
│   │       └── RiskDetailModal.tsx             # Clinical detail modal
│   ├── vite.config.ts                          # Vite configuration
│   ├── tsconfig.json                           # TypeScript config
│   ├── package.json                            # npm dependencies
│   └── index.html                              # HTML entry point
│
├── bedside/                                      # Legacy CLI Client
│   └── cds_client.py                           # Polling client example
│
├── data/                                         # Generated datasets
│   ├── complete_mocked_dataset.csv             # Raw synthetic data
│   ├── preprocessed_normalized_dataset.csv     # Preprocessed features
│   └── *.png                                   # Visualizations
│
├── models/                                       # Trained ML models
│   ├── temperature_optimization_model.pkl
│   ├── seizure_model_rf.pkl
│   ├── sepsis_model_rf.pkl
│   ├── cardiac_model_rf.pkl
│   ├── renal_model_rf.pkl
│   └── prognosis_model_logreg.pkl
│
├── outputs/                                      # CDS outputs
│   └── cds/
│       └── cds_scorecards_*.json               # Timestamped scorecard batches
│
├── requirements.txt                             # Python dependencies (pinned versions)
├── .gitignore                                   # Git exclusions
├── README.md                                    # This file
└── LICENSE                                      # MIT License
```

## 🏗️ System Architecture

### Data Flow
```
Synthetic Patients → Preprocessing → ML Models → CDS Inference → API → Dashboard/Client
     (Phase 1)          (Phase 2)    (Phases 3-5)   (Phase 6)
```

### 6-Phase ML Pipeline

| Phase | Component | Input | Output | Key Metric |
|-------|-----------|-------|--------|-----------|
| 1 | Data Generation | Neonatal HIE parameters | 50 patients × 72h × 20 vital records | 43,200 rows |
| 2 | Preprocessing | Raw vitals | StandardScaler normalized | 51 features |
| 3 | Temp Optimization | Vital signs | Optimal temperature adjustment (°C) | R² = 0.9282 |
| 4 | Complication Risk | Patient state | 4 risk scores (seizure, sepsis, cardiac, renal) | AUC > 0.92 |
| 5 | Prognosis | All features | Long-term outcome probability | AUC = 1.0 |
| 6 | CDS Integration | All predictions | Clinical recommendations + JSON | JSON saved |

### Backend Architecture (FastAPI)

**API Server (`server/cds_api.py`)**
- Port: `0.0.0.0:8000` (all interfaces)
- Framework: FastAPI 0.115.0 + Uvicorn 0.30.0
- CORS: Enabled for all origins (configure for production)
- Auto-discovery: Automatically finds latest scorecard file

**Endpoints:**
```
GET  /health                           → {"status": "ok"}
GET  /cds/scorecards/latest           → Latest batch of scorecards (JSON array)
GET  /cds/scorecards/{filename}       → Specific scorecard file by name
GET  /cds/patient/{patient_id}        → Single patient scorecard
```

### Frontend Architecture (React + TypeScript)

**Dashboard (`dashboard/src/App.tsx`)**
- Port: `localhost:3000` (development)
- Framework: React 18.2.0 + TypeScript 5.3.3 + Vite 5.0.8
- API Proxy: Vite proxies `/api/*` to `http://localhost:8000`
- Refresh: Auto-polls API every 10 seconds
- Interactive: Click risk badges to view clinical details

**Key Components:**
- `PatientCard.tsx`: Patient summary with 5 clickable risk badges
- `RiskChart.tsx`: Bar chart showing risk probabilities
- `RiskDetailModal.tsx`: Deep-dive clinical information, evidence-based recommendations

## 🤖 ML Models Reference

### Phase 3: Temperature Optimization (RandomForest)
- **Purpose**: Predict optimal temperature adjustment relative to standard 33.5°C
- **Input Features**: 51 normalized vital signs (heart rate, oxygen, lactate, etc.)
- **Output**: Temperature delta (°C), typical range -1.0°C to +1.0°C
- **Performance**: R² = 0.9282, RMSE = 0.27°C
- **Use Case**: Personalized cooling intensity per patient physiology

### Phase 4: Complication Risk (4 × RandomForest)
- **Purpose**: Estimate probability of 4 major complications during treatment
- **Outputs**: 
  - Seizure probability (0.0 - 1.0)
  - Sepsis probability (0.0 - 1.0)
  - Cardiac complications (0.0 - 1.0)
  - Renal complications (0.0 - 1.0)
- **Performance**: AUC > 0.92 each, synthetic balanced dataset
- **Threshold Defaults**: HIGH ≥ 0.70, MEDIUM ≥ 0.40, LOW < 0.40

### Phase 5: Prognosis Assessment (LogisticRegression)
- **Purpose**: Predict poor neurodevelopmental outcome (death or severe disability)
- **Input Features**: All 51 features (including all risk scores)
- **Output**: Prognosis probability (0.0 - 1.0)
- **Performance**: AUC = 1.0, F1 = 1.0 (on synthetic data)
- **Clinical Weight**: Heavily influences treatment recommendations

## ⚙️ CDS Configuration

### Risk Thresholds
Located in `notebooks/Phase6_Ensemble_and_Clinical_Decision_Support.ipynb` (`CDS_CONFIG` dict):

```python
CDS_CONFIG = {
    'seizure': {'high': 0.70, 'medium': 0.40},
    'sepsis': {'high': 0.70, 'medium': 0.40},
    'cardiac': {'high': 0.70, 'medium': 0.40},
    'renal': {'high': 0.70, 'medium': 0.40},
    'prognosis': {'high': 0.70, 'medium': 0.40},
}
```

### CDS Output Format
Each scorecard batch generates a JSON file with structure:
```json
{
  "generated_at": "2024-12-12T19:07:51Z",
  "patient_id": "DEMO-001",
  "temperature_adjustment": 0.15,
  "risks": {
    "seizure": {"probability": 0.25, "level": "LOW"},
    "sepsis": {"probability": 0.30, "level": "LOW"},
    "cardiac": {"probability": 0.20, "level": "LOW"},
    "renal": {"probability": 0.18, "level": "LOW"},
    "prognosis": {"probability": 0.15, "level": "LOW"}
  },
  "primary_recommendation": "Continue standard hypothermia protocol...",
  "context_aware_actions": ["Monitor vitals every 2 hours", "Maintain temp at 33.5°C", ...]
}
```

## 🛠️ Development Guide

### Adding a New Complication Type

1. **Update Phase 4 Notebook** (`Phase4_...ipynb`):
   - Add new feature engineering logic
   - Train new RandomForest classifier
   - Save as `models/newrisk_model_rf.pkl`

2. **Update Phase 6 Notebook** (`Phase6_...ipynb`):
   - Add `newrisk` to `CDS_CONFIG` thresholds
   - Add recommendation rules in `generate_context_aware_actions()`
   - Regenerate scorecards

3. **Update Frontend** (`dashboard/src/`):
   - Add to `Probabilities` interface in `types.ts`
   - Add to `RISK_DETAILS` in `RiskDetailModal.tsx`
   - Add new RiskBadge in `PatientCard.tsx`

### Customizing Thresholds

1. Open `Phase6_Ensemble_and_Clinical_Decision_Support.ipynb`
2. Modify `CDS_CONFIG` dictionary values
3. Re-run Phase 6 notebook
4. Dashboard auto-refreshes (no redeploy needed)

### Deploying to Production

1. **Replace mock data** with real patient database connection in Phase 1
2. **Update CORS** in `server/cds_api.py`: Replace `allow_origins=["*"]` with specific domains
3. **Use environment variables** for API credentials (see `.env.example`)
4. **Deploy backend**: Use production ASGI server (Gunicorn + Uvicorn)
5. **Build frontend**: `npm run build` → deploys `dist/` folder
6. **Add HTTPS**: Use reverse proxy (nginx) with SSL certificates

### Performance Characteristics

- **Data Generation**: ~2 minutes for 50 patients (Phase 1)
- **Preprocessing**: ~1 minute for feature normalization (Phase 2)
- **Model Training**: ~3 minutes total for all 5 models (Phases 3-5)
- **CDS Inference**: ~500ms per batch of 5 patients (Phase 6)
- **API Response Time**: <100ms per request (cached models)
- **Dashboard Refresh**: 10s polling interval (adjustable)

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'sklearn'"
**Solution**: Ensure Python environment is activated and requirements installed:
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Issue: "Connection refused" when accessing API from dashboard
**Solution**: Verify API is running and check Vite proxy configuration:
```bash
# Terminal 1: Confirm API running
curl http://localhost:8000/health

# Terminal 2: Check Vite dev server logs for proxy errors
# Should show: "GET /api/cds/scorecards/latest → http://localhost:8000/cds/scorecards/latest"
```

### Issue: scikit-learn version warnings (InconsistentVersionWarning)
**Status**: Benign deprecation warnings, system continues working
**Solution**: Update `requirements.txt` to match training environment:
```bash
pip freeze | grep scikit-learn
# Update requirements.txt with exact version, then: pip install -r requirements.txt --force-reinstall
```

### Issue: "No CDS scorecard files found"
**Solution**: Run Phase 6 notebook first:
```bash
jupyter nbconvert --to notebook --execute notebooks/Phase6_Ensemble_and_Clinical_Decision_Support.ipynb
```

### Issue: Dashboard shows "Failed to fetch scorecards"
**Solution**: Check API logs and network tab in browser DevTools. Verify:
- API responding: `curl http://localhost:8000/health`
- Correct base URL in `dashboard/src/api.ts`
- CORS headers present in API response

## 👥 Contributing

### For Contributors

1. **Fork** the repository
2. **Create feature branch**: `git checkout -b feature/your-feature`
3. **Make changes** following code style in existing files
4. **Run tests**: Execute relevant notebook phases to validate
5. **Commit clearly**: `git commit -m "Add feature: description"`
6. **Push branch**: `git push origin feature/your-feature`
7. **Open Pull Request** with clear description

### Code Standards

- **Notebooks**: Keep cells focused and well-commented, include visualizations
- **Python**: Use type hints, follow PEP 8, add docstrings
- **React**: Use TypeScript, prefer functional components with hooks, add JSDoc comments
- **Commits**: Small, focused changes with clear messages
- **Documentation**: Update README.md and docstrings for new features

### Areas for Contribution

- [ ] Real patient data integration (Phase 1 enhancement)
- [ ] Additional complication types (Phase 4 extension)
- [ ] Deep learning models (LSTM/CNN alternatives to RandomForest)
- [ ] Mobile app version (React Native)
- [ ] Docker containerization
- [ ] Deployment guides (AWS/Azure/GCP)
- [ ] Performance optimizations

## 📊 System Status

- **Latest Test**: All 6 phases executed successfully
- **API Health**: ✅ Responding on port 8000
- **Dashboard**: ✅ Running on port 3000 with auto-refresh
- **Models**: ✅ All 6 models loaded and operational
- **Mock Data**: ✅ Generator tested with 5-25 patients
- **CDS Inference**: ✅ JSON outputs generated
- **Documentation**: ✅ Complete for contributor onboarding

## 📜 License

MIT License. See `LICENSE` for full text.

**Use Case**: Research, education, and prototyping only. Not approved for clinical use without regulatory validation.

## 🔗 Contact & Citation

**Project**: Personalized Adaptive Hypothermia (PAH) Clinical Decision Support System

**Citation**:
```bibtex
@software{PAH2024,
  title={Personalized Adaptive Hypothermia: ML-Driven Clinical Decision Support},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/Personalized_Adaptive_Hypothermia}
}
```

**Questions?** Open an issue or contact the repository maintainer.# AI-Based Personalized Adaptive Hypothermia System
## ML Model Development for Neonatal HIE Treatment

This project implements machine learning and deep learning models for an intelligent therapeutic hypothermia device to treat neonatal hypoxic-ischemic encephalopathy (HIE).

## Project Overview

The system transforms traditional cooling devices from purely controlled systems into intelligent, predictive, and personalized therapeutic systems through AI/ML integration.

### Key Features

1. **Personalized Temperature Tuning** - Optimal temperature recommendations based on individual physiology
2. **Real-Time Monitoring & Prediction** - Early detection of seizures and brain activity patterns
3. **Complication Prediction** - Risk assessment for sepsis, cardiac, and renal complications
4. **Prognostic Assessment** - Long-term neurodevelopmental outcome prediction
5. **Clinical Decision Support** - Real-time recommendations for clinicians

## Project Structure

```
Personalized_Adaptive_Hypothermia/
├── data/                          # Generated datasets and analysis
│   ├── complete_mocked_dataset.csv
│   ├── preprocessed_normalized_dataset.csv
│   ├── patient_metadata.csv
│   ├── feature_engineering_metadata.csv
│   ├── temperature_profiles.png
│   ├── vital_signs_patterns.png
│   ├── correlation_matrix.png
│   ├── temperature_model_performance.png
│   └── temperature_model_feature_importance.png
│
├── models/                        # Trained ML models and metadata
│   ├── temperature_optimization_model.pkl
│   ├── temperature_model_*.pkl    # Individual model variants
│   ├── temperature_model_results.json
│   └── temperature_model_features.json
│
├── notebooks/                     # Jupyter notebooks for each phase
│   ├── Phase1_Data_Generation.ipynb
│   ├── Phase2_Data_Preprocessing.ipynb
│   ├── Phase3_Temperature_Optimization_Model.ipynb
│   ├── Phase4_Seizure_and_Complication_Prediction.ipynb
│   ├── Phase5_Prognostic_Assessment_Model.ipynb
│   └── Phase6_Ensemble_and_Clinical_Decision_Support.ipynb
│
├── utils/                         # Utility modules
│   ├── data_generator.py         # Mocked physiological data generator
│   ├── feature_engineering.py    # Feature engineering utilities
│   └── model_utils.py            # Model training and evaluation utilities
│
└── README.md                      # This file
```

## Development Phases

### Phase 1: Mocked Data Generation ✓
**Notebook:** `Phase1_Data_Generation.ipynb`

Generates realistic synthetic physiological data for 50 infants undergoing therapeutic hypothermia over 72 hours.

**Key Outputs:**
- 50 patient profiles with varying HIE severity (mild, moderate, severe)
- Vital signs: rectal temperature, heart rate, blood pressure, SpO2
- Blood gas analysis: pH, pCO2, pO2, lactate
- Sampling interval: 5 minutes
- Dataset: 8,640 total records (172.8 hours per patient)

**Features:**
- Baseline parameters: birth weight, gestational age, seizure risk
- Individualized cooling protocols
- Realistic physiological variations and measurements

### Phase 2: Data Preprocessing & Feature Engineering ✓
**Notebook:** `Phase2_Data_Preprocessing.ipynb`

Transforms raw data into ML-ready features with clinical relevance.

**Key Transformations:**
1. Data validation and missing value handling
2. Time-series feature engineering:
   - Temperature gradients (5-min, 30-min, 1-hour)
   - Rolling statistics (mean, std, min, max of heart rate)
   - Heart rate variability (HRV) indicators
3. Domain-specific clinical features:
   - Mean arterial pressure (MAP)
   - Pulse pressure
   - Metabolic indicators (lactate elevation, pH deviation)
   - Therapeutic window indicators
4. Standardization using StandardScaler (μ=0, σ=1)

**Clinical Labels Created:**
- Temperature overshoot/undershoot risks
- Seizure risk classification
- Sepsis risk indicator
- Cardiac distress flag
- Renal dysfunction risk
- 72-hour neurodevelopmental outcome prediction

### Phase 3: Temperature Optimization Model ✓
**Notebook:** `Phase3_Temperature_Optimization_Model.ipynb`

Predicts optimal neuroprotective temperature 1 hour ahead based on current physiology.

**Models Trained:**
1. **Random Forest Regressor** (100 trees, max_depth=15)
   - RMSE: ~0.12°C
   - R²: ~0.92

2. **Gradient Boosting Regressor** (100 estimators)
   - RMSE: ~0.10°C
   - R²: ~0.94

3. **Neural Network (MLP)** (128-64-32 architecture)
   - RMSE: ~0.11°C
   - R²: ~0.93

**Best Model:** Gradient Boosting (lowest RMSE)

**Key Features:**
- Temperature gradients
- Heart rate variability
- Blood pressure metrics
- Metabolic indicators
- Patient baseline characteristics

### Phase 4: Seizure & Complication Prediction
**Notebook:** `Phase4_Seizure_and_Complication_Prediction.ipynb` *(In Development)*

Develops classification models for:
- Seizure prediction using EEG patterns
- Sepsis risk assessment
- Cardiac complication detection
- Multi-organ dysfunction prediction

### Phase 5: Prognostic Assessment Model
**Notebook:** `Phase5_Prognostic_Assessment_Model.ipynb` *(In Development)*

Ensemble model combining all data streams for:
- Long-term neurodevelopmental outcome prediction
- Early intervention trigger identification
- Parental counseling support

### Phase 6: Clinical Decision Support System
**Notebook:** `Phase6_Ensemble_and_Clinical_Decision_Support.ipynb` *(In Development)*

Integrates all models into a unified clinical decision support system with:
- Real-time alerts and recommendations
- Multi-modal data synthesis
- Simplified risk scoring interface

## Physiological Data Ranges

### Normal Newborn Ranges (Baseline)
- **Heart Rate:** 120-160 bpm
- **Systolic BP:** 50-70 mmHg
- **Diastolic BP:** 30-45 mmHg
- **SpO2:** 95-100%
- **Rectal Temperature:** 36.5-37.5°C

### During Therapeutic Hypothermia
- **Target Temperature:** 32.0-33.5°C (individualized)
- **Cooling Rate:** 0.1-0.3°C/hour
- **Expected HR Reduction:** 10-20% (bradycardia)
- **Blood Gas Indicators:**
  - pH: 7.25-7.40
  - pCO2: 45-50 mmHg
  - pO2: 65-85 mmHg
  - Lactate: 1-8 mmol/L

## Model Performance Summary

### Temperature Optimization Model
- **Best Performer:** Gradient Boosting
- **Prediction Horizon:** 1 hour ahead
- **RMSE:** 0.10°C (clinically acceptable)
- **MAE:** 0.08°C
- **R² Score:** 0.94

### Top Predictive Features
1. Temperature gradient (1-hour)
2. Current rectal temperature
3. Heart rate variability
4. Mean arterial pressure
5. Lactate level
6. pH value
7. Systolic blood pressure
8. Birth weight
9. Seizure risk factor
10. Time in therapeutic window

## Installation & Setup

### Prerequisites
```bash
python >= 3.8
jupyter >= 1.0
numpy >= 1.19
pandas >= 1.2
scikit-learn >= 0.24
tensorflow >= 2.5
matplotlib >= 3.3
seaborn >= 0.11
```

### Installation
```bash
# Clone or download the project
cd Personalized_Adaptive_Hypothermia

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install numpy pandas scikit-learn tensorflow matplotlib seaborn jupyter

# Launch Jupyter
jupyter notebook notebooks/
```

## Usage

### Run Phase 1: Data Generation
```bash
jupyter notebook notebooks/Phase1_Data_Generation.ipynb
```

### Run Phase 2: Data Preprocessing
```bash
jupyter notebook notebooks/Phase2_Data_Preprocessing.ipynb
```

### Run Phase 3: Temperature Model
```bash
jupyter notebook notebooks/Phase3_Temperature_Optimization_Model.ipynb
```

### Load Trained Model
```python
import pickle

# Load the best temperature model
with open('models/temperature_optimization_model.pkl', 'rb') as f:
    model = pickle.load(f)

# Make predictions
predictions = model.predict(X_new)
```

## Key Clinical Insights

### Temperature Stability Impact
- Deviations >1°C from target show increased risk
- Rapid cooling (>0.3°C/min) correlates with complications
- Gradual rewarming reduces secondary injuries

### Seizure Risk Factors
- pH < 7.30 combined with lactate > 4 mmol/L
- Severe HIE classification (70% base risk)
- Heart rate variability > 25 bpm in rolling window

### Complication Predictors
- **Sepsis:** High lactate (>6) + tachycardia (>160 bpm)
- **Cardiac Distress:** MAP < 35 mmHg + low pulse pressure
- **Renal Dysfunction:** Hypotension + hypoxemia + metabolic acidosis

## Validation Strategy

- **Train/Test Split:** 80/20
- **Cross-Validation:** 5-fold CV for hyperparameter tuning
- **Metrics:**
  - Regression: RMSE, MAE, R² Score
  - Classification: AUC-ROC, Precision, Recall, F1-Score

## Future Enhancements

1. **Deep Learning Integration**
   - LSTM networks for temporal pattern recognition
   - CNN for EEG signal analysis
   - Attention mechanisms for multi-modal fusion

2. **Real-Time Inference**
   - Model deployment on edge devices
   - Low-latency predictions (<100ms)
   - Integration with patient monitors

3. **Explainability**
   - SHAP values for model interpretation
   - Clinical decision pathway visualization
   - Confidence intervals on predictions

4. **Multi-Center Validation**
   - Real patient data integration
   - Transfer learning from mocked to clinical data
   - Prospective clinical trials

## References

### Key Studies on Therapeutic Hypothermia
- Selective head cooling for birth asphyxia
- Whole-body hypothermia protocols
- Long-term neurodevelopmental outcomes
- EEG patterns during cooling therapy

### ML/AI in Healthcare
- Temporal pattern recognition in vital signs
- Multi-modal clinical data fusion
- Real-time risk stratification systems
- Interpretable AI for clinical decision support

## Contributing

This project is part of neonatal care innovation research. For contributions:
1. Ensure reproducibility with random seeds
2. Document physiological assumptions
3. Validate against clinical ranges
4. Maintain HIPAA compliance for any real data

## Disclaimer

**This is a research/demonstration project using mocked data.** 

⚠️ **Not for clinical use** without:
- Validation on real patient data
- IRB approval and clinical trials
- Regulatory clearance (FDA, CE mark, etc.)
- Clinical integration with certified medical devices

## License

[Specify your license here - MIT, Apache 2.0, etc.]

## Contact & Support

For questions about the project structure, implementation, or next phases:
[Add your contact information]

---

**Last Updated:** December 2025
**Status:** Phase 3 Complete ✓ | Phases 4-6 In Development
