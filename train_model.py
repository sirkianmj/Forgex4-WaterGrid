import pandas as pd
import numpy as np
import json

print("--- Statistical Model Training Script ---")

# --- 1. Configuration ---
NUM_SAMPLES = 1000
MODEL_FILE_NAME = "model_stats.json" # We will now save to a simple JSON file
YIELD_FACTOR = 250

# --- 2. Generate Synthetic "Normal" Data (Unchanged) ---
print(f"Generating {NUM_SAMPLES} samples of 'normal' data...")
np.random.seed(42)
humidity_data = 0.20 + (0.95 - 0.20) * np.random.rand(NUM_SAMPLES)
noise = np.random.normal(0, 15, NUM_SAMPLES)
yield_data = (humidity_data * YIELD_FACTOR) + noise
df = pd.DataFrame({'humidity': humidity_data, 'yield': yield_data})
df['yield'] = df['yield'].clip(lower=0)
print("Synthetic data generated successfully.")

# --- 3. Calculate Descriptive Statistics ---
print("Calculating mean and standard deviation of the 'yield' data...")
mean_yield = df['yield'].mean()
std_dev_yield = df['yield'].std()

print(f"Mean Yield: {mean_yield}")
print(f"Standard Deviation: {std_dev_yield}")

# --- 4. Save the Statistics to a File ---
stats = {
    "mean_yield": mean_yield,
    "std_dev_yield": std_dev_yield
}
with open(MODEL_FILE_NAME, 'w') as f:
    json.dump(stats, f)

print(f"--- Model statistics saved to '{MODEL_FILE_NAME}' successfully! ---")