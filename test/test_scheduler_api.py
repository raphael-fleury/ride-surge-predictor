"""
Test script to monitor the scheduler via API endpoints.
Run the API server first: python main.py --server

Then test the scheduler endpoints:
    python test_scheduler_api.py
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint."""
    print("📋 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        data = response.json()
        print(f"✅ Health Status: {data['status']}")
        print(f"   Model Loaded: {data['model_loaded']}")
        print(f"   Timestamp: {data['timestamp']}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_scheduler_status():
    """Test scheduler status endpoint."""
    print("\n⏰ Testing Scheduler Status...")
    try:
        response = requests.get(f"{BASE_URL}/scheduler/status")
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Scheduler Status: {data['status']}")
        print(f"   Jobs Running: {data['jobs_count']}")
        
        if data['jobs']:
            print("\n   Scheduled Jobs:")
            for job in data['jobs']:
                print(f"   - {job['name']} (ID: {job['id']})")
                print(f"     Next Run: {job['next_run']}")
        
        return True
    except Exception as e:
        print(f"❌ Scheduler status check failed: {e}")
        return False

def test_scheduler_jobs():
    """Test scheduler jobs endpoint."""
    print("\n📊 Testing Scheduler Jobs Details...")
    try:
        response = requests.get(f"{BASE_URL}/scheduler/jobs")
        response.raise_for_status()
        jobs = response.json()
        
        print(f"✅ Found {len(jobs)} scheduled jobs:\n")
        
        for job in jobs:
            print(f"   Job ID: {job['id']}")
            print(f"   Name: {job['name']}")
            print(f"   Trigger: {job['trigger']}")
            print(f"   Next Run: {job['next_run_time'] or 'Not scheduled'}")
            print()
        
        return True
    except Exception as e:
        print(f"❌ Scheduler jobs check failed: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 Ride Surge Predictor - Scheduler API Tests")
    print("="*60)
    
    # Test endpoints
    results = [
        ("Health Check", test_health()),
        ("Scheduler Status", test_scheduler_status()),
        ("Scheduler Jobs", test_scheduler_jobs()),
    ]
    
    # Summary
    print("\n" + "="*60)
    print("📈 Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed\n")
    
    if passed == total:
        print("🎉 All tests passed! Scheduler is running correctly.")
    else:
        print("⚠️  Some tests failed. Check the API server logs.")

if __name__ == "__main__":
    main()
