import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# --- Load Environment Variables ---
load_dotenv()
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

# --- YOUR EXCELLENT ADDITION: Fail-fast if the key is missing ---
if not OPENWEATHERMAP_API_KEY:
    raise RuntimeError("FATAL: OPENWEATHERMAP_API_KEY environment variable not set.")

# --- Hardcoded Statistical Model ---
MODEL_STATS = {
    "mean_yield": 143.40654101675244,
    "std_dev_yield": 56.09032380666645
}

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

# --- YOUR EXCELLENT ADDITION: More robust error handling ---
async def get_weather_data(city: str) -> dict:
    api_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(api_url)
            response.raise_for_status()
            data = response.json()
            humidity = data["main"]["humidity"] / 100
            temperature = data["main"]["temp"]
            return {"relative_humidity": humidity, "temperature_celsius": temperature}
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Error fetching weather data for '{city}'.")
        except (KeyError, TypeError):
            raise HTTPException(status_code=500, detail="Could not parse weather data from API response.")

# --- THE FINAL, CORRECTED LOGIC: Rule-based Anomaly Detection ---
def is_anomalous(yield_value: float, surface_area: float) -> bool:
    """Checks if the result is physically improbable."""
    if surface_area == 0: return False
    
    # Define a generous "world record" physical limit for this technology
    MAX_PHYSICALLY_POSSIBLE_YIELD_PER_SQ_METER = 10.0
    
    yield_per_sq_meter = yield_value / surface_area
    
    # If the calculated yield per square meter exceeds our defined physical limit, it is an anomaly.
    return yield_per_sq_meter > MAX_PHYSICALLY_POSSIBLE_YIELD_PER_SQ_METER


# --- FastAPI Application ---
app = FastAPI(
    title="Water Harvest Simulation API",
    description="An API to simulate water yield based on location and surface area."
)

@app.post("/simulate")
async def run_simulation(input_data: SimulationInput):
    weather_data = await get_weather_data(input_data.location)
    estimated_yield = calculate_water_harvest(
        surface_area=input_data.surface_area,
        relative_humidity=weather_data["relative_humidity"]
    )
    
    # Call the corrected, rule-based anomaly function
    is_anomaly = is_anomalous(
        yield_value=estimated_yield, 
        surface_area=input_data.surface_area
    )

    forecast_multipliers = [1.0, 1.05, 0.98, 1.10, 0.95, 1.02, 1.08]
    forecast_data = [round(estimated_yield * v, 2) for v in forecast_multipliers]
    
    return {
        "input_parameters": input_data,
        "live_weather_data": weather_data,
        "estimated_yield_liters_per_day": estimated_yield,
        "forecast_7_day": forecast_data,
        "anomaly_flag": is_anomaly
    }