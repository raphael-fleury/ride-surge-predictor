import os
import pandas as pd
import requests
from src.env import CONVEX_URL

def get_routes():
    """Fetches all available routes from the API."""
    try:
        response = requests.get(f"{CONVEX_URL}/routes")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"| Error fetching routes: {e}")
        return []

def get_rides():
    """Fetches all processed ride data from the API."""
    try:
        response = requests.get(f"{CONVEX_URL}/rides?rideType=uber_x")
        response.raise_for_status()
        return [transform_ride(ride) for ride in response.json()]
    except requests.RequestException as e:
        print(f"| Error fetching rides: {e}")
        return []

def get_rides_by_route(route_id):
    """Fetches rides filtered by route from the API."""
    try:
        response = requests.get(f"{CONVEX_URL}/rides?routeId={route_id}")
        response.raise_for_status()
        return [transform_ride(ride) for ride in response.json()]
    except requests.RequestException as e:
        print(f"| Error fetching rides for route {route_id}: {e}")
        return []
    
    
def transform_ride(ride):
    timestamp_ms = ride.get('timestamp', 0)
    dt = pd.to_datetime(timestamp_ms, unit='ms')

    origin_name = ride.get("origin", {}).get("name", "")
    destination_name = ride.get("destination", {}).get("name", "")
    return {
        'timestamp': dt,
        'from': origin_name,
        'to': destination_name,
        'route_id': ride.get('route', ''),
        'distance_m': ride.get('distance', 0),
        'estimated_time_s': ride.get('duration', 0),
        'ride_id': ride.get('rideType', ''),
        'price': ride.get('price', 0),
        'wait_time_minutes': ride.get('waitTime', 0),
        'temperature_celsius': ride.get('temperature', 0),
        'precipitation_mm': ride.get('precipitation', 0),
        'weather_code': ride.get('weatherCode', 0)
    }


def save_ride(route_id, timestamp, ride_type, price, wait_time, temperature, precipitation, weather_code):
    """
    Saves a ride to the API.
    
    Args:
        route_id: Route identifier
        timestamp: Unix timestamp in milliseconds
        ride_type: Type of ride (e.g., 'UberX', 'UberXL')
        price: Ride price
        wait_time: Waiting time in minutes
        temperature: Temperature in Celsius
        precipitation: Precipitation in mm
        weather_code: Weather code (0-100)
        
    Returns:
        Response status (201 for success, or error details)
    """
    try:
        payload = {
            "route": route_id,
            "timestamp": timestamp,
            "rideType": ride_type,
            "price": price,
            "waitTime": wait_time,
            "temperature": temperature,
            "precipitation": precipitation,
            "weatherCode": weather_code
        }
        
        response = requests.post(f"{CONVEX_URL}/rides", json=payload)
        response.raise_for_status()
        return {"status": 201, "message": "Ride saved successfully"}
    except requests.RequestException as e:
        print(f"| Error saving ride: {e}")
        return {"status": response.status_code if 'response' in locals() else 500, "error": str(e)}
    