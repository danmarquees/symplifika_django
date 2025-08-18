"""
Production settings for symplifika project on Render.com
Uses SQLite by default for simplicity and compatibility
"""

import os
from .settings import *

# Override settings for production
DEBUG = False

# Security settings
ALLOWED_HOSTS = [
    os.environ.get('RENDER_EXTERNAL_HOSTNAME', ''),
    'localhost',
    '127.0.0.1'
]

# Remove any empty strings from ALLOWED_HOSTS
ALLOWED_HOSTS = [host for host in ALLOWED_HOSTS if host]

# Use SQLite for simplicity - works reliably on Render free tier
# This avoids PostgreSQL driver compatibility issues
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# CORS and CSRF settings for Render
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    CORS_ALLOWED_ORIGINS = [
        f"https://{RENDER_EXTERNAL_HOSTNAME}",
        f"http://{RENDER_EXTERNAL_HOSTNAME}",
    ]
    CSRF_TRUSTED_ORIGINS = [
        f"https://{RENDER_EXTERNAL_HOSTNAME}",
    ]

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_PRELOAD = True

# Simplified logging for production - console only
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[{levelname}] {asctime} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'symplifika': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'gunicorn': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Session configuration - use database sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 24 hours

# Email configuration (if needed)
if all(key in os.environ for key in ['EMAIL_HOST', 'EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD']):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ['EMAIL_HOST']
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
    EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
    EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
else:
    # Use console backend for development/testing
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Print configuration info for debugging
print(f"Production settings loaded:")
print(f"  - DEBUG: {DEBUG}")
print(f"  - ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print(f"  - DATABASE ENGINE: {DATABASES['default']['ENGINE']}")
print(f"  - RENDER_EXTERNAL_HOSTNAME: {RENDER_EXTERNAL_HOSTNAME}")
print(f"  - Using SQLite for maximum compatibility")
