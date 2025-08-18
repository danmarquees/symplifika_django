#!/usr/bin/env python
"""
Environment Check Script for Symplifika Django
This script helps diagnose environment and configuration issues
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_section(title):
    """Print a formatted section"""
    print(f"\n{'-'*40}")
    print(f" {title}")
    print(f"{'-'*40}")

def check_python_environment():
    """Check Python environment details"""
    print_section("Python Environment")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Platform: {sys.platform}")
    print(f"Current working directory: {os.getcwd()}")

    # Check virtual environment
    venv = os.environ.get('VIRTUAL_ENV')
    if venv:
        print(f"Virtual environment: {venv}")
    else:
        print("Virtual environment: Not detected")

def check_django_installation():
    """Check Django installation and basic setup"""
    print_section("Django Installation")
    try:
        import django
        print(f"✅ Django version: {django.get_version()}")
        print(f"Django location: {django.__file__}")
    except ImportError as e:
        print(f"❌ Django import failed: {e}")
        return False

    # Check if manage.py exists
    manage_py = Path("manage.py")
    if manage_py.exists():
        print("✅ manage.py found")
    else:
        print("❌ manage.py not found")
        return False

    return True

def check_environment_variables():
    """Check important environment variables"""
    print_section("Environment Variables")

    important_vars = [
        'DJANGO_SETTINGS_MODULE',
        'DEBUG',
        'SECRET_KEY',
        'DATABASE_URL',
        'ALLOWED_HOSTS',
        'OPENAI_API_KEY',
        'RENDER_EXTERNAL_HOSTNAME',
        'PORT'
    ]

    for var in important_vars:
        value = os.environ.get(var)
        if value:
            if var in ['SECRET_KEY', 'OPENAI_API_KEY', 'DATABASE_URL']:
                # Mask sensitive values
                masked_value = value[:10] + '...' if len(value) > 10 else '***'
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"⚠️  {var}: Not set")

def check_django_settings():
    """Check Django settings configuration"""
    print_section("Django Settings")

    try:
        # Set default settings module if not set
        if not os.environ.get('DJANGO_SETTINGS_MODULE'):
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'symplifika.settings')

        import django
        django.setup()
        from django.conf import settings

        print(f"✅ Settings module: {settings.SETTINGS_MODULE}")
        print(f"✅ DEBUG: {settings.DEBUG}")
        print(f"✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")

        # Database configuration
        db_config = settings.DATABASES['default']
        print(f"✅ Database engine: {db_config['ENGINE']}")
        if 'NAME' in db_config:
            print(f"✅ Database name: {db_config['NAME']}")

        # Static files
        print(f"✅ STATIC_URL: {settings.STATIC_URL}")
        print(f"✅ STATIC_ROOT: {settings.STATIC_ROOT}")

        # Check for staticfiles storage
        storage = getattr(settings, 'STATICFILES_STORAGE', 'Default')
        print(f"✅ STATICFILES_STORAGE: {storage}")

    except Exception as e:
        print(f"❌ Django settings error: {e}")
        return False

    return True

def check_database_connectivity():
    """Check database connectivity"""
    print_section("Database Connectivity")

    try:
        from django.db import connections
        from django.core.management import execute_from_command_line

        db_conn = connections['default']
        db_conn.cursor()
        print("✅ Database connection successful")

        # Try to run a simple query
        with db_conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                print("✅ Database query successful")

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

    return True

def check_installed_packages():
    """Check installed packages"""
    print_section("Installed Packages")

    required_packages = [
        'django',
        'djangorestframework',
        'django-cors-headers',
        'python-decouple',
        'openai',
        'requests',
        'gunicorn',
        'psycopg2-binary',
        'whitenoise',
        'dj-database-url'
    ]

    for package in required_packages:
        try:
            result = subprocess.run(
                [sys.executable, '-c', f'import {package.replace("-", "_")}; print("installed")'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"✅ {package}")
            else:
                print(f"❌ {package}: Not found")
        except Exception:
            print(f"❌ {package}: Error checking")

def check_file_structure():
    """Check project file structure"""
    print_section("File Structure")

    important_files = [
        'manage.py',
        'requirements.txt',
        'build.sh',
        'runtime.txt',
        'Procfile',
        'symplifika/settings.py',
        'symplifika/wsgi.py',
        'symplifika/urls.py',
    ]

    for file_path in important_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}: Missing")

def check_directories():
    """Check important directories"""
    print_section("Directories")

    important_dirs = [
        'static',
        'staticfiles',
        'media',
        'logs',
        'templates'
    ]

    for dir_path in important_dirs:
        path = Path(dir_path)
        if path.exists():
            if path.is_dir():
                print(f"✅ {dir_path}/")
            else:
                print(f"⚠️  {dir_path}: Exists but not a directory")
        else:
            print(f"⚠️  {dir_path}/: Missing")

def run_django_checks():
    """Run Django system checks"""
    print_section("Django System Checks")

    try:
        from django.core.management import execute_from_command_line

        print("Running Django system checks...")
        execute_from_command_line(['manage.py', 'check'])
        print("✅ Django system checks passed")

    except Exception as e:
        print(f"❌ Django system checks failed: {e}")
        return False

    return True

def main():
    """Main function to run all checks"""
    print_header("Symplifika Django Environment Check")
    print("This script will check your environment configuration")

    checks = [
        ("Python Environment", check_python_environment),
        ("Django Installation", check_django_installation),
        ("Environment Variables", check_environment_variables),
        ("Django Settings", check_django_settings),
        ("Database Connectivity", check_database_connectivity),
        ("Installed Packages", check_installed_packages),
        ("File Structure", check_file_structure),
        ("Directories", check_directories),
        ("Django System Checks", run_django_checks),
    ]

    results = []

    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result if result is not None else True))
        except Exception as e:
            print(f"❌ {check_name} failed with error: {e}")
            results.append((check_name, False))

    # Summary
    print_header("Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"Checks passed: {passed}/{total}")
    print()

    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")

    if passed == total:
        print(f"\n🎉 All checks passed! Your environment is ready.")
    else:
        print(f"\n⚠️  Some checks failed. Please review the output above.")

    print(f"\nFor more help, check the RENDER_DEPLOY.md file.")

if __name__ == "__main__":
    main()
