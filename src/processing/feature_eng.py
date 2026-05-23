import pandas as pd
import numpy as np

# valid categories
VALID_CATEGORIES =['uber_x', 'uber_moto', 'comfort', 'bag']

def clean_data(df):
    """Applies strict filtering to remove LLM hallucinations and bad data."""
    initial_len = len(df)
    
    # Drop rows where critical data is entirely missing
    df = df.dropna(subset=['price', 'wait_time_minutes', 'ride_id'])
    
    # Convert types (just in case LLM outputted strings)
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['wait_time_minutes'] = pd.to_numeric(df['wait_time_minutes'], errors='coerce')
    
    # Drop NaNs again if coercion failed
    df = df.dropna(subset=['price', 'wait_time_minutes'])
    
    # Filter Zeroes, Negatives, and Absurd values.
    df = df[(df['price'] > 0) & (df['price'] < 400.0)] # 400 max value
    df = df[(df['wait_time_minutes'] >= 0) & (df['wait_time_minutes'] < 60)]
    
    # Filter invalid ride categories (hallucinated by LLM)
    df = df[df['ride_id'].isin(VALID_CATEGORIES)]
    
    # Drop duplicates (LLM might repeat the same row in the JSON array)
    df = df.drop_duplicates()
    
    dropped = initial_len - len(df)
    print(f"    | Cleaned data. Removed {dropped} invalid/hallucinated rows.")
    return df

def engineer_features(df):
    """Creates time-series features for Machine Learning."""
    
    # Parse timestamps (Format: 2026-05-21 17:50:09)
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S')
    
    # Extract temporal features
    df['hour'] = df['timestamp'].dt.hour
    df['minute'] = df['timestamp'].dt.minute
    df['day_of_week'] = df['timestamp'].dt.dayofweek # 0=Monday, 6=Sunday
    df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
    
    # Handle missing weather data (if Open-Meteo API failed during a ping)
    # We forward-fill the last known weather, then fill remaining with 0 or mean.
    df['temperature_celsius'] = df['temperature_celsius'].ffill().fillna(df['temperature_celsius'].mean())
    df['precipitation_mm'] = df['precipitation_mm'].fillna(0.0)
    
    # Route encoding: Create a string identifier for the route
    # This helps models like Random Forest later via One-Hot Encoding
    df['route_name'] = df['from'] + " -> " + df['to']
    
    print("    | Engineered time and route features.")
    return df