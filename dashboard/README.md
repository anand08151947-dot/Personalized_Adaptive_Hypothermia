# Clinical Decision Support Dashboard

Modern React + TypeScript dashboard for real-time patient monitoring.

## Quick Start

```powershell
# Install dependencies
cd dashboard
npm install

# Start development server (connects to API on port 8000)
npm run dev

# Open browser to http://localhost:3000
```

## Features

- **Real-time Monitoring**: Auto-refreshes every 10 seconds
- **Risk Visualization**: Color-coded alerts (RED=HIGH, YELLOW=MED, GREEN=LOW)
- **Interactive Charts**: Click patients to see detailed probability charts
- **Clinical Recommendations**: Evidence-based interventions displayed per patient
- **Temperature Management**: Visual indicators for cooling adjustments

## Architecture

- **Frontend**: React 18 + TypeScript + Vite
- **Charts**: Recharts for data visualization
- **Icons**: Lucide React
- **API Proxy**: Vite dev server proxies `/api/*` to `http://localhost:8000`

## Build for Production

```powershell
npm run build
npm run preview
```
