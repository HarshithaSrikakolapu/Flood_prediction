# Predictive Flood Early Warning System (PFEWS)

A hackathon-ready flood prediction and simulation platform using multi-source sensor fusion (Rainfall, River Level, Soil Moisture, Elevation).

## Features
- **Real-time Risk Assessment**: Rule-based logic to classify flood risk (LOW, MEDIUM, HIGH).
- **Interactive Grid Simulation**: 2D/3D water flow simulation based on elevation topography.
- **Sensor Fusion Dashboard**: Mock sensor inputs for rainfall, river levels, and moisture.
- **Alert System**: Immediate recommendations based on current risk factors.

## Tech Stack
- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit
- **Logic**: NumPy (Simulation), Plotly (3D Visuals)

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Both Services (Recommended)
We provide a convenience script to start both the backend and frontend at once:
```bash
python run_all.py
```

### 3. Alternative: Run Separately
**Backend:** `uvicorn backend.main:app --reload`
**Frontend:** `streamlit run frontend/app.py`

## API Call Example
You can test the risk engine externally using `curl`:
```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"rainfall": 0.8, "river_level": 0.7, "elevation": 5.0, "soil_moisture": 0.9}'
```

## Error Handling
- **Backend**: Uses Pydantic for input validation. Returns 422 for malformed JSON and 500 for calculation errors.
- **Frontend**: Handles connection timeouts and non-200 responses with user-friendly error messages in the dashboard.

## How to Demo
1. Open the Streamlit dashboard.
2. Use the **Sidebar Sliders** to simulate different environmental conditions:
   - Increase **Rainfall** and **River Level** to trigger HIGH risk.
   - Decrease them for LOW risk.
3. Click **Trigger Prediction** to see the risk level and recommendation.
4. Click **Run 15-Step Flow Simulation** to see a 3D animation of water accumulating in lower elevations across the grid.
