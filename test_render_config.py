#!/usr/bin/env python
"""
Quick test script to verify Render configuration
"""

import os
import sys

def test_render_config():
    """Test if Render configuration is working"""
    print("🧪 Testing Render Configuration...")

    # Set production settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'symplifika.production_settings')

    try:
        # Test Django import
        import django
        print(f"✅ Django {django.get_version()} imported successfully")

        # Setup Django
        django.setup()

        # Test settings
        from django.conf import settings
        print(f"✅ Settings loaded: {settings.SETTINGS_MODULE}")
        print(f"✅ DEBUG: {settings.DEBUG}")
        print(f"✅ Database: {settings.DATABASES['default']['ENGINE']}")

        # Test database connection
        from django.db import connections
        db_conn = connections['default']
        with db_conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                print("✅ Database connection successful")

        # Test static files configuration
        print(f"✅ Static files: {settings.STATICFILES_STORAGE}")

        # Test apps
        from django.apps import apps
        print(f"✅ Apps loaded: {len(apps.get_app_configs())} apps")

        print("\n🎉 All tests passed! Configuration is ready for Render.")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_render_config()
    sys.exit(0 if success else 1)
