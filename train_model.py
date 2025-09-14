import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib

print("--- Anomaly Detection Model Training Script ---")

# --- 1. Configuration ---
NUM_SAMPLES = 1000  # We will create 1000 "normal" examples.
MODEL_FILE_NAME = "anomaly_model.joblib"
# We'll use a simplified factor based on our core logic for generating data.
YIELD_FACTOR = 250 

# --- 2. Generate Synthetic "Normal" Data ---
print(f"Generating {NUM_SAMPLES} samples of synthetic 'normal' data...")

# Create 1000 random humidity values between 0.20 (20%) and 0.95 (95%).
np.random.seed(42) # This makes our random numbers predictable for consistency
humidity_data = 0.20 + (0.95 - 0.20) * np.random.rand(NUM_SAMPLES)

# Create corresponding yield data. The formula is: yield = humidity * FACTOR + small random noise.
# The "noise" makes the data look more realistic.
noise = np.random.normal(0, 15, NUM_SAMPLES) # Add some realistic variation
yield_data = (humidity_data * YIELD_FACTOR) + noise

# Create a clean DataFrame (a table) from our data.
df = pd.DataFrame({
    'humidity': humidity_data,
    'yield': yield_data
})

# Ensure yield can't be negative, which is physically impossible.
df['yield'] = df['yield'].clip(lower=0)

print("Synthetic data generated successfully.")
# Optional: print the first 5 rows to see what the data looks like
# print(df.head())

# --- 3. Train the AI Model ---
print("Training the Isolation Forest model...")

# Initialize the Isolation Forest model.
# `random_state` ensures we get the same result every time we run it.
# `contamination='auto'` is a good modern default for this algorithm.
model = IsolationForest(contamination='auto', random_state=42)

# "Fit" the model to the data. This is the training step.
# The model learns the boundaries of what is "normal".
model.fit(df[['humidity', 'yield']])

print("Model training complete.")

# --- 4. Save the Trained Model to a File ---
print(f"Saving the trained model to '{MODEL_FILE_NAME}'...")

# Use the joblib library to save our trained model object to a single file.
joblib.dump(model, MODEL_FILE_NAME)

print(f"--- Model saved successfully! You can now integrate '{MODEL_FILE_NAME}' into your API. ---")