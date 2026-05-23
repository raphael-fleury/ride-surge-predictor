from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
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

def create_app():
    """Creates and configures the FastAPI application."""
    app = FastAPI(
        title="Ride Surge Predictor API",
        description="API for predicting ride prices based on origin, destination, and datetime",
        version="1.0.0"
    )
    
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
        
        try:
            # Get weather data for origin location
            weather = get_current_weather(request.origin.latitude, request.origin.longitude)
            
            predicted_price = predict_price(
                datetime=request.datetime,
                wait_time_minutes=5.0,  # Default wait time
                temperature_celsius=weather.get('temperature') or 25.0,
                precipitation_mm=weather.get('precipitation') or 0.0,
                weather_code=int(weather.get('weather_code') or 0),
                origin_lat=request.origin.latitude,
                origin_lon=request.origin.longitude,
                dest_lat=request.destination.latitude,
                dest_lon=request.destination.longitude
            )
            
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
