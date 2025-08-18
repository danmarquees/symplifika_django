#!/usr/bin/env python
"""
Integration test script to verify the duplicate handling works at the database level
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'symplifika.settings')
django.setup()

from django.contrib.auth.models import User
from shortcuts.models import Category
from users.models import UserProfile
from django.db import IntegrityError
import uuid

def test_database_constraints():
    """Test that database constraints are working"""
    print("🧪 Testing database level constraints...")

    # Generate unique username to avoid conflicts
    unique_id = str(uuid.uuid4())[:8]
    username = f'testuser_{unique_id}'
    email = f'test_{unique_id}@example.com'

    # Clean up any existing user with similar name (just in case)
    User.objects.filter(username=username).delete()

    # Create test user (UserProfile is created automatically via signal)
    user = User.objects.create_user(username, email, 'pass123')
    print(f"✅ Created test user: {user.username}")
    print(f"✅ User profile created automatically: {user.profile}")

    # Create first category
    cat1 = Category.objects.create(user=user, name='Test Category', description='First')
    print(f"✅ Created category 1: {cat1}")

    # Try to create duplicate (should raise IntegrityError)
    try:
        cat2 = Category.objects.create(user=user, name='Test Category', description='Duplicate')
        print(f"❌ ERROR: Duplicate category was created: {cat2}")
        user.delete()
        return False
    except IntegrityError as e:
        print(f"✅ IntegrityError caught correctly: {e}")

    # Clean up
    user.delete()
    print("✅ Test completed and cleaned up")
    return True

if __name__ == '__main__':
    print("🚀 Starting database constraint integration test...\n")

    try:
        success = test_database_constraints()

        if success:
            print("\n🎉 Database constraints are working correctly!")
        else:
            print("\n❌ Database constraint test failed!")
            sys.exit(1)

    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
