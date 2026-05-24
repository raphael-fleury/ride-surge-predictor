import os
import joblib
import logging
import pandas as pd
from src.integrations.api import get_routes

MODELS_DIR = os.path.join(os.getcwd(), "models")

logger = logging.getLogger(__name__)

def load_best_model():
    """Loads the best trained model from disk."""
    model_path = os.path.join(MODELS_DIR, "model.joblib")
    
    if not os.path.exists(model_path):
        raise RuntimeError("Model file 'model.joblib' not found. Please run training first.")
    
    try:
        return joblib.load(model_path)
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise RuntimeError(f"Error loading model: {e}")
    
def predict_price(ride_type, datetime, wait_time_minutes, temperature_celsius, precipitation_mm, weather_code, origin_lat, origin_lon, dest_lat, dest_lon):
    """Predicts ride price using the loaded model and input features."""
    model = load_best_model()
    if model is None:
        raise RuntimeError("Model not available for prediction.")
    
    hour, minute, day_of_week, is_weekend = extract_datetime_features(datetime)
    features = pd.DataFrame({
        'ride_id': [ride_type],
        'route_name': [get_route_name(origin_lat, origin_lon, dest_lat, dest_lon)],
        'weather_code': [weather_code],
        'wait_time_minutes': [wait_time_minutes],
        'temperature_celsius': [temperature_celsius],
        'precipitation_mm': [precipitation_mm],
        'hour': [hour],
        'minute': [minute],
        'day_of_week': [day_of_week],
        'is_weekend': [is_weekend]
    })
    
    return model.predict(features)[0]

def extract_datetime_features(dt_str: str):
    """Extracts hour, minute, day_of_week, is_weekend from datetime string."""
    try:
        dt = pd.to_datetime(dt_str)
        hour = dt.hour
        minute = dt.minute
        day_of_week = dt.dayofweek  # 0=Monday, 6=Sunday
        is_weekend = 1 if day_of_week >= 5 else 0
        
        return hour, minute, day_of_week, is_weekend
    except Exception as e:
        logger.error(f"Error parsing datetime: {e}")
        raise ValueError(f"Invalid datetime format: {dt_str}. Use 'YYYY-MM-DD HH:MM:SS'")
    
def get_route_name(origin_lat, origin_lon, dest_lat, dest_lon):
    """Attempts to find matching route from available routes."""
    try:
        routes = get_routes()
        # Simple heuristic: find route with closest origin coordinates
        best_route = None
        best_distance = float('inf')
        
        for route in routes:
            origin = route.get('origin', {})
            route_lat = origin.get('latitude', 0)
            route_lon = origin.get('longitude', 0)
            
            # Calculate simple distance
            distance_origin = ((route_lat - origin_lat) ** 2 + (route_lon - origin_lon) ** 2) ** 0.5
            distance_dest = ((route_lat - dest_lat) ** 2 + (route_lon - dest_lon) ** 2) ** 0.5
            distance = distance_origin + distance_dest
            
            if distance < best_distance:
                best_distance = distance
                best_route = route.get('name', 'Unknown Route')
        
        return best_route or "Unknown Route"
    except Exception as e:
        logger.warning(f"Failed to fetch routes: {e}")
        return "Unknown Route"