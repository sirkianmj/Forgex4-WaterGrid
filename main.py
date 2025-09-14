import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# --- Load Environment Variables ---
load_dotenv()
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

# --- Application-level Checks ---
if not OPENWEATHERMAP_API_KEY:
    raise RuntimeError("FATAL: OPENWEATHERMAP_API_KEY environment variable not set.")

# --- Hardcoded Statistical Model ---
# This contains the mean and standard deviation from historical training data.
MODEL_STATS = {
    "mean_yield": 143.40654101675244,
    "std_dev_yield": 56.09032380666645
}

# --- Pydantic Models (Data Validation) ---
class SimulationInput(BaseModel):
    """Input model for the simulation endpoint."""
    surface_area: float = Field(..., gt=0, description="The surface area in square meters.")
    location: str = Field(..., min_length=2, description="The city name for weather data.")

# --- Core Application Logic ---
def calculate_water_harvest(surface_area: float, relative_humidity: float) -> float:
    """
    Calculates the estimated daily water yield based on a simplified model.
    """
    BASELINE_YIELD_PER_SQ_METER = 1.11
    BASELINE_HUMIDITY = 0.20  # Represents 20% humidity

    if relative_humidity <= 0 or surface_area <= 0:
        return 0.0

    # Adjust yield based on how the current humidity compares to the baseline.
    humidity_factor = relative_humidity / BASELINE_HUMIDITY
    estimated_yield = surface_area * BASELINE_YIELD_PER_SQ_METER * humidity_factor
    return round(estimated_yield, 2)

async def get_weather_data(city: str) -> dict:
    """
    Fetches live weather data from the OpenWeatherMap API.
    """
    api_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(api_url)
            response.raise_for_status()  # Raise an exception for 4XX or 5XX status codes
            data = response.json()

            # Safely extract data to prevent server errors on unexpected API responses
            humidity = data["main"]["humidity"] / 100
            temperature = data["main"]["temp"]
            return {"relative_humidity": humidity, "temperature_celsius": temperature}

        except httpx.HTTPStatusError as e:
            # Handle API-level errors (e.g., city not found, invalid key)
            raise HTTPException(status_code=e.response.status_code, detail=f"Error fetching weather data for '{city}'.")
        except (KeyError, TypeError):
            # Handle unexpected JSON structure from the API
            raise HTTPException(status_code=500, detail="Could not parse weather data from API response.")

# --- Z-Score Anomaly Detection ---
def is_anomalous(yield_value: float, threshold: float = 3.5) -> bool:
    """
    Checks if a result is anomalous using Z-score on the total yield.
    A Z-score above the threshold is considered an anomaly.
    """
    mean = MODEL_STATS["mean_yield"]
    std_dev = MODEL_STATS["std_dev_yield"]

    if std_dev == 0:
        return False  # Cannot compute Z-score if standard deviation is zero

    z_score = abs((yield_value - mean) / std_dev)
    return z_score > threshold

# --- FastAPI Application ---
app = FastAPI(
    title="Water Harvest Simulation API",
    description="An API to simulate water yield based on location and surface area."
)

@app.post("/simulate")
async def run_simulation(input_data: SimulationInput):
    """
    Runs a simulation to estimate daily water yield.
    """
    # 1. Fetch live weather conditions
    weather_data = await get_weather_data(input_data.location)

    # 2. Calculate the estimated water yield
    estimated_yield = calculate_water_harvest(
        surface_area=input_data.surface_area,
        relative_humidity=weather_data["relative_humidity"]
    )

    # 3. Check if the result is a statistical anomaly
    is_anomaly = is_anomalous(yield_value=estimated_yield)

    # 4. Generate a simple 7-day forecast based on the current yield
    forecast_multipliers = [1.0, 1.05, 0.98, 1.10, 0.95, 1.02, 1.08]
    forecast_data = [round(estimated_yield * v, 2) for v in forecast_multipliers]

    # 5. Return the consolidated results
    return {
        "input_parameters": input_data,
        "live_weather_data": weather_data,
        "estimated_yield_liters_per_day": estimated_yield,
        "forecast_7_day": forecast_data,
        "anomaly_flag": is_anomaly
    }