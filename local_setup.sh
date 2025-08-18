#!/usr/bin/env bash

# Local Development Setup Script for Symplifika Django
echo "🚀 Setting up Symplifika Django for local development..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not detected. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Virtual environment created and activated"
else
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Local Development Environment
DEBUG=True
SECRET_KEY=django-insecure-local-development-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,testserver

# Database (SQLite for local development)
# DATABASE_URL=sqlite:///db.sqlite3

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000,http://127.0.0.1:3000
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000,http://127.0.0.1:3000

# AI Configuration (add your OpenAI key here)
OPENAI_API_KEY=

# Email settings (for development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EOF
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi

# Create logs directory
mkdir -p logs
echo "✅ Logs directory created"

# Create media directory
mkdir -p media
echo "✅ Media directory created"

# Run migrations
echo "🔄 Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser (optional)
echo ""
echo "👤 Do you want to create a superuser? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    python manage.py createsuperuser
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Add your OpenAI API key to the .env file"
echo "   2. Run: python manage.py runserver"
echo "   3. Visit: http://localhost:8000"
echo "   4. Admin panel: http://localhost:8000/admin"
echo ""
echo "💡 Useful commands:"
echo "   • Start development server: python manage.py runserver"
echo "   • Run tests: python manage.py test"
echo "   • Create migrations: python manage.py makemigrations"
echo "   • Apply migrations: python manage.py migrate"
echo "   • Django shell: python manage.py shell"
echo ""
