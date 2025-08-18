#!/usr/bin/env python3
"""
Test script to reproduce API issues using requests library
"""
import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_categories_api():
    """Test Categories API endpoints"""
    print("🔍 Testing Categories API...")

    # Test GET request
    print("\n1. Testing GET /shortcuts/api/categories/")
    try:
        response = requests.get(f"{BASE_URL}/shortcuts/api/categories/")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")

        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error Response: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

    # Test POST request - Valid data
    print("\n2. Testing POST /shortcuts/api/categories/ - Valid Data")
    valid_data = {
        "name": "Test Category API",
        "description": "Testing category creation via API",
        "color": "#ff6600"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/shortcuts/api/categories/",
            json=valid_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

    # Test POST request - Invalid data (empty name)
    print("\n3. Testing POST /shortcuts/api/categories/ - Invalid Data")
    invalid_data = {
        "name": "",
        "description": "Empty name test",
        "color": "#ff0000"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/shortcuts/api/categories/",
            json=invalid_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

    # Test POST request - Missing required field
    print("\n4. Testing POST /shortcuts/api/categories/ - Missing Name")
    missing_data = {
        "description": "Missing name field",
        "color": "#00ff00"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/shortcuts/api/categories/",
            json=missing_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

    # Test POST request - No authentication (if applicable)
    print("\n5. Testing POST /shortcuts/api/categories/ - No Auth")
    try:
        # Make request without session/auth
        response = requests.post(
            f"{BASE_URL}/shortcuts/api/categories/",
            json=valid_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")


def test_with_authentication():
    """Test with proper Django session authentication"""
    print("\n🔐 Testing with Authentication...")

    session = requests.Session()

    # Get CSRF token first
    print("Getting CSRF token...")
    try:
        response = session.get(f"{BASE_URL}/admin/login/")
        csrf_token = None

        if 'csrftoken' in session.cookies:
            csrf_token = session.cookies['csrftoken']
            print(f"CSRF Token: {csrf_token}")
        else:
            print("No CSRF token found")
    except Exception as e:
        print(f"CSRF request failed: {e}")
        return

    # Try to authenticate (this would require a login endpoint)
    print("\nTesting authenticated requests...")

    headers = {
        'Content-Type': 'application/json',
        'Referer': f"{BASE_URL}/",
    }

    if csrf_token:
        headers['X-CSRFToken'] = csrf_token

    # Test authenticated POST
    test_data = {
        "name": "Authenticated Test Category",
        "description": "Testing with authentication",
        "color": "#0066ff"
    }

    try:
        response = session.post(
            f"{BASE_URL}/shortcuts/api/categories/",
            json=test_data,
            headers=headers
        )
        print(f"Authenticated POST Status: {response.status_code}")
        print(f"Authenticated POST Response: {response.text}")
    except Exception as e:
        print(f"Authenticated request failed: {e}")


def test_server_connection():
    """Test if server is running"""
    print("🔌 Testing server connection...")

    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"Server Status: {response.status_code}")
        print("✅ Server is running")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running or not accessible")
        print(f"Make sure Django server is running on {BASE_URL}")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False


def main():
    print("🚀 Starting API Request Tests")
    print("=" * 50)

    # Check server connection first
    if not test_server_connection():
        print("\n⚠️  Please start the Django server with:")
        print("python manage.py runserver 8000")
        sys.exit(1)

    # Test categories API
    test_categories_api()

    # Test with authentication
    test_with_authentication()

    print("\n🏁 Tests completed!")
    print("\nTo reproduce the exact errors from the logs:")
    print("1. Start Django server: python manage.py runserver")
    print("2. Run this script while server is running")
    print("3. Check server logs for the UnorderedObjectListWarning and 400 errors")


if __name__ == "__main__":
    main()
