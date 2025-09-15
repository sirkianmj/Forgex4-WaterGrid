import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# --- Load Environment Variables ---
load_dotenv()
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

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

# --- NEW: Final, Correct, Rule-Based Anomaly Detection ---
def get_anomaly_info(yield_value: float, surface_area: float) -> dict:
    """
    Checks if the result is anomalous based on two simple, robust rules.
    Returns a dictionary with the flag and debug information.
    """
    # Rule 1: Check if the input surface area is nonsensical.
    # 10,000,000 m^2 is 10 square kilometers, a generous upper limit for a single building facade.
    MAX_SANE_SURFACE_AREA = 10_000_000.0
    
    is_area_anomaly = surface_area > MAX_SANE_SURFACE_AREA
    
    # Rule 2: Check if the yield per square meter is physically impossible.
    # This catches data corruption errors (e.g., humidity > 100%).
    yield_per_sq_meter = 0
    if surface_area > 0:
        yield_per_sq_meter = yield_value / surface_area
        
    MAX_PHYSICALLY_POSSIBLE_YIELD_PER_SQ_METER = 10.0
    is_yield_anomaly = yield_per_sq_meter > MAX_PHYSICALLY_POSSIBLE_YIELD_PER_SQ_METER

    # The final flag is true if EITHER rule is broken.
    final_flag = is_area_anomaly or is_yield_anomaly

    # This debug info will be sent to the frontend!
    debug_info = {
        "reasoning": "Anomaly is true if either the input area is too large or the yield per m^2 is physically impossible.",
        "input_surface_area": surface_area,
        "max_sane_surface_area": MAX_SANE_SURFACE_AREA,
        "is_area_anomaly": is_area_anomaly,
        "yield_per_sq_meter": round(yield_per_sq_meter, 2),
        "max_yield_per_sq_meter": MAX_PHYSICALLY_POSSIBLE_YIELD_PER_SQ_METER,
        "is_yield_anomaly": is_yield_anomaly,
        "final_decision": final_flag
    }
    
    return {"is_anomaly": final_flag, "debug_info": debug_info}


# --- FastAPI Application ---
app = FastAPI()

@app.post("/simulate")
async def run_simulation(input_data: SimulationInput):
    weather_data = await get_weather_data(input_data.location)
    estimated_yield = calculate_water_harvest(
        surface_area=input_data.surface_area,
        relative_humidity=weather_data["relative_humidity"]
    )
    
    # Call the new, correct anomaly function
    anomaly_result = get_anomaly_info(
        yield_value=estimated_yield,
        surface_area=input_data.surface_area
    )

    forecast_data = [round(estimated_yield * v, 2) for v in [1.0, 1.05, 0.98, 1.10, 0.95, 1.02, 1.08]]
    
    return {
        "input_parameters": input_data,
        "live_weather_data": weather_data,
        "estimated_yield_liters_per_day": estimated_yield,
        "forecast_7_day": forecast_data,
        "anomaly_flag": anomaly_result["is_anomaly"],
        "debug_info": anomaly_result["debug_info"] # We now return the debug info!
    }