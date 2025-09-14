import os
import httpx
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import joblib
import numpy as np

# --- Load Environment Variables ---
load_dotenv()
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

# --- NEW: Bulletproof Model Loading ---
# This is the guaranteed way to find a file in a deployed environment.
# It builds an absolute path to the model file based on the script's own location.
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_PATH = os.path.join(BASE_DIR, "anomaly_model.joblib")
    anomaly_model = joblib.load(MODEL_PATH)
    print("--- Anomaly detection model loaded successfully. ---")
except FileNotFoundError:
    anomaly_model = None
    print("--- WARNING: Anomaly detection model not found. Proceeding without it. ---")


# --- Pydantic Models ---
class SimulationInput(BaseModel):
    surface_area: float = Field(..., gt=0)
    location: str = Field(..., min_length=2)


# --- Core Application Logic (Unchanged) ---
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

def is_anomalous(humidity: float, yield_value: float) -> bool:
    if anomaly_model is None: return False
    data_point = np.array([[humidity, yield_value]])
    prediction = anomaly_model.predict(data_point)
    return prediction[0] == -1


# --- FastAPI Application (Unchanged) ---
app = FastAPI()

@app.post("/simulate")
async def run_simulation(input_data: SimulationInput):
    weather_data = await get_weather_data(input_data.location)
    estimated_yield = calculate_water_harvest(surface_area=input_data.surface_area, relative_humidity=weather_data["relative_humidity"])
    is_anomaly = is_anomalous(humidity=weather_data["relative_humidity"], yield_value=estimated_yield)
    forecast_data = [round(estimated_yield * v, 2) for v in [1.0, 1.05, 0.98, 1.10, 0.95, 1.02, 1.08]]
    return {
        "input_parameters": input_data,
        "live_weather_data": weather_data,
        "estimated_yield_liters_per_day": estimated_yield,
        "forecast_7_day": forecast_data,
        "anomaly_flag": is_anomaly
    }