import os
import csv

INTERIM_DIR = os.path.join(os.getcwd(), "data", "interim")
CSV_FILE = os.path.join(INTERIM_DIR, "uber_rides_log.csv")

def save_to_csv(timestamp, route_info, weather_data, ride_data):
    file_exists = os.path.isfile(CSV_FILE)
    
    # Garantir que a pasta interim existe
    os.makedirs(INTERIM_DIR, exist_ok=True)
    
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'from', 'to', 'ride_id', 'price', 'wait_time_minutes', 'temperature_celsius', 'precipitation_mm', 'weather_code'])
        for item in ride_data:
            writer.writerow([
                timestamp,
                route_info.get('from', ''),
                route_info.get('to', ''),
                item.get('ride_id'),
                item.get('price'),
                item.get('wait_time_minutes'),
                weather_data.get('temperature'),
                weather_data.get('precipitation'),
                weather_data.get('weather_code')
            ])
