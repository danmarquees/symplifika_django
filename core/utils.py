"""
Utility functions for Symplifika project
"""
from django.conf import settings
from django.urls import reverse
from typing import Dict, Any, Optional


class APIEndpoints:
    """
    Centralized API endpoints management
    """
    
    @staticmethod
    def get_endpoint(category: str, endpoint: str, **kwargs) -> str:
        """
        Get API endpoint URL with optional parameters
        
        Args:
            category: Category of endpoint (auth, users, shortcuts, payments)
            endpoint: Specific endpoint name
            **kwargs: URL parameters to format
            
        Returns:
            Formatted endpoint URL
        """
        try:
            endpoint_url = settings.API_ENDPOINTS[category][endpoint]
            if kwargs:
                return endpoint_url.format(**kwargs)
            return endpoint_url
        except KeyError:
            raise ValueError(f"Endpoint {category}.{endpoint} not found")
    
    @staticmethod
    def get_frontend_url(page: str) -> str:
        """
        Get frontend URL for specific page
        
        Args:
            page: Page name (login, register, dashboard, etc.)
            
        Returns:
            Frontend URL
        """
        try:
            return settings.FRONTEND_URLS[page]
        except KeyError:
            raise ValueError(f"Frontend URL for {page} not found")
    
    @staticmethod
    def get_all_endpoints() -> Dict[str, Any]:
        """
        Get all configured API endpoints
        
        Returns:
            Dictionary with all endpoints
        """
        return settings.API_ENDPOINTS
    
    @staticmethod
    def get_chrome_extension_config() -> Dict[str, Any]:
        """
        Get Chrome extension configuration
        
        Returns:
            Chrome extension configuration
        """
        return settings.CHROME_EXTENSION


class EnvironmentHelper:
    """
    Helper class for environment-related utilities
    """
    
    @staticmethod
    def is_production() -> bool:
        """Check if running in production environment"""
        return not settings.DEBUG
    
    @staticmethod
    def is_development() -> bool:
        """Check if running in development environment"""
        return settings.DEBUG
    
    @staticmethod
    def get_base_url() -> str:
        """Get base URL for current environment"""
        return settings.API_BASE_URL
    
    @staticmethod
    def get_frontend_url() -> str:
        """Get frontend URL for current environment"""
        return settings.FRONTEND_URL
    
    @staticmethod
    def is_stripe_configured() -> bool:
        """Check if Stripe is properly configured"""
        return bool(
            settings.STRIPE_SECRET_KEY and 
            settings.STRIPE_PUBLISHABLE_KEY
        )
    
    @staticmethod
    def is_ai_configured() -> bool:
        """Check if AI (Gemini) is properly configured"""
        return bool(settings.GEMINI_API_KEY)


def get_api_context() -> Dict[str, Any]:
    """
    Get API context for templates
    
    Returns:
        Dictionary with API configuration for frontend use
    """
    return {
        'api_base_url': settings.API_BASE_URL,
        'frontend_url': settings.FRONTEND_URL,
        'endpoints': {
            'auth': {
                'login': APIEndpoints.get_endpoint('auth', 'login'),
                'register': APIEndpoints.get_endpoint('auth', 'register'),
                'logout': APIEndpoints.get_endpoint('auth', 'logout'),
            },
            'shortcuts': {
                'list': APIEndpoints.get_endpoint('shortcuts', 'list'),
                'create': APIEndpoints.get_endpoint('shortcuts', 'create'),
                'categories': APIEndpoints.get_endpoint('shortcuts', 'categories'),
            },
            'payments': {
                'create_checkout': APIEndpoints.get_endpoint('payments', 'create_checkout_session'),
                'plans': APIEndpoints.get_endpoint('payments', 'plans'),
            }
        },
        'stripe': {
            'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            'configured': EnvironmentHelper.is_stripe_configured(),
        },
        'environment': {
            'is_production': EnvironmentHelper.is_production(),
            'is_development': EnvironmentHelper.is_development(),
        }
    }


def format_endpoint_url(endpoint_template: str, **params) -> str:
    """
    Format endpoint URL with parameters
    
    Args:
        endpoint_template: URL template with placeholders
        **params: Parameters to replace in template
        
    Returns:
        Formatted URL
    """
    return endpoint_template.format(**params)


def validate_api_configuration() -> Dict[str, bool]:
    """
    Validate API configuration
    
    Returns:
        Dictionary with validation results
    """
    return {
        'stripe_configured': EnvironmentHelper.is_stripe_configured(),
        'ai_configured': EnvironmentHelper.is_ai_configured(),
        'base_url_set': bool(settings.API_BASE_URL),
        'frontend_url_set': bool(settings.FRONTEND_URL),
        'cors_configured': bool(settings.CORS_ALLOWED_ORIGINS),
    }
