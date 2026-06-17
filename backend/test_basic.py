#!/usr/bin/env python3
"""
Basic API test script that works without API keys
"""
import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_basic_endpoints():
    """Test basic endpoints that don't require API keys"""
    print("🧪 Testing Basic API Endpoints")
    print("=" * 50)
    
    # Test root endpoint
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ Root endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
    
    print()
    
    # Test API documentation
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        print(f"✅ API Docs: {response.status_code}")
        if response.status_code == 200:
            print("   📚 Swagger UI available at http://localhost:8001/docs")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ API Docs failed: {e}")
    
    print()
    
    # Test OpenAPI spec
    try:
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        print(f"✅ OpenAPI Spec: {response.status_code}")
        if response.status_code == 200:
            spec = response.json()
            print(f"   API Title: {spec.get('info', {}).get('title', 'Unknown')}")
            print(f"   API Version: {spec.get('info', {}).get('version', 'Unknown')}")
            print(f"   Available Endpoints: {len(spec.get('paths', {}))}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ OpenAPI Spec failed: {e}")
    
    print()
    
    # Test health endpoint (will fail without API keys, but that's expected)
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"🔍 Health endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Expected failure (no API keys): {response.text}")
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
    
    print()
    print("=" * 50)
    print("📝 Next Steps:")
    print("1. Create .env file: cp env.example .env")
    print("2. Add your API keys to .env file")
    print("3. Restart the server")
    print("4. Run: python test_api.py")

if __name__ == "__main__":
    test_basic_endpoints()
