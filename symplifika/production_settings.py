"""
Production settings for symplifika project on Render.com
Uses PostgreSQL for better data persistence and scalability
"""

import os
import dj_database_url
from .settings import *

# Override settings for production
DEBUG = False

# Production-specific overrides (everything else inherited from base settings)
SECURE_HSTS_PRELOAD = True

# Override logging level for production
LOGGING['loggers']['symplifika']['level'] = 'INFO'

# Production info logging
print(f"Production settings loaded - DEBUG: {DEBUG}")
