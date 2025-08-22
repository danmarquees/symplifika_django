#!/usr/bin/env python
"""
Simple build verification script
"""
import os
import sys

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'symplifika.production_settings')

try:
    import django
    django.setup()

    from django.conf import settings
    from django.db import connections

    print("✅ Django setup successful")
    print(f"✅ Database engine: {settings.DATABASES['default']['ENGINE']}")
    print(f"✅ DEBUG: {settings.DEBUG}")

    # Test database connection
    db_conn = connections['default']
    with db_conn.cursor() as cursor:
        cursor.execute("SELECT 1")
        print("✅ Database connection successful")

    print("🎉 All verifications passed!")

except Exception as e:
    print(f"❌ Verification failed: {e}")
    sys.exit(1)