import re
from bs4 import BeautifulSoup

def extract_rides_from_html(html_content):
    """Parses local Uber HTML using BeautifulSoup."""
    soup = BeautifulSoup(html_content, "html.parser")
    extracted_data = []
    
    currency_elements = soup.find_all(string=re.compile(r'R?\$'))
    seen_prices = set()
    
    for el in currency_elements:
        text = el.text.strip()
        price_match = re.search(r'(R?\$)\s*(\d+[.,]\d+)', text)
        if price_match:
            price_val = float(price_match.group(2).replace(',', '.'))
            
            parent = el.find_parent('div')
            for _ in range(3):
                if parent and parent.parent:
                    parent = parent.parent
                else: break
            
            if not parent: continue
            
            block_text = parent.get_text(separator=' | ').lower()
            
            ride_id = "unknown"
            if 'bag' in block_text: ride_id = "bag"
            elif 'uberx' in block_text or 'uber x' in block_text: ride_id = "uber_x"
            elif 'moto' in block_text: ride_id = "uber_moto"
            elif 'comfort' in block_text: ride_id = "comfort"
            elif 'black' in block_text: ride_id = "black"
            
            if ride_id == "unknown":
                continue
                
            wait_time = 0
            wait_match = re.search(r'(\d+)\s*(min|mins)', block_text)
            if wait_match:
                wait_time = int(wait_match.group(1))
                
            sig = f"{ride_id}-{price_val}"
            if sig not in seen_prices:
                seen_prices.add(sig)
                extracted_data.append({
                    "ride_id": ride_id,
                    "price": price_val,
                    "wait_time_minutes": wait_time
                })
                
    return extracted_data
