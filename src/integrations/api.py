import os
import pandas as pd
import requests

API_URL = os.environ.get("API_URL", "https://standing-wombat-211.convex.site")
print(f"| API URL: {API_URL}")

def get_routes():
    """Fetches all available routes from the API."""
    try:
        response = requests.get(f"{API_URL}/routes")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"| Error fetching routes: {e}")
        return []

def get_rides():
    """Fetches all processed ride data from the API."""
    try:
        response = requests.get(f"{API_URL}/rides")
        response.raise_for_status()
        return [transform_ride(ride) for ride in response.json()]
    except requests.RequestException as e:
        print(f"| Error fetching rides: {e}")
        return []

def get_rides_by_route(route_id):
    """Fetches rides filtered by route from the API."""
    try:
        response = requests.get(f"{API_URL}/rides?routeId={route_id}")
        response.raise_for_status()
        return [transform_ride(ride) for ride in response.json()]
    except requests.RequestException as e:
        print(f"| Error fetching rides for route {route_id}: {e}")
        return []
    
    
def transform_ride(ride):
    timestamp_ms = ride.get('timestamp', 0)
    dt = pd.to_datetime(timestamp_ms, unit='ms')
    
    # Extract temporal features
    hour = dt.hour
    minute = dt.minute
    day_of_week = dt.dayofweek  # 0=Monday, 6=Sunday
    is_weekend = 1 if day_of_week >= 5 else 0
    
    # Create transformed record
    origin_name = ride.get("origin", {}).get("name", "")
    destination_name = ride.get("destination", {}).get("name", "")
    return {
        'timestamp': dt,
        'from': origin_name,
        'to': destination_name,
        'ride_id': ride.get('rideType', ''),
        'price': ride.get('price', 0),
        'wait_time_minutes': ride.get('waitTime', 0),
        'temperature_celsius': ride.get('temperature', 0),
        'precipitation_mm': ride.get('precipitation', 0),
        'weather_code': ride.get('weatherCode', 0),
        'hour': hour,
        'minute': minute,
        'day_of_week': day_of_week,
        'is_weekend': is_weekend,
        'route_name': f"{origin_name} -> {destination_name}"
    }
    