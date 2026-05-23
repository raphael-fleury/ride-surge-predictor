import json
import urllib.parse

from src.integrations.api import get_routes

def get_uber_routes():
    return [transform_route(route) for route in get_routes()]

def transform_route(route_data):
    """
    Transforma rota para formato com URL do Uber.
    
    Args:
        route_data: Dicionário com origem, destino e IDs
        
    Returns:
        Dicionário com 'from', 'to' e 'url'
    """
    origin = route_data.get("origin", {})
    destination = route_data.get("destination", {})
    
    # Constrói parâmetros para URL do Uber
    drop_param = {
        "addressLine1": destination.get("name", ""),
        "addressLine2": destination.get("display_name", "").split(",", 1)[1].strip() if "," in destination.get("display_name", "") else "",
        "id": destination.get("place_id", ""),
        "source": "SEARCH",
        "latitude": float(destination.get("lat", 0)),
        "longitude": float(destination.get("lon", 0)),
        "provider": "uber_places"
    }
    
    pickup_param = {
        "addressLine1": origin.get("name", ""),
        "addressLine2": origin.get("display_name", "").split(",", 1)[1].strip() if "," in origin.get("display_name", "") else "",
        "id": origin.get("place_id", ""),
        "source": "MANUAL",
        "latitude": float(origin.get("lat", 0)),
        "longitude": float(origin.get("lon", 0)),
        "provider": "uber_places"
    }
    
    # Codifica parâmetros
    drop_encoded = urllib.parse.quote(json.dumps(drop_param))
    pickup_encoded = urllib.parse.quote(json.dumps(pickup_param))
    
    # Constrói URL
    base_url = "https://m.uber.com/go/product-selection"
    url = f"{base_url}?drop%5B0%5D={drop_encoded}&pickup={pickup_encoded}&vehicle=10000294"
    
    return {
        "origin": {
            "name": origin.get("name", ""),
            "display_name": origin.get("display_name", ""),
            "lat": origin.get("lat", ""),
            "lon": origin.get("lon", "")
        },
        "destination": {
            "name": destination.get("name", ""),
            "display_name": destination.get("display_name", ""),
            "lat": destination.get("lat", ""),
            "lon": destination.get("lon", "")
        },
        "url": url
    }
