#!/usr/bin/env python
"""
Simple test script to verify the UserSettingsForm works correctly
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'symplifika.settings')
django.setup()

def test_user_settings_form():
    """Test the UserSettingsForm"""
    try:
        from core.forms import UserSettingsForm
        from django.contrib.auth.models import User
        from users.models import UserProfile
        
        print("✅ Successfully imported UserSettingsForm")
        
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        # Ensure user has a profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        print("✅ Test user and profile created/retrieved")
        
        # Test form instantiation
        form = UserSettingsForm(instance=profile, user=user)
        print("✅ Form instantiated successfully")
        
        # Check form fields
        expected_fields = ['first_name', 'last_name', 'email', 'ai_model_preference', 'theme', 'email_notifications', 'ai_enabled']
        actual_fields = list(form.fields.keys())
        
        print(f"Form fields: {actual_fields}")
        
        # Check if all expected fields are present
        missing_fields = set(expected_fields) - set(actual_fields)
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
        else:
            print("✅ All expected fields are present")
        
        # Test form validation with valid data
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'ai_model_preference': 'gpt-3.5-turbo',
            'theme': 'auto',
            'email_notifications': True,
            'ai_enabled': True
        }
        
        form = UserSettingsForm(data=form_data, instance=profile, user=user)
        if form.is_valid():
            print("✅ Form validation passed")
            
            # Test saving
            saved_profile = form.save()
            print("✅ Form saved successfully")
            print(f"Saved AI model preference: {saved_profile.ai_model_preference}")
            
        else:
            print(f"❌ Form validation failed: {form.errors}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_user_settings_form()
    sys.exit(0 if success else 1)
