"""
Context processors for Symplifika project
"""
import json
from django.conf import settings
from .utils import get_api_context


def api_context(request):
    """
    Add API configuration to template context
    
    Args:
        request: Django request object
        
    Returns:
        Dictionary with API context
    """
    return {
        'api_config': json.dumps(get_api_context()),
        'app_name': getattr(settings, 'APP_NAME', 'Symplifika'),
        'debug': settings.DEBUG,
    }
