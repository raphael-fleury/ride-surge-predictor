"""
Test script for the Ride Surge Predictor API
Run this after starting the server with: python main.py --server
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("=" * 60)
    print("Testing Health Check...")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("✅ Health check passed!\n")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}\n")
        return False

def test_prediction():
    """Test the prediction endpoint with sample data"""
    print("=" * 60)
    print("Testing Price Prediction...")
    print("=" * 60)
    
    # Test Case 1: São Paulo Downtown to Airport
    payload = {
        "origin": {
            "latitude": -23.5505,
            "longitude": -46.6333
        },
        "destination": {
            "latitude": -23.5565,
            "longitude": -46.6560
        },
        "datetime": "2024-05-23 14:30:00",
        "rideType": "uber_x",
        "temperature": 25.5,
        "precipitation": 0.0,
        "weatherCode": 0
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predict", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Request: {json.dumps(payload, indent=2)}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Prediction test passed!\n")
            return True
        else:
            print("❌ Prediction test failed!\n")
            return False
    except Exception as e:
        print(f"❌ Prediction test failed: {e}\n")
        return False

def test_multiple_scenarios():
    """Test multiple scenarios with different times and locations"""
    print("=" * 60)
    print("Testing Multiple Scenarios...")
    print("=" * 60)
    
    scenarios = [
        {
            "name": "Morning Rush Hour - Uber X",
            "payload": {
                "origin": {"latitude": -23.5505, "longitude": -46.6333},
                "destination": {"latitude": -23.5565, "longitude": -46.6560},
                "datetime": "2024-05-23 08:00:00",
                "rideType": "uber_x",
                "temperature": 22.0,
                "precipitation": 0.0,
                "weatherCode": 0
            }
        },
        {
            "name": "Evening Peak - Comfort",
            "payload": {
                "origin": {"latitude": -23.5505, "longitude": -46.6333},
                "destination": {"latitude": -23.5565, "longitude": -46.6560},
                "datetime": "2024-05-23 18:00:00",
                "rideType": "comfort",
                "temperature": 25.5,
                "precipitation": 0.0,
                "weatherCode": 80
            }
        },
        {
            "name": "Late Night - Uber Moto",
            "payload": {
                "origin": {"latitude": -23.5505, "longitude": -46.6333},
                "destination": {"latitude": -23.5565, "longitude": -46.6560},
                "datetime": "2024-05-23 23:00:00",
                "rideType": "uber_moto",
                "temperature": 20.0,
                "precipitation": 0.5,
                "weatherCode": 45
            }
        },
        {
            "name": "Weekend - Bag (Com bagagem)",
            "payload": {
                "origin": {"latitude": -23.5505, "longitude": -46.6333},
                "destination": {"latitude": -23.5565, "longitude": -46.6560},
                "datetime": "2024-05-25 10:00:00",
                "rideType": "bag",
                "temperature": 26.0,
                "precipitation": 0.0,
                "weatherCode": 1
            }
        },
        {
            "name": "Without Weather Data (Optional)",
            "payload": {
                "origin": {"latitude": -23.5505, "longitude": -46.6333},
                "destination": {"latitude": -23.5565, "longitude": -46.6560},
                "datetime": "2024-05-23 12:00:00",
                "rideType": "comfort"
            }
        }
    ]
    
    success_count = 0
    for scenario in scenarios:
        print(f"\n🧪 Scenario: {scenario['name']}")
        try:
            response = requests.post(f"{BASE_URL}/predict", json=scenario['payload'])
            if response.status_code == 200:
                data = response.json()
                print(f"   Predicted Price: R$ {data['predicted_price']:.2f}")
                print(f"   Model: {data['model_used']}")
                print(f"   Confidence: {data['confidence']}")
                print("   ✅ Success")
                success_count += 1
            else:
                print(f"   ❌ Error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 Results: {success_count}/{len(scenarios)} scenarios passed\n")
    return success_count == len(scenarios)

def main():
    """Run all tests"""
    print("\n")
    print("🚀 Starting API Tests...")
    print("Make sure the server is running: python main.py --server\n")
    
    results = {
        "health_check": test_health_check(),
        "prediction": test_prediction(),
        "multiple_scenarios": test_multiple_scenarios()
    }
    
    print("=" * 60)
    print("📈 Test Summary")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    all_passed = all(results.values())
    print("=" * 60)
    
    if all_passed:
        print("✨ All tests passed! API is working correctly.\n")
        return 0
    else:
        print("⚠️  Some tests failed. Check the errors above.\n")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
