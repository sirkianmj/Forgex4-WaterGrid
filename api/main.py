import os
import httpx
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# --- Load Environment Variables ---
# This line loads the OPENWEATHERMAP_API_KEY from your .env file
load_dotenv()
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

# --- Pydantic Models (Data Validation) ---
class SimulationInput(BaseModel):
    surface_area: float = Field(
        ..., 
        gt=0, 
        description="The facade surface area in square meters. Must be greater than 0."
    )
    location: str = Field(
        ...,
        min_length=2,
        description="The city name for which to fetch weather data."
    )

# --- Core Application Logic ---
def calculate_water_harvest(surface_area: float, relative_humidity: float) -> float:
    # This function remains unchanged
    BASELINE_YIELD_PER_SQ_METER = 1.11
    BASELINE_HUMIDITY = 0.20
    if relative_humidity <= 0 or surface_area <= 0:
        return 0.0
    humidity_factor = relative_humidity / BASELINE_HUMIDITY
    estimated_yield = surface_area * BASELINE_YIELD_PER_SQ_METER * humidity_factor
    return round(estimated_yield, 2)

async def get_weather_data(city: str) -> dict:
    """Fetches weather data from OpenWeatherMap API."""
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
    # The humidity is given as a percentage, so we divide by 100
    humidity = data["main"]["humidity"] / 100
    temperature = data["main"]["temp"]
    
    return {"relative_humidity": humidity, "temperature_celsius": temperature}

# --- FastAPI Application ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/simulate")
async def run_simulation(input_data: SimulationInput):
    """
    Runs the simulation by fetching real-world weather data for a given location.
    """
    # 1. Fetch live weather data
    weather_data = await get_weather_data(input_data.location)
    
    # 2. Run the simulation with the fetched humidity
    estimated_yield = calculate_water_harvest(
        surface_area=input_data.surface_area,
        relative_humidity=weather_data["relative_humidity"]
    )

    # 3. Return a comprehensive result
    return {
        "input_parameters": input_data,
        "live_weather_data": weather_data,
        "estimated_yield_liters_per_day": estimated_yield
    }