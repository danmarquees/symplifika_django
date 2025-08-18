#!/usr/bin/env python
"""
Test script to verify that the category duplicate handling works correctly.
This script uses Django's testing framework to ensure IntegrityError is handled properly.
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'symplifika.settings')
django.setup()

from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from shortcuts.models import Category, Shortcut
from users.models import UserProfile


@override_settings(ALLOWED_HOSTS=['testserver'])
class CategoryDuplicateTest(APITestCase):
    """Test category duplicate handling"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create user profile if it doesn't exist
        if not hasattr(self.user, 'profile'):
            UserProfile.objects.create(user=self.user)

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_category_success(self):
        """Test creating a category successfully"""
        data = {
            'name': 'Test Category',
            'description': 'A test category',
            'color': '#ff5722'
        }

        response = self.client.post('/shortcuts/api/categories/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Test Category')

    def test_create_duplicate_category_fails(self):
        """Test that creating a duplicate category fails gracefully"""
        # Create first category
        data = {
            'name': 'Duplicate Test',
            'description': 'First category',
            'color': '#ff5722'
        }

        response = self.client.post('/shortcuts/api/categories/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Try to create duplicate
        duplicate_data = {
            'name': 'Duplicate Test',
            'description': 'Second category with same name',
            'color': '#00ff00'
        }

        response = self.client.post('/shortcuts/api/categories/', duplicate_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_update_category_to_duplicate_name_fails(self):
        """Test that updating a category to a duplicate name fails"""
        # Create two categories
        cat1 = Category.objects.create(user=self.user, name='Category 1')
        cat2 = Category.objects.create(user=self.user, name='Category 2')

        # Try to update cat2 to have the same name as cat1
        data = {'name': 'Category 1'}

        response = self.client.patch(f'/shortcuts/api/categories/{cat2.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)


@override_settings(ALLOWED_HOSTS=['testserver'])
class ShortcutDuplicateTest(APITestCase):
    """Test shortcut duplicate handling"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create user profile if it doesn't exist
        if not hasattr(self.user, 'profile'):
            UserProfile.objects.create(user=self.user)

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_shortcut_success(self):
        """Test creating a shortcut successfully"""
        data = {
            'trigger': '//test',
            'title': 'Test Shortcut',
            'content': 'This is a test shortcut',
            'expansion_type': 'static'
        }

        response = self.client.post('/shortcuts/api/shortcuts/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['trigger'], '//test')

    def test_create_duplicate_shortcut_fails(self):
        """Test that creating a duplicate shortcut fails gracefully"""
        # Create first shortcut
        data = {
            'trigger': '//duplicate',
            'title': 'First Shortcut',
            'content': 'First content',
            'expansion_type': 'static'
        }

        response = self.client.post('/shortcuts/api/shortcuts/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Try to create duplicate
        duplicate_data = {
            'trigger': '//duplicate',
            'title': 'Second Shortcut',
            'content': 'Second content',
            'expansion_type': 'static'
        }

        response = self.client.post('/shortcuts/api/shortcuts/', duplicate_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('trigger', response.data)


def run_tests():
    """Run the tests programmatically"""
    import unittest

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(CategoryDuplicateTest))
    suite.addTests(loader.loadTestsFromTestCase(ShortcutDuplicateTest))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    print("🚀 Starting category and shortcut duplicate handling tests...\n")

    try:
        success = run_tests()

        if success:
            print("\n🎉 All tests passed! The duplicate handling fix is working correctly.")
        else:
            print("\n❌ Some tests failed. Please check the implementation.")
            sys.exit(1)

    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
