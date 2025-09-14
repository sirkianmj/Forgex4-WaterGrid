import os
import httpx
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import joblib  # NEW: Import joblib to load our model
import numpy as np # NEW: Import numpy to shape our data for the model

# --- Load Environment Variables ---
load_dotenv()
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

# --- NEW: Load the AI Model on Startup ---
try:
    anomaly_model = joblib.load("anomaly_model.joblib")
    print("--- Anomaly detection model loaded successfully. ---")
except FileNotFoundError:
    anomaly_model = None
    print("--- WARNING: Anomaly detection model not found. Proceeding without it. ---")


# --- Pydantic Models ---
class SimulationInput(BaseModel):
    surface_area: float = Field(..., gt=0)
    location: str = Field(..., min_length=2)


# --- Core Application Logic ---
def calculate_water_harvest(surface_area: float, relative_humidity: float) -> float:
    BASELINE_YIELD_PER_SQ_METER = 1.11
    BASELINE_HUMIDITY = 0.20
    if relative_humidity <= 0 or surface_area <= 0:
        return 0.0
    humidity_factor = relative_humidity / BASELINE_HUMIDITY
    estimated_yield = surface_area * BASELINE_YIELD_PER_SQ_METER * humidity_factor
    return round(estimated_yield, 2)

async def get_weather_data(city: str) -> dict:
    if not OPENWEATHERMAP_API_KEY:
        raise HTTPException(status_code=500, detail="OpenWeatherMap API key is not configured.")
    api_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url)
    if response.status_code == 401:
        raise HTTPException(status_code=401, detail="Invalid OpenWeatherMap API key.")
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"City '{city}' not found.")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching weather data.")
    data = response.json()
    humidity = data["main"]["humidity"] / 100
    temperature = data["main"]["temp"]
    return {"relative_humidity": humidity, "temperature_celsius": temperature}

# NEW: Function to use our loaded AI model
def is_anomalous(humidity: float, yield_value: float) -> bool:
    if anomaly_model is None:
        return False
    data_point = np.array([[humidity, yield_value]])
    prediction = anomaly_model.predict(data_point)
    return prediction[0] == -1


# --- FastAPI Application ---
app = FastAPI()

# This is your existing, correct CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/simulate")
async def run_simulation(input_data: SimulationInput):
    weather_data = await get_weather_data(input_data.location)
    
    estimated_yield = calculate_water_harvest(
        surface_area=input_data.surface_area,
        relative_humidity=weather_data["relative_humidity"]
    )

    # NEW: Use the AI model to check for anomalies
    is_anomaly = is_anomalous(
        humidity=weather_data["relative_humidity"],
        yield_value=estimated_yield
    )

    # We are still using real weather data to generate the first day's yield.
    # The forecast for the next 6 days is a simple mock based on the first day.
    forecast_data = [round(estimated_yield * v, 2) for v in [1.0, 1.05, 0.98, 1.10, 0.95, 1.02, 1.08]]

    return {
        "input_parameters": input_data,
        "live_weather_data": weather_data,
        "estimated_yield_liters_per_day": estimated_yield,
        "forecast_7_day": forecast_data,
        "anomaly_flag": is_anomaly # NEW: Add the flag to our response
    }