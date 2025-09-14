import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import numpy as np

# --- Load Environment Variables ---
load_dotenv()
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

# --- Hardcoded Statistical Model ---
# This eliminates all file loading errors. The model is now part of the code.
model_stats = {
    "mean_yield": 143.40654101675244,
    "std_dev_yield": 56.09032380666645
}
print("--- Anomaly detection stats are hardcoded successfully. ---")


# --- Pydantic Models (Unchanged) ---
class SimulationInput(BaseModel):
    surface_area: float = Field(..., gt=0)
    location: str = Field(..., min_length=2)


# --- Core Logic (Unchanged) ---
def calculate_water_harvest(surface_area: float, relative_humidity: float) -> float:
    BASELINE_YIELD_PER_SQ_METER = 1.11
    BASELINE_HUMIDITY = 0.20
    if relative_humidity <= 0 or surface_area <= 0: return 0.0
    humidity_factor = relative_humidity / BASELINE_HUMIDITY
    estimated_yield = surface_area * BASELINE_YIELD_PER_SQ_METER * humidity_factor
    return round(estimated_yield, 2)

async def get_weather_data(city: str) -> dict:
    if not OPENWEATHERMAP_API_KEY: raise HTTPException(status_code=500, detail="OpenWeatherMap API key is not configured.")
    api_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url)
    if response.status_code != 200: raise HTTPException(status_code=response.status_code, detail=f"Error fetching weather data for '{city}'.")
    data = response.json()
    humidity = data["main"]["humidity"] / 100
    temperature = data["main"]["temp"]
    return {"relative_humidity": humidity, "temperature_celsius": temperature}

# --- Z-Score Anomaly Detection (Unchanged) ---
def is_anomalous(yield_value: float, threshold: float = 3.5) -> bool:
    if not model_stats: return False
    mean = model_stats["mean_yield"]
    std_dev = model_stats["std_dev_yield"]
    if std_dev == 0: return False
    z_score = abs((yield_value - mean) / std_dev)
    return z_score > threshold


# --- FastAPI Application ---
app = FastAPI()

@app.post("/simulate")
async def run_simulation(input_data: SimulationInput):
    weather_data = await get_weather_data(input_data.location)
    estimated_yield = calculate_water_harvest(surface_area=input_data.surface_area, relative_humidity=weather_data["relative_humidity"])
    is_anomaly = is_anomalous(yield_value=estimated_yield)
    forecast_data = [round(estimated_yield * v, 2) for v in [1.0, 1.05, 0.98, 1.10, 0.95, 1.02, 1.08]]
    return {
        "input_parameters": input_data,
        "live_weather_data": weather_data,
        "estimated_yield_liters_per_day": estimated_yield,
        "forecast_7_day": forecast_data,
        "anomaly_flag": is_anomaly
    }