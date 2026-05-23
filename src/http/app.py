from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import joblib
import pandas as pd
from datetime import datetime
import logging

from src.collection.weather import get_current_weather
from src.integrations.api import get_routes

logger = logging.getLogger(__name__)

class Location(BaseModel):
    latitude: float
    longitude: float

class PredictionRequest(BaseModel):
    origin: Location
    destination: Location
    datetime: str  # Format: "YYYY-MM-DD HH:MM:SS"

class PredictionResponse(BaseModel):
    predicted_price: float
    model_used: str
    confidence: str

MODELS_DIR = os.path.join(os.getcwd(), "models")

def load_best_model():
    """Loads the best trained model from disk."""
    model_files = {
        'xgboost': 'xgboost.joblib',
        'random_forest': 'random_forest.joblib',
        'linear_regression': 'regressão_linear_baseline.joblib'
    }
    
    best_model = None
    best_model_name = None
    
    # Try to load XGBoost first (usually the best performer)
    for model_key, filename in model_files.items():
        filepath = os.path.join(MODELS_DIR, filename)
        if os.path.exists(filepath):
            try:
                model = joblib.load(filepath)
                best_model = model
                best_model_name = model_key
                if model_key == 'xgboost':  # XGBoost is preferred if available
                    break
            except Exception as e:
                logger.warning(f"Failed to load {filename}: {e}")
                continue
    
    if best_model is None:
        raise RuntimeError("No trained models found in models/ directory")
    
    return best_model, best_model_name

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
            distance = ((route_lat - origin_lat) ** 2 + (route_lon - origin_lon) ** 2) ** 0.5
            
            if distance < best_distance:
                best_distance = distance
                best_route = route.get('name', 'Unknown Route')
        
        return best_route or "Unknown Route"
    except Exception as e:
        logger.warning(f"Failed to fetch routes: {e}")
        return "Unknown Route"

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

def create_app():
    """Creates and configures the FastAPI application."""
    app = FastAPI(
        title="Ride Surge Predictor API",
        description="API for predicting ride prices based on origin, destination, and datetime",
        version="1.0.0"
    )
    
    # Load model at startup
    try:
        model, model_name = load_best_model()
        app.state.model = model
        app.state.model_name = model_name
    except Exception as e:
        logger.error(f"Failed to load model at startup: {e}")
        app.state.model = None
        app.state.model_name = None
    
    @app.get("/health")
    def health_check():
        """Health check endpoint."""
        return {
            "status": "ok",
            "model_loaded": app.state.model is not None,
            "model_name": app.state.model_name
        }
    
    @app.post("/predict", response_model=PredictionResponse)
    def predict_price(request: PredictionRequest):
        """
        Predicts ride price based on origin, destination, and datetime.
        
        Parameters:
        - origin: {latitude, longitude}
        - destination: {latitude, longitude}
        - datetime: "YYYY-MM-DD HH:MM:SS"
        
        Returns predicted price and model information.
        """
        
        if app.state.model is None:
            raise HTTPException(status_code=503, detail="Model not available")
        
        try:
            # Extract datetime features
            hour, minute, day_of_week, is_weekend = extract_datetime_features(request.datetime)
            
            # Get weather data for origin location
            weather = get_current_weather(request.origin.latitude, request.origin.longitude)
            
            # Get route name
            route_name = get_route_name(
                request.origin.latitude,
                request.origin.longitude,
                request.destination.latitude,
                request.destination.longitude
            )
            
            # Default values for features not directly provided
            wait_time_minutes = 5.0  # Default wait time
            temperature_celsius = weather.get('temperature') or 25.0
            precipitation_mm = weather.get('precipitation') or 0.0
            weather_code = int(weather.get('weather_code') or 0)
            ride_id = "api_prediction"
            
            # Create feature dataframe in the same format as training
            features = pd.DataFrame({
                'route_name': [route_name],
                'ride_id': [ride_id],
                'weather_code': [weather_code],
                'wait_time_minutes': [wait_time_minutes],
                'temperature_celsius': [temperature_celsius],
                'precipitation_mm': [precipitation_mm],
                'hour': [hour],
                'minute': [minute],
                'day_of_week': [day_of_week],
                'is_weekend': [is_weekend]
            })
            
            # Make prediction using the pipeline (includes preprocessing)
            predicted_price = app.state.model.predict(features)[0]
            
            # Determine confidence level based on certain conditions
            confidence = "high" if weather.get('temperature') is not None else "medium"
            
            return PredictionResponse(
                predicted_price=float(predicted_price),
                model_used=app.state.model_name,
                confidence=confidence
            )
        
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise HTTPException(status_code=500, detail="Error making prediction")
    
    return app

if __name__ == "__main__":
    import uvicorn
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
