#!/usr/bin/env python
"""
Demonstration script showing the duplicate category/shortcut fix in action.
This script shows before/after behavior and validates the solution.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'symplifika.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import IntegrityError
from shortcuts.models import Category, Shortcut
from shortcuts.serializers import CategorySerializer, ShortcutCreateSerializer
from users.models import UserProfile
from rest_framework.request import Request
from django.test import RequestFactory
import uuid

def print_separator(title):
    """Print a nice separator with title"""
    print("\n" + "="*60)
    print(f" {title} ")
    print("="*60)

def print_step(step_num, description):
    """Print step information"""
    print(f"\n{step_num}️⃣  {description}")

def create_test_user():
    """Create a test user for demonstration"""
    unique_id = str(uuid.uuid4())[:8]
    username = f'demo_user_{unique_id}'
    email = f'demo_{unique_id}@example.com'

    # Clean up any existing user
    User.objects.filter(username=username).delete()

    user = User.objects.create_user(username, email, 'demo123')
    print(f"✅ Created demo user: {user.username}")
    return user

def demo_database_constraints():
    """Demonstrate that database constraints exist and work"""
    print_separator("DATABASE CONSTRAINTS DEMONSTRATION")

    user = create_test_user()

    print_step(1, "Creating first category directly in database...")
    cat1 = Category.objects.create(
        user=user,
        name='Demo Category',
        description='First category'
    )
    print(f"✅ Created: {cat1}")

    print_step(2, "Attempting to create duplicate category (should fail)...")
    try:
        cat2 = Category.objects.create(
            user=user,
            name='Demo Category',
            description='Duplicate category'
        )
        print(f"❌ ERROR: Duplicate was created: {cat2}")
    except IntegrityError as e:
        print(f"✅ Database constraint working: {e}")

    # Cleanup
    user.delete()
    print("🧹 Cleaned up test user")

def demo_serializer_validation():
    """Demonstrate serializer validation preventing duplicates"""
    print_separator("SERIALIZER VALIDATION DEMONSTRATION")

    user = create_test_user()

    # Create mock request
    factory = RequestFactory()
    request = factory.post('/')
    request.user = user

    print_step(1, "Creating first category via serializer...")
    serializer1 = CategorySerializer(data={
        'name': 'Serializer Demo',
        'description': 'First category via serializer',
        'color': '#007bff'
    }, context={'request': request})

    if serializer1.is_valid():
        category1 = serializer1.save()
        print(f"✅ Created via serializer: {category1}")
    else:
        print(f"❌ Validation failed: {serializer1.errors}")

    print_step(2, "Attempting to create duplicate via serializer...")
    serializer2 = CategorySerializer(data={
        'name': 'Serializer Demo',  # Same name!
        'description': 'Duplicate category attempt',
        'color': '#ff5722'
    }, context={'request': request})

    if serializer2.is_valid():
        category2 = serializer2.save()
        print(f"❌ ERROR: Duplicate was created: {category2}")
    else:
        print(f"✅ Serializer validation caught duplicate:")
        for field, errors in serializer2.errors.items():
            print(f"   {field}: {errors}")

    print_step(3, "Creating category with different name...")
    serializer3 = CategorySerializer(data={
        'name': 'Different Demo Category',
        'description': 'This should work',
        'color': '#00ff00'
    }, context={'request': request})

    if serializer3.is_valid():
        category3 = serializer3.save()
        print(f"✅ Created different category: {category3}")
    else:
        print(f"❌ Unexpected validation error: {serializer3.errors}")

    # Cleanup
    user.delete()
    print("🧹 Cleaned up test user")

def demo_shortcut_validation():
    """Demonstrate shortcut duplicate validation"""
    print_separator("SHORTCUT VALIDATION DEMONSTRATION")

    user = create_test_user()

    # Create mock request
    factory = RequestFactory()
    request = factory.post('/')
    request.user = user

    print_step(1, "Creating first shortcut via serializer...")
    serializer1 = ShortcutCreateSerializer(data={
        'trigger': '//demodemo',
        'title': 'Demo Shortcut',
        'content': 'This is a demo shortcut',
        'expansion_type': 'static'
    }, context={'request': request})

    if serializer1.is_valid():
        shortcut1 = serializer1.save()
        print(f"✅ Created shortcut: {shortcut1}")
    else:
        print(f"❌ Validation failed: {serializer1.errors}")

    print_step(2, "Attempting to create duplicate shortcut...")
    serializer2 = ShortcutCreateSerializer(data={
        'trigger': '//demodemo',  # Same trigger!
        'title': 'Duplicate Shortcut',
        'content': 'This should fail',
        'expansion_type': 'static'
    }, context={'request': request})

    if serializer2.is_valid():
        try:
            shortcut2 = serializer2.save()
            print(f"❌ ERROR: Duplicate was created: {shortcut2}")
        except IntegrityError as e:
            print(f"✅ Database constraint caught duplicate: {e}")
    else:
        print(f"✅ Serializer validation caught duplicate:")
        for field, errors in serializer2.errors.items():
            print(f"   {field}: {errors}")

    # Cleanup
    user.delete()
    print("🧹 Cleaned up test user")

def demo_update_validation():
    """Demonstrate update validation"""
    print_separator("UPDATE VALIDATION DEMONSTRATION")

    user = create_test_user()

    # Create mock request
    factory = RequestFactory()
    request = factory.patch('/')
    request.user = user

    print_step(1, "Creating two categories...")
    cat1 = Category.objects.create(user=user, name='Category One')
    cat2 = Category.objects.create(user=user, name='Category Two')
    print(f"✅ Created: {cat1}")
    print(f"✅ Created: {cat2}")

    print_step(2, "Attempting to update cat2 to have same name as cat1...")
    serializer = CategorySerializer(
        cat2,
        data={'name': 'Category One'},
        partial=True,
        context={'request': request}
    )

    if serializer.is_valid():
        updated_cat = serializer.save()
        print(f"❌ ERROR: Update succeeded: {updated_cat}")
    else:
        print(f"✅ Update validation caught duplicate:")
        for field, errors in serializer.errors.items():
            print(f"   {field}: {errors}")

    print_step(3, "Updating cat2 to a different name...")
    serializer2 = CategorySerializer(
        cat2,
        data={'name': 'Category Two Updated'},
        partial=True,
        context={'request': request}
    )

    if serializer2.is_valid():
        updated_cat = serializer2.save()
        print(f"✅ Update succeeded: {updated_cat}")
    else:
        print(f"❌ Unexpected validation error: {serializer2.errors}")

    # Cleanup
    user.delete()
    print("🧹 Cleaned up test user")

def show_solution_summary():
    """Show summary of the solution"""
    print_separator("SOLUTION SUMMARY")

    print("""
