import time
import os
import datetime
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

from src.collection.uber_routes import get_uber_routes
from .weather import get_current_weather
from .auth import login_uber
from .parser import extract_rides_from_html
from .storage import save_to_csv

load_dotenv()

COOKIES_FILE = os.path.join(os.getcwd(), "config", "cookies.json")
INTERVAL_MINUTES = 15

def run_job(page, context):
    print(f"\nCycle started at {datetime.datetime.now().strftime('%H:%M:%S')}")
    
    for route in get_uber_routes():
        print(f"| Route: {route['origin']['name']} -> {route['destination']['name']}")
        try:
            weather_data = get_current_weather(route['origin']['lat'], route['origin']['lon'])
            print(f"|🌤️| Temp: {weather_data['temperature']}°C | Rain: {weather_data['precipitation']}mm")

            def start_point():
                page.goto(route['url'], timeout=60000)
                time.sleep(15)

            start_point()
            if "sign-in" in page.url or "login" in page.url:
                login_uber(page, context, COOKIES_FILE)
                start_point()

            page_content = page.content()
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            print("    -> Extracting data from DOM...")
            ride_data = extract_rides_from_html(page_content)
            
            if ride_data:
                save_to_csv(timestamp, route, weather_data, ride_data)
                print(f"    | Data extracted and appended to CSV.")
            else:
                print("    | Extraction failed or no target rides found.")
                
        except Exception as e:
            print(f"| Error communicating with browser: {e}")
        time.sleep(2)

def run_collection():
    print(f"Starting collection automation: Every {INTERVAL_MINUTES} minutes.")
        
    try:
        while True:
            start_time = time.time()
            
            print("\n[+] Launching browser for new cycle...")
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                iphone = p.devices['iPhone 13']
                if os.path.exists(COOKIES_FILE):
                    context = browser.new_context(**iphone, storage_state=COOKIES_FILE)
                else:
                    context = browser.new_context(**iphone)
                page = context.new_page()

                try:
                    run_job(page, context)
                except Exception as e:
                    print(f"\n[!] Error during run_job: {e}")
                finally:
                    browser.close()
                    print("[-] Browser closed to free memory.")
            
            elapsed = time.time() - start_time
            sleep_duration = max(0, (INTERVAL_MINUTES * 60) - elapsed)
            print(f"[#] Cycle complete. Sleeping {round(sleep_duration/60, 2)} minutes...")
            time.sleep(sleep_duration)
            
    except KeyboardInterrupt:
        print("\n[!] Script stopped.")
