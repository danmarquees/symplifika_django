#!/usr/bin/env bash
# Build script for Render.com deployment
# Exit on any error
set -o errexit

echo "🚀 Starting build process for Symplifika Django..."

# Print environment info
echo "📊 Environment Information:"
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo "Current directory: $(pwd)"
echo "DJANGO_SETTINGS_MODULE: ${DJANGO_SETTINGS_MODULE:-Not set}"

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p media
mkdir -p staticfiles
mkdir -p static
echo "✅ Directories created: logs, media, staticfiles, static"

# Set Django settings module for production
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-symplifika.production_settings}
echo "🔧 Using Django settings: $DJANGO_SETTINGS_MODULE"

# Check if Django can be imported
echo "🔍 Checking Django installation..."
python -c "import django; print(f'Django version: {django.get_version()}')" || {
    echo "❌ Django import failed"
    exit 1
}

# Check if settings can be loaded
echo "🔍 Checking Django settings..."
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', '$DJANGO_SETTINGS_MODULE'); import django; django.setup(); from django.conf import settings; print('✅ Settings loaded successfully')" || {
    echo "❌ Django settings failed to load"
    exit 1
}

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --verbosity=2

# Check for database connectivity
echo "🔍 Checking database connectivity..."
python manage.py check --database default || {
    echo "⚠️  Database check failed, but continuing..."
}

# Run database migrations
echo "🔄 Running database migrations..."
python manage.py migrate --verbosity=2

# Create cache table if needed
echo "🗃️  Creating cache table..."
python manage.py createcachetable || {
    echo "ℹ️  Cache table creation skipped (may already exist or not configured)"
}

# Create superuser if it doesn't exist
echo "👤 Setting up superuser..."
python manage.py shell << 'EOF'
import os
from django.contrib.auth import get_user_model

User = get_user_model()

# Check if any superuser exists
if not User.objects.filter(is_superuser=True).exists():
    # Create default superuser
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@symplifika.com')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')

    User.objects.create_superuser(
        username='admin',
        email=admin_email,
        password=admin_password
    )
    print(f'✅ Superuser created: admin / {admin_password}')
    print(f'📧 Email: {admin_email}')
    print('⚠️  Please change the default password after first login!')
else:
    print('✅ Superuser already exists')
EOF

# Check Django deployment settings
echo "🔐 Checking deployment configuration..."
python manage.py check --deploy --verbosity=2 || {
    echo "⚠️  Some deployment checks failed, but continuing..."
}

# Final verification
echo "🔍 Final verification..."
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '$DJANGO_SETTINGS_MODULE')
import django
django.setup()

from django.conf import settings
from django.core.management import execute_from_command_line

print('✅ Django setup successful')
print(f'✅ DEBUG: {settings.DEBUG}')
print(f'✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
print(f'✅ DATABASE ENGINE: {settings.DATABASES[\"default\"][\"ENGINE\"]}')
print(f'✅ STATIC_ROOT: {settings.STATIC_ROOT}')
print(f'✅ STATICFILES_STORAGE: {getattr(settings, \"STATICFILES_STORAGE\", \"Default\")}')
"

echo "🎉 Build completed successfully!"
echo ""
echo "📋 Build Summary:"
echo "   • Python dependencies installed"
echo "   • Static files collected"
echo "   • Database migrations applied"
echo "   • Superuser configured"
echo "   • Deployment checks completed"
echo ""
echo "🚀 Ready for deployment!"
