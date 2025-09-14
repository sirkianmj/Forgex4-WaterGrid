from fastapi import FastAPI

# Create an instance of the FastAPI class
app = FastAPI()



def calculate_water_harvest(surface_area: float, relative_humidity: float) -> float:
    """
    Calculates the estimated daily water yield based on a simplified model
    derived from the PEG-SiO2 Nanocomposite technical paper.

    Args:
        surface_area (float): The facade surface area in square meters.
        relative_humidity (float): The current relative humidity as a decimal (e.g., 0.60 for 60%).

    Returns:
        float: The estimated water yield in Liters per day.
    """
    # --- Constants based on the scientific paper's data ---
    # Yield (L/m^2/day) at the baseline humidity level.
    BASELINE_YIELD_PER_SQ_METER = 1.11
    # The baseline humidity condition (20%).
    BASELINE_HUMIDITY = 0.20

    # Basic validation: no water can be harvested with no area or humidity.
    if relative_humidity <= 0 or surface_area <= 0:
        return 0.0

    # Simplified linear scaling model for the MVP:
    # We assume the yield scales directly with humidity relative to the baseline.
    # For example, at 40% humidity (0.40), the yield per square meter should be double the baseline.
    humidity_factor = relative_humidity / BASELINE_HUMIDITY
    
    estimated_yield = surface_area * BASELINE_YIELD_PER_SQ_METER * humidity_factor

    # Return the result rounded to two decimal places for cleanliness.
    return round(estimated_yield, 2)


# Define a "route" or "endpoint"
@app.get("/")
def read_root():
    return {"Hello": "World"}