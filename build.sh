#!/usr/bin/env bash
# Build script for Render.com deployment
# Supports PostgreSQL for better data persistence
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
python -c "
import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '$DJANGO_SETTINGS_MODULE')
try:
    import django
    django.setup()
    from django.conf import settings
    print('✅ Settings loaded successfully')
    print(f'Database engine: {settings.DATABASES[\"default\"][\"ENGINE\"]}')
    if 'postgresql' in settings.DATABASES[\"default\"][\"ENGINE\"]:
        print(f'Database name: {settings.DATABASES[\"default\"].get(\"NAME\", \"N/A\")}')
        print(f'Database host: {settings.DATABASES[\"default\"].get(\"HOST\", \"N/A\")}')
    else:
        print(f'Database file: {settings.DATABASES[\"default\"].get(\"NAME\", \"N/A\")}')
except Exception as e:
    print(f'❌ Settings load failed: {e}')
    sys.exit(1)
"

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --verbosity=1

# Run database migrations
echo "🔄 Running database migrations..."
# Wait a bit for database to be ready (for PostgreSQL)
sleep 2
python manage.py migrate --verbosity=1

# Check if we're using PostgreSQL and create indexes if needed
echo "🔍 Checking database optimization..."
python manage.py shell << 'EOF'
from django.conf import settings
from django.db import connection

db_engine = settings.DATABASES['default']['ENGINE']
if 'postgresql' in db_engine:
    print('✅ Using PostgreSQL - optimized for production')
    # You can add custom SQL commands here if needed
    # cursor = connection.cursor()
    # cursor.execute("CREATE INDEX IF NOT EXISTS idx_example ON your_table(column_name);")
else:
    print('ℹ️  Using SQLite - suitable for development')
EOF

# Create cache table if needed
echo "🗃️  Creating cache table..."
python manage.py createcachetable 2>/dev/null || {
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

    try:
        User.objects.create_superuser(
            username='admin',
            email=admin_email,
            password=admin_password
        )
        print(f'✅ Superuser created: admin / {admin_password}')
        print(f'📧 Email: {admin_email}')
        print('⚠️  Please change the default password after first login!')
    except Exception as e:
        print(f'⚠️  Superuser creation failed: {e}')
else:
    print('✅ Superuser already exists')
EOF

# Final verification
echo "🔍 Final verification..."
python verify_build.py

echo "🎉 Build completed successfully!"
echo ""
echo "📋 Build Summary:"
echo "   • Python dependencies installed"
echo "   • Static files collected"
if [ -n "$DATABASE_URL" ]; then
    echo "   • Database migrations applied (PostgreSQL)"
else
    echo "   • Database migrations applied (SQLite)"
fi
echo "   • Superuser configured"
echo "   • Deployment checks completed"
echo ""
echo "🚀 Ready for deployment!"