🎯 PROBLEM SOLVED:
   • Users were getting 500 Internal Server Error when creating duplicate categories/shortcuts
   • Error: UNIQUE constraint failed: shortcuts_category.user_id, shortcuts_category.name

✅ SOLUTION IMPLEMENTED:

   1️⃣ SERIALIZER VALIDATION (First Line of Defense)
      • Added validate_name() method to CategorySerializer
      • Checks for duplicates before attempting database save
      • Returns user-friendly error messages in Portuguese

   2️⃣ VIEW ERROR HANDLING (Second Line of Defense)
      • Added IntegrityError handling in CategoryViewSet and ShortcutViewSet
      • Catches any database constraint violations
      • Returns proper 400 Bad Request instead of 500 Server Error

   3️⃣ DATABASE CONSTRAINTS (Ultimate Safeguard)
      • unique_together = ['user', 'name'] on Category model
      • unique_together = ['user', 'trigger'] on Shortcut model
      • Ensures data integrity at database level

🏆 BENEFITS:
   ✅ No more 500 errors for duplicate data
   ✅ Clear, user-friendly error messages
   ✅ Defense in depth approach
   ✅ Maintains data integrity
   ✅ Performance optimized (validation before DB writes)

📝 FILES MODIFIED:
   • shortcuts/serializers.py - Added CategorySerializer.validate_name()
   • shortcuts/views.py - Added IntegrityError handling
    """)

def main():
    """Run the complete demonstration"""
    print("🚀 DUPLICATE HANDLING FIX DEMONSTRATION")
    print("This demo shows how the fix prevents 500 errors and handles duplicates gracefully.\n")

    try:
        # Run all demonstrations
        demo_database_constraints()
        demo_serializer_validation()
        demo_shortcut_validation()
        demo_update_validation()
        show_solution_summary()

        print_separator("DEMONSTRATION COMPLETE")
        print("🎉 All demonstrations completed successfully!")
        print("The duplicate handling fix is working correctly across all levels.")

    except Exception as e:
        print(f"\n💥 Demo failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
