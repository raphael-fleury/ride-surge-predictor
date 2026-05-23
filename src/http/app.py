import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal, Optional

from src.models.predict import predict_price as get_prediction

logger = logging.getLogger(__name__)

class Location(BaseModel):
    latitude: float
    longitude: float

class PredictionRequest(BaseModel):
    origin: Location
    destination: Location
    datetime: str  # Format: "YYYY-MM-DD HH:MM:SS"
    rideType: Literal["uber_x", "uber_moto", "comfort", "bag"]
    temperature: Optional[float] = None  # Optional, in Celsius
    precipitation: Optional[float] = None  # Optional, in mm
    weatherCode: Optional[int] = None  # Optional, WMO weather code

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
        Predicts ride price based on origin, destination, and other parameters.
        
        Parameters:
        - origin: {latitude, longitude}
        - destination: {latitude, longitude}
        - datetime: "YYYY-MM-DD HH:MM:SS"
        - rideType: one of ["uber_x", "uber_moto", "comfort", "bag"]
        - temperature: float (optional, temperature in Celsius, defaults to 25.0)
        - precipitation: float (optional, precipitation in mm, defaults to 0.0)
        - weatherCode: int (optional, WMO weather code, defaults to 0)
        
        Returns predicted price and model information.
        """
        
        try:
            # Use default values if weather parameters are not provided
            temperature_celsius = request.temperature if request.temperature is not None else 25.0
            precipitation_mm = request.precipitation if request.precipitation is not None else 0.0
            weather_code = request.weatherCode if request.weatherCode is not None else 0
            
            # Call the prediction function from predict.py
            predicted_price = get_prediction(
                ride_type=request.rideType,
                datetime=request.datetime,
                wait_time_minutes=5.0,  # Default wait time
                temperature_celsius=temperature_celsius,
                precipitation_mm=precipitation_mm,
                weather_code=weather_code,
                origin_lat=request.origin.latitude,
                origin_lon=request.origin.longitude,
                dest_lat=request.destination.latitude,
                dest_lon=request.destination.longitude
            )
            
            # Determine confidence level based on whether weather data was provided
            confidence = "high" if request.temperature is not None else "medium"
            
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
