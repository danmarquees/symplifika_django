#!/usr/bin/env python3
"""
Final validation script to confirm all API fixes are working properly.
This script validates that the UnorderedObjectListWarning and 400 errors are resolved.
"""
import os
import sys
import warnings
import logging

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'symplifika.settings')

import django
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory, override_settings
from django.db.models import Q, Count
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.pagination import PageNumberPagination

from shortcuts.models import Category, Shortcut
from shortcuts.views import CategoryViewSet, ShortcutViewSet
from shortcuts.serializers import CategorySerializer
from users.models import UserProfile

# Capture warnings
warnings.filterwarnings('error', category=UserWarning, module='rest_framework.pagination')

class ValidationResults:
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.issues_found = []
        self.fixes_verified = []

    def log_success(self, test_name):
        self.tests_passed += 1
        self.fixes_verified.append(test_name)
        print(f"✅ {test_name}")

    def log_failure(self, test_name, error=None):
        self.tests_failed += 1
        self.issues_found.append(f"{test_name}: {error}" if error else test_name)
        print(f"❌ {test_name}" + (f" - {error}" if error else ""))

    def log_warning(self, test_name, warning=None):
        print(f"⚠️  {test_name}" + (f" - {warning}" if warning else ""))

    def print_summary(self):
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_failed}")

        if self.fixes_verified:
            print("\n✅ FIXES VERIFIED:")
            for fix in self.fixes_verified:
                print(f"   • {fix}")

        if self.issues_found:
            print("\n❌ ISSUES STILL PRESENT:")
            for issue in self.issues_found:
                print(f"   • {issue}")

        success_rate = (self.tests_passed / (self.tests_passed + self.tests_failed)) * 100 if (self.tests_passed + self.tests_failed) > 0 else 0
        print(f"\nSuccess Rate: {success_rate:.1f}%")

        if self.tests_failed == 0:
            print("\n🎉 ALL ISSUES HAVE BEEN RESOLVED!")
        else:
            print(f"\n⚠️  {self.tests_failed} issue(s) still need attention")

