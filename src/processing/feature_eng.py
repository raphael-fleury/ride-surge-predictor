import pandas as pd
import numpy as np

VALID_CATEGORIES = ['uber_x', 'uber_moto', 'comfort', 'bag']

def prepare_data(df):
    df = clean_data(df)

    # Calculated features
    df = extract_time_features(df)
    df['price_per_meter'] = df.apply(lambda row: row['price'] / row['distance_m'] if row['distance_m'] > 0 else 0, axis=1)
    df['price_per_min'] = df.apply(lambda row: row['price'] / (row['estimated_time_s'] / 60) if row['estimated_time_s'] > 0 else 0, axis=1)
    
    df['route_avg_price'] = df.groupby('route_id')['price'].transform('mean')
    df['route_median_price'] = df.groupby('route_id')['price'].transform('median')
    
    df['price_variation_from_route_avg'] = df['price'] / df['route_avg_price']
    df['price_variation_from_route_median'] = df['price'] / df['route_median_price']
    
    # Drop name columns
    df = df.drop(columns=['from', 'to', 'route_name'], errors='ignore')
    
    return df

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
    
    # Handle missing weather data (if Open-Meteo API failed during a ping)
    # We forward-fill the last known weather, then fill remaining with 0 or mean.
    df['temperature_celsius'] = df['temperature_celsius'].ffill().fillna(df['temperature_celsius'].mean())
    df['precipitation_mm'] = df['precipitation_mm'].fillna(0.0)
    df['weather_code'] = df['weather_code'].fillna(0).astype(int)
    
    # Filter invalid ride categories (hallucinated by LLM)
    df = df[df['ride_id'].isin(VALID_CATEGORIES)]
    
    # Drop duplicates (LLM might repeat the same row in the JSON array)
    df = df.drop_duplicates()
    
    dropped = initial_len - len(df)
    print(f"    | Cleaned data. Removed {dropped} invalid/hallucinated rows.")
    return df

def extract_time_features(df):
    """Creates time-series features for Machine Learning."""
    
    # Parse timestamps (Format: 2026-05-21 17:50:09)
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S')
    
    df['hour'] = df['timestamp'].dt.hour
    df['minute'] = df['timestamp'].dt.minute
    df['day'] = df['timestamp'].dt.day
    df['day_of_week'] = df['timestamp'].dt.dayofweek # 0=Monday, 6=Sunday
    df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
    
    df['day_sin'] = np.sin(2 * np.pi * df['day'] / 31)
    df['day_cos'] = np.cos(2 * np.pi * df['day'] / 31)
    
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    
    df['weekday_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
    df['weekday_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
    
    df.drop(columns=['timestamp'], inplace=True)
    return df
