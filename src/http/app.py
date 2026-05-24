import logging
import os
import joblib
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime

from src.models.predict import predict_price as get_prediction
from src.env import PORT

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

class SchedulerJob(BaseModel):
    id: str
    name: str
    next_run_time: Optional[str]
    trigger: str

def load_model():
    """Load the trained model from disk."""
    model_path = os.path.join(os.getcwd(), "models", "model.joblib")
    try:
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            # Try to extract model name from the pipeline's final estimator
            if hasattr(model, 'named_steps') and 'model' in model.named_steps:
                model_obj = model.named_steps['model']
                model_name = type(model_obj).__name__
            else:
                model_name = "Loaded Model"
            logger.info(f"Model loaded successfully: {model_name}")
            return model, model_name
        else:
            logger.warning(f"Model file not found at {model_path}")
            return None, "Not found"
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return None, f"Error: {str(e)}"

def create_app():
    """Creates and configures the FastAPI application."""
    
    # Initialize scheduler on app startup
    from src.scheduler import init_scheduler
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Manage application lifespan: startup and shutdown events."""
        # Startup - Initialize app state
        app.state.model, app.state.model_name = load_model()
        
        try:
            app.state.scheduler = init_scheduler()
        except Exception as e:
            logger.error(f"Failed to initialize scheduler: {e}")
            print(f"⚠️  Warning: Could not initialize scheduler: {e}")
        
        yield
        
        # Shutdown
        if hasattr(app.state, "scheduler"):
            app.state.scheduler.shutdown()
            logger.info("Scheduler shutdown successfully")
    
    app = FastAPI(
        title="Ride Surge Predictor API",
        description="API for predicting ride prices based on origin, destination, and datetime",
        version="1.0.0",
        lifespan=lifespan
    )
    
    @app.get("/health")
    def health_check():
        """Health check endpoint."""
        try:
            model_loaded = getattr(app.state, "model", None) is not None
            model_name = getattr(app.state, "model_name", "Unknown")
            scheduler_running = hasattr(app.state, "scheduler") and (getattr(app.state, "scheduler", None) is not None)
            
            return {
                "status": "ok",
                "model_loaded": model_loaded,
                "model_name": model_name,
                "scheduler_running": scheduler_running,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Health check error: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
    
    @app.get("/scheduler/jobs", response_model=list[SchedulerJob])
    def list_scheduler_jobs():
        """List all scheduled jobs."""
        if not hasattr(app.state, "scheduler"):
            raise HTTPException(status_code=503, detail="Scheduler not initialized")
        
        jobs = []
        for job in app.state.scheduler.get_jobs():
            jobs.append(SchedulerJob(
                id=job.id,
                name=job.name,
                next_run_time=job.next_run_time.isoformat() if job.next_run_time else None,
                trigger=str(job.trigger)
            ))
        return jobs
    
    @app.get("/scheduler/status")
    def scheduler_status():
        """Get scheduler status."""
        if not hasattr(app.state, "scheduler"):
            return {"status": "not_initialized"}
        
        scheduler = app.state.scheduler
        jobs = scheduler.get_jobs()
        
        return {
            "status": "running" if scheduler.running else "stopped",
            "jobs_count": len(jobs),
            "jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in jobs
            ]
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
    uvicorn.run(app, host="0.0.0.0", port=PORT)