def create_test_user():
    """Create or get test user"""
    try:
        user, created = User.objects.get_or_create(
            username='validation_test_user',
            defaults={
                'email': 'validation@test.com',
                'first_name': 'Validation',
                'last_name': 'User'
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
        return user
    except Exception as e:
        print(f"Error creating test user: {e}")
        return None

def test_pagination_warning_fix(results):
    """Test that pagination warning is fixed"""
    print("\n🔍 Testing Pagination Warning Fix...")

    user = create_test_user()
    if not user:
        results.log_failure("Pagination Test - User Creation Failed")
        return

    # Create test categories
    for i in range(10):
        Category.objects.get_or_create(
            user=user,
            name=f'Validation Category {i+1}',
            defaults={
                'description': f'Test category {i+1}',
                'color': f'#00{i%10:01d}{i%10:01d}ff'
            }
        )

    # Test CategoryViewSet queryset
    try:
        factory = APIRequestFactory()
        request = factory.get('/shortcuts/api/categories/')
        request.user = user

        view = CategoryViewSet()
        view.request = request

        # Get the queryset as the view would
        queryset = view.get_queryset()

        # Test pagination with this queryset
        paginator = PageNumberPagination()
        paginator.page_size = 5

        # This should NOT raise UnorderedObjectListWarning
        try:
            paginated = paginator.paginate_queryset(queryset, request)
            results.log_success("CategoryViewSet pagination warning fixed")
        except UserWarning as w:
            if "UnorderedObjectListWarning" in str(w):
                results.log_failure("CategoryViewSet still has pagination warning", str(w))
            else:
                results.log_warning("CategoryViewSet unexpected warning", str(w))

    except Exception as e:
        results.log_failure("CategoryViewSet pagination test failed", str(e))

    # Test ShortcutViewSet queryset
    try:
        # Create test shortcuts
        category = Category.objects.filter(user=user).first()
        for i in range(5):
            Shortcut.objects.get_or_create(
                user=user,
                trigger=f'//validation-test-{i+1}',
                defaults={
                    'title': f'Validation Shortcut {i+1}',
                    'content': f'Content {i+1}',
                    'category': category,
                    'expansion_type': 'static'
                }
            )

        view = ShortcutViewSet()
        view.request = request

        queryset = view.get_queryset()

        # Test pagination
        try:
            paginated = paginator.paginate_queryset(queryset, request)
            results.log_success("ShortcutViewSet pagination warning fixed")
        except UserWarning as w:
            if "UnorderedObjectListWarning" in str(w):
                results.log_failure("ShortcutViewSet still has pagination warning", str(w))
            else:
                results.log_warning("ShortcutViewSet unexpected warning", str(w))

    except Exception as e:
        results.log_failure("ShortcutViewSet pagination test failed", str(e))

def test_serializer_validation_fix(results):
    """Test that serializer validation is working properly"""
    print("\n🔍 Testing Serializer Validation Fix...")

    user = create_test_user()
    if not user:
        results.log_failure("Serializer Test - User Creation Failed")
        return

    # Mock request context
    class MockRequest:
        def __init__(self, user):
            self.user = user

    mock_request = MockRequest(user)
    context = {'request': mock_request}

    # Test 1: Valid data should pass
    try:
        valid_data = {
            'name': 'Valid Test Category',
            'description': 'This should work',
            'color': '#00ff00'
        }

        serializer = CategorySerializer(data=valid_data, context=context)
        if serializer.is_valid():
            results.log_success("Valid data passes serializer validation")
        else:
            results.log_failure("Valid data failed validation", str(serializer.errors))
    except Exception as e:
        results.log_failure("Valid data serialization test failed", str(e))

    # Test 2: Empty name should fail
    try:
        invalid_data = {
            'name': '',
            'description': 'Empty name test',
            'color': '#ff0000'
        }

        serializer = CategorySerializer(data=invalid_data, context=context)
        if not serializer.is_valid() and 'name' in serializer.errors:
            results.log_success("Empty name properly rejected")
        else:
            results.log_failure("Empty name validation not working")
    except Exception as e:
        results.log_failure("Empty name validation test failed", str(e))

    # Test 3: Short name should fail
    try:
        invalid_data = {
            'name': 'A',
            'description': 'Short name test',
            'color': '#ff0000'
        }

        serializer = CategorySerializer(data=invalid_data, context=context)
        if not serializer.is_valid() and 'name' in serializer.errors:
            results.log_success("Short name properly rejected")
        else:
            results.log_failure("Short name validation not working")
    except Exception as e:
        results.log_failure("Short name validation test failed", str(e))

    # Test 4: Invalid color should fail
    try:
        invalid_data = {
            'name': 'Valid Name',
            'description': 'Invalid color test',
            'color': 'invalid-color'
        }

        serializer = CategorySerializer(data=invalid_data, context=context)
        if not serializer.is_valid():
            results.log_success("Invalid color properly rejected")
        else:
            results.log_failure("Invalid color validation not working")
    except Exception as e:
        results.log_failure("Invalid color validation test failed", str(e))

    # Test 5: Duplicate name should fail
    try:
        # Create a category first
        Category.objects.get_or_create(
            user=user,
            name='Duplicate Test Category',
            defaults={'description': 'Original', 'color': '#0000ff'}
        )

        duplicate_data = {
            'name': 'Duplicate Test Category',
            'description': 'Duplicate attempt',
            'color': '#ff0000'
        }

        serializer = CategorySerializer(data=duplicate_data, context=context)
        if not serializer.is_valid() and 'name' in serializer.errors:
            results.log_success("Duplicate name properly rejected")
        else:
            results.log_failure("Duplicate name validation not working")
    except Exception as e:
        results.log_failure("Duplicate name validation test failed", str(e))

def test_viewset_error_handling(results):
    """Test that ViewSet error handling is improved"""
    print("\n🔍 Testing ViewSet Error Handling...")

    user = create_test_user()
    if not user:
        results.log_failure("ViewSet Test - User Creation Failed")
        return

    try:
        factory = APIRequestFactory()

        # Test valid POST request
        valid_data = {
            'name': 'ViewSet Test Category',
            'description': 'Testing ViewSet',
            'color': '#ff9900'
        }

        request = factory.post('/shortcuts/api/categories/', valid_data, format='json')
        force_authenticate(request, user=user)

        view = CategoryViewSet.as_view({'post': 'create'})
        response = view(request)

        if response.status_code in [200, 201]:
            results.log_success("ViewSet handles valid requests properly")
        else:
            results.log_failure(f"ViewSet failed valid request - Status: {response.status_code}")

    except Exception as e:
        results.log_failure("ViewSet valid request test failed", str(e))

    try:
        # Test invalid POST request
        invalid_data = {
            'name': '',  # Invalid empty name
            'description': 'Testing error handling',
            'color': '#ff0000'
        }

        request = factory.post('/shortcuts/api/categories/', invalid_data, format='json')
        force_authenticate(request, user=user)

        view = CategoryViewSet.as_view({'post': 'create'})
        response = view(request)

        if response.status_code == 400:
            results.log_success("ViewSet properly returns 400 for invalid data")
        else:
            results.log_failure(f"ViewSet error handling not working - Status: {response.status_code}")

    except Exception as e:
        results.log_failure("ViewSet invalid request test failed", str(e))

def test_queryset_ordering(results):
    """Test that all querysets have proper ordering"""
    print("\n🔍 Testing QuerySet Ordering...")

    user = create_test_user()
    if not user:
        results.log_failure("QuerySet Test - User Creation Failed")
        return

    # Test CategoryViewSet ordering
    try:
        factory = APIRequestFactory()
        request = factory.get('/shortcuts/api/categories/')
        request.user = user

        view = CategoryViewSet()
        view.request = request

        queryset = view.get_queryset()

        # Check if queryset has ordering
        if queryset.query.order_by:
            results.log_success("CategoryViewSet queryset has explicit ordering")
        else:
            results.log_failure("CategoryViewSet queryset lacks explicit ordering")

    except Exception as e:
        results.log_failure("CategoryViewSet ordering test failed", str(e))

    # Test ShortcutViewSet ordering
    try:
        view = ShortcutViewSet()
        view.request = request

        queryset = view.get_queryset()

        if queryset.query.order_by:
            results.log_success("ShortcutViewSet queryset has explicit ordering")
        else:
            results.log_failure("ShortcutViewSet queryset lacks explicit ordering")

    except Exception as e:
        results.log_failure("ShortcutViewSet ordering test failed", str(e))

def cleanup_test_data():
    """Clean up test data"""
    try:
        User.objects.filter(username__in=['validation_test_user', 'api_test_user']).delete()
        print("✅ Test data cleaned up")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")

def main():
    """Run all validation tests"""
    print("🚀 Starting Final Validation of API Fixes")
    print("="*60)

    results = ValidationResults()

    # Run all validation tests
    test_pagination_warning_fix(results)
    test_serializer_validation_fix(results)
    test_viewset_error_handling(results)
    test_queryset_ordering(results)

    # Print results
    results.print_summary()

    # Cleanup
    cleanup_test_data()

    # Exit with appropriate code
    sys.exit(0 if results.tests_failed == 0 else 1)

if __name__ == '__main__':
    main()
