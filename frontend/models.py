from pydantic import BaseModel, Field
from typing import List, Optional

class PredictRequest(BaseModel):
    rainfall: float = Field(..., ge=0, description="Amount of rainfall in mm or normalized unit")
    river_level: float = Field(..., ge=0, description="River water level")
    elevation: float = Field(..., gt=0, description="Elevation above sea level (must be > 0)")
    soil_moisture: float = Field(..., ge=0, description="Soil moisture level (0-1 or percentage)")

class PredictResponse(BaseModel):
    risk_score: float
    risk_level: str

class LocationPredictRequest(BaseModel):
    city: Optional[str] = Field(None, description="City name")
    lat: Optional[float] = Field(None, description="Latitude")
    lon: Optional[float] = Field(None, description="Longitude")
    elevation: float = Field(10.0, gt=0, description="Elevation above sea level")

class LocationPredictResponse(BaseModel):
    risk_score: float
    risk_level: str
    weather_data: dict = Field(..., description="Fetched weather data details")

class SimulationRequest(BaseModel):
    grid_size: int = 10
    elevation_grid: List[List[float]]
    initial_water_level: float
    rainfall_intensity: float

class SimulationResponse(BaseModel):
    steps: List[List[List[float]]] # 3D array: [step][row][col]
