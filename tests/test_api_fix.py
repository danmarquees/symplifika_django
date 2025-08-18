#!/usr/bin/env python
"""
HTTP API test to verify that the category duplicate handling works correctly.
This script makes actual HTTP requests to the running server to test the fix.
"""

import requests
import json
import sys
import time

# Base URL for the API
BASE_URL = "http://127.0.0.1:8000"

def create_test_user_and_login():
    """Create a test user and get authentication token"""
    print("🔐 Creating test user and logging in...")

    # Create user data
    user_data = {
        "username": "test_api_user",
        "email": "testapi@example.com",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    }

    # Try to register (might fail if user exists, that's okay)
    try:
        register_response = requests.post(f"{BASE_URL}/users/api/register/", json=user_data)
        if register_response.status_code == 201:
            print("✅ User created successfully")
        else:
            print("ℹ️  User might already exist, trying to login...")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on port 8000")
        return None

    # Login to get token
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"]
    }

    try:
        login_response = requests.post(f"{BASE_URL}/users/api/login/", json=login_data)
        if login_response.status_code == 200:
            token = login_response.json().get('access')
            print("✅ Login successful")
            return token
        else:
            print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
            return None
    except Exception as e:
        print(f"❌ Login request failed: {e}")
        return None

def test_category_duplicate_handling(token):
    """Test category duplicate handling via HTTP API"""
    print("\n🧪 Testing category duplicate handling via HTTP API...")

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # Test data
    category_data = {
        'name': 'API Test Category',
        'description': 'A test category created via API',
        'color': '#ff5722'
    }

    print("1️⃣  Creating first category via API...")

    # Create first category
    response = requests.post(f"{BASE_URL}/shortcuts/api/categories/",
                           json=category_data, headers=headers)

    if response.status_code == 201:
        print("✅ First category created successfully")
        created_category = response.json()
        print(f"   Category ID: {created_category['id']}")
        print(f"   Category name: {created_category['name']}")
        category_id = created_category['id']
    else:
        print(f"❌ Failed to create first category. Status: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

    print("\n2️⃣  Attempting to create duplicate category...")

    # Try to create duplicate
    response = requests.post(f"{BASE_URL}/shortcuts/api/categories/",
                           json=category_data, headers=headers)

    if response.status_code == 400:
        print("✅ Duplicate category properly rejected")
        error_data = response.json()
        print(f"   Error response: {error_data}")

        # Check if error message is about duplicates
        if 'name' in error_data:
            error_messages = error_data['name']
            if any('já existe' in str(msg).lower() or 'already exists' in str(msg).lower()
                   for msg in error_messages):
                print("✅ Error message correctly identifies duplicate name issue")
            else:
                print("⚠️  Error message might not be specific enough")
                print(f"   Messages: {error_messages}")

    elif response.status_code == 500:
        print("❌ Server error occurred - the fix didn't work!")
        print(f"   Response: {response.text}")
        return False
    else:
        print(f"❌ Unexpected response status: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

    print("\n3️⃣  Testing category with different name...")

    # Create category with different name
    different_category_data = {
        'name': 'Different API Test Category',
        'description': 'A different test category',
        'color': '#00ff00'
    }

    response = requests.post(f"{BASE_URL}/shortcuts/api/categories/",
                           json=different_category_data, headers=headers)

    if response.status_code == 201:
        print("✅ Category with different name created successfully")
        created_category = response.json()
        print(f"   Category ID: {created_category['id']}")
        print(f"   Category name: {created_category['name']}")
    else:
        print(f"❌ Failed to create category with different name. Status: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

    print("\n4️⃣  Testing update to duplicate name...")

    # Try to update the first category to have same name as second (should fail)
    update_data = {'name': 'Different API Test Category'}
    response = requests.patch(f"{BASE_URL}/shortcuts/api/categories/{category_id}/",
                            json=update_data, headers=headers)

    if response.status_code == 400:
        print("✅ Update to duplicate name properly rejected")
        error_data = response.json()
        print(f"   Error response: {error_data}")
    else:
        print(f"⚠️  Update response: {response.status_code} - {response.text}")

    return True

def test_shortcut_duplicate_handling(token):
    """Test shortcut duplicate handling via HTTP API"""
    print("\n🧪 Testing shortcut duplicate handling via HTTP API...")

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # Test data
    shortcut_data = {
        'trigger': '//apitest',
        'title': 'API Test Shortcut',
        'content': 'This is a test shortcut created via API',
        'expansion_type': 'static'
    }

    print("1️⃣  Creating first shortcut via API...")

    # Create first shortcut
    response = requests.post(f"{BASE_URL}/shortcuts/api/shortcuts/",
                           json=shortcut_data, headers=headers)

    if response.status_code == 201:
        print("✅ First shortcut created successfully")
        created_shortcut = response.json()
        print(f"   Shortcut ID: {created_shortcut['id']}")
        print(f"   Shortcut trigger: {created_shortcut['trigger']}")
    else:
        print(f"❌ Failed to create first shortcut. Status: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

    print("\n2️⃣  Attempting to create duplicate shortcut...")

    # Try to create duplicate
    response = requests.post(f"{BASE_URL}/shortcuts/api/shortcuts/",
                           json=shortcut_data, headers=headers)

    if response.status_code == 400:
        print("✅ Duplicate shortcut properly rejected")
        error_data = response.json()
        print(f"   Error response: {error_data}")
    elif response.status_code == 500:
        print("❌ Server error occurred - the shortcut fix didn't work!")
        print(f"   Response: {response.text}")
        return False
    else:
        print(f"❌ Unexpected response status: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

    return True

def cleanup_test_data(token):
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    try:
        # Get all categories and delete them
        response = requests.get(f"{BASE_URL}/shortcuts/api/categories/", headers=headers)
        if response.status_code == 200:
            categories = response.json().get('results', [])
            for category in categories:
                if 'API Test' in category['name']:
                    delete_response = requests.delete(
                        f"{BASE_URL}/shortcuts/api/categories/{category['id']}/",
                        headers=headers
                    )
                    if delete_response.status_code == 204:
                        print(f"   ✅ Deleted category: {category['name']}")

        # Get all shortcuts and delete them
        response = requests.get(f"{BASE_URL}/shortcuts/api/shortcuts/", headers=headers)
        if response.status_code == 200:
            shortcuts = response.json().get('results', [])
            for shortcut in shortcuts:
                if shortcut['trigger'] == '//apitest':
                    delete_response = requests.delete(
                        f"{BASE_URL}/shortcuts/api/shortcuts/{shortcut['id']}/",
                        headers=headers
                    )
                    if delete_response.status_code == 204:
                        print(f"   ✅ Deleted shortcut: {shortcut['trigger']}")

        print("✅ Cleanup completed")

    except Exception as e:
        print(f"⚠️  Cleanup failed: {e}")

def main():
    """Main test function"""
    print("🚀 Starting HTTP API duplicate handling tests...\n")

    # Create user and login
    token = create_test_user_and_login()
    if not token:
        print("❌ Failed to authenticate. Exiting.")
        sys.exit(1)

    try:
        # Run tests
        category_success = test_category_duplicate_handling(token)
        shortcut_success = test_shortcut_duplicate_handling(token)

        # Cleanup
        cleanup_test_data(token)

        # Results
        if category_success and shortcut_success:
            print("\n🎉 All HTTP API tests passed! The duplicate handling fix is working correctly.")
        else:
            print("\n❌ Some tests failed. Please check the implementation.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        cleanup_test_data(token) if token else None
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Tests failed with exception: {e}")
        import traceback
        traceback.print_exc()
        cleanup_test_data(token) if token else None
        sys.exit(1)

if __name__ == '__main__':
    main()
