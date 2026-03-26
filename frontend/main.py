from fastapi import FastAPI, HTTPException
import numpy as np
import httpx
import os
from dotenv import load_dotenv
from .models import (
    PredictRequest, PredictResponse, 
    SimulationRequest, SimulationResponse,
    LocationPredictRequest, LocationPredictResponse
)
from .logic import calculate_refined_risk
from .simulation_engine import simulate_water

load_dotenv()  # Load OPENWEATHER_API_KEY from .env
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "your_api_key_here")

app = FastAPI(title="PFEWS Backend", description="Predictive Flood Early Warning System API")

@app.get("/")
async def root():
    return {"message": "PFEWS API - Refined Risk Model Active"}

@app.post("/predict", response_model=PredictResponse)
async def predict_flood(data: PredictRequest):
    try:
        report = calculate_refined_risk(
            rainfall=data.rainfall,
            river_level=data.river_level,
            soil_moisture=data.soil_moisture,
            elevation=data.elevation
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/location", response_model=LocationPredictResponse)
async def predict_location_flood(data: LocationPredictRequest):
    is_mock = False
    mock_map = {
        "bhimavaram": {"name": "Bhimavaram", "temp": 34, "hum": 94, "rain": 0.0},
        "narsapur": {"name": "Narsapur", "temp": 34, "hum": 94, "rain": 0.0}
    }
    
    city_low = data.city.lower() if data.city else ""
    
    if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY == "your_api_key_here" or OPENWEATHER_API_KEY == "" or city_low in mock_map:
        is_mock = True
        if city_low in mock_map:
            m = mock_map[city_low]
            weather_json = {
                "name": m["name"],
                "rain": {"1h": m["rain"]},
                "main": {"temp": m["temp"], "humidity": m["hum"]}
            }
        else:
            weather_json = {
                "name": f"Mock City ({data.city or 'Station 1'})",
                "rain": {"1h": 12.5},
                "main": {"temp": 22.5, "humidity": 75},
                "dt": 1618317040
            }
    else:
        # Fetch Weather Data
        async with httpx.AsyncClient() as client:
            if data.city:
                url = f"https://api.openweathermap.org/data/2.5/weather?q={data.city}&appid={OPENWEATHER_API_KEY}&units=metric"
            elif data.lat is not None and data.lon is not None:
                url = f"https://api.openweathermap.org/data/2.5/weather?lat={data.lat}&lon={data.lon}&appid={OPENWEATHER_API_KEY}&units=metric"
            else:
                raise HTTPException(status_code=400, detail="Missing city or coordinates")
            
            try:
                res = await client.get(url)
                if res.status_code != 200:
                    # Fallback to mock if API key is invalid
                    is_mock = True
                    weather_json = {
                        "name": f"Demo: {data.city or 'Search Result'}",
                        "rain": {"1h": 8.2},
                        "main": {"temp": 18.0, "humidity": 65}
                    }
                else:
                    weather_json = res.json()
            except Exception as e:
                is_mock = True
                weather_json = {
                    "name": "Demo (Offline)",
                    "rain": {"1h": 0.0},
                    "main": {"temp": 0, "humidity": 0}
                }

    # Extract Rainfall
    # rain might be missing if clear skies
    rainfall_mm = weather_json.get("rain", {}).get("1h", 0.0)
    
    # Normalize rainfall for the model
    rainfall_norm = min(1.0, rainfall_mm / 20.0)
    
    # Mock river_level and soil_moisture based on rainfall
    river_level = min(1.0, rainfall_norm * 0.8 + 0.1)
    soil_moisture = min(1.0, rainfall_norm * 0.6 + 0.2)
    
    # Calculate Risk
    report = calculate_refined_risk(
        rainfall=rainfall_norm,
        river_level=river_level,
        soil_moisture=soil_moisture,
        elevation=data.elevation
    )
    
    return LocationPredictResponse(
        risk_score=report["risk_score"],
        risk_level=report["risk_level"],
        weather_data={
            "city": weather_json.get("name"),
            "rainfall_1h": rainfall_mm,
            "humidity": weather_json.get("main", {}).get("humidity"),
            "temp": weather_json.get("main", {}).get("temp"),
            "mocked_river_level": river_level,
            "mocked_soil_moisture": soil_moisture,
            "is_demo": is_mock
        }
    )

@app.post("/simulate", response_model=SimulationResponse)
async def simulate_flood(req: SimulationRequest):
    print(f"DEBUG: Simulation started for grid {req.grid_size}x{req.grid_size}")
    try:
        elev = np.array(req.elevation_grid)
        initial_water = np.zeros_like(elev) + float(req.initial_water_level)
        
        history = [initial_water.tolist()]
        current_water = initial_water
        
        # We'll run it step-by-step to capture history for animation
        for i in range(15):
            current_water = simulate_water(current_water, elev, steps=1)
            history.append(current_water.tolist())
        
        print(f"DEBUG: Simulation complete. History length: {len(history)}")
        return SimulationResponse(steps=history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
