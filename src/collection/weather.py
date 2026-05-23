import requests

def get_current_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,precipitation,weather_code"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            current = data.get("current", {})
            return {
                "temperature": current.get("temperature_2m"),
                "precipitation": current.get("precipitation"),
                "weather_code": current.get("weather_code")
            }
    except Exception as e:
        print(f"| Error fetching weather data: {e}")
    return {"temperature": None, "precipitation": None, "weather_code": None}
