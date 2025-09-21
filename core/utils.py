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


def get_breadcrumbs_context(breadcrumbs_list=None):
    """
    Generate breadcrumbs context for templates

    Args:
        breadcrumbs_list: List of breadcrumb dictionaries with 'title' and 'url' keys

    Returns:
        Dictionary with breadcrumbs data
    """
    if breadcrumbs_list is None:
        breadcrumbs_list = []

    return {
        'breadcrumbs': breadcrumbs_list,
        'has_breadcrumbs': len(breadcrumbs_list) > 0
    }


def build_breadcrumbs(*breadcrumbs):
    """
    Helper function to build breadcrumbs list

    Args:
        *breadcrumbs: Variable arguments of breadcrumb dictionaries or tuples

    Returns:
        List of breadcrumb dictionaries

    Example:
        build_breadcrumbs(
            ('Home', reverse('core:index')),
            ('Settings', reverse('core:settings')),
            ('Profile', None)  # Current page
        )
    """
    breadcrumb_list = []

    for breadcrumb in breadcrumbs:
        if isinstance(breadcrumb, dict):
            breadcrumb_list.append(breadcrumb)
        elif isinstance(breadcrumb, (tuple, list)) and len(breadcrumb) == 2:
            breadcrumb_list.append({
                'title': breadcrumb[0],
                'url': breadcrumb[1]
            })
        else:
            raise ValueError("Breadcrumb must be a dict or tuple/list of (title, url)")

    return breadcrumb_list


def get_pagination_context(page_obj, request=None):
    """
    Generate pagination context for templates

    Args:
        page_obj: Django Paginator page object
        request: Django request object (optional, for preserving query params)

    Returns:
        Dictionary with pagination data
    """
    context = {
        'page_obj': page_obj,
        'has_pagination': page_obj.paginator.num_pages > 1,
        'pagination_info': {
            'current_page': page_obj.number,
            'total_pages': page_obj.paginator.num_pages,
            'total_items': page_obj.paginator.count,
            'items_per_page': page_obj.paginator.per_page,
            'start_index': page_obj.start_index(),
            'end_index': page_obj.end_index(),
        }
    }

    # Add query string preservation if request is provided
    if request:
        query_params = request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        context['query_string'] = query_params.urlencode()

    return context


def get_search_context(request, results=None, total_count=0):
    """
    Generate search context for templates

    Args:
        request: Django request object
        results: Search results (optional)
        total_count: Total count of results

    Returns:
        Dictionary with search context
    """
    query = request.GET.get('q', '').strip()
    filter_type = request.GET.get('filter', 'all')

    return {
        'search_query': query,
        'search_filter': filter_type,
        'search_results': results or [],
        'search_total_count': total_count,
        'has_search': bool(query),
        'search_filters': [
            {'value': 'all', 'label': 'Todos', 'active': filter_type == 'all'},
            {'value': 'shortcuts', 'label': 'Atalhos', 'active': filter_type == 'shortcuts'},
            {'value': 'categories', 'label': 'Categorias', 'active': filter_type == 'categories'},
            {'value': 'commands', 'label': 'Comandos', 'active': filter_type == 'commands'},
        ]
    }


def get_user_context(user):
    """
    Generate user context for templates

    Args:
        user: Django User object

    Returns:
        Dictionary with user context
    """
    if not user.is_authenticated:
        return {'user': None, 'is_authenticated': False}

    # Try to get user profile
    try:
        from users.models import UserProfile
        profile, created = UserProfile.objects.get_or_create(user=user)
    except ImportError:
        profile = None

    context = {
        'user': user,
        'is_authenticated': True,
        'user_profile': profile,
        'user_display_name': user.get_full_name() or user.username,
        'user_initials': get_user_initials(user),
    }

    if profile:
        context.update({
            'user_plan': getattr(profile, 'plan', None),
            'user_theme': getattr(profile, 'theme', 'light'),
            'user_avatar': profile.avatar.url if hasattr(profile, 'avatar') and profile.avatar else None,
        })

    return context


def get_user_initials(user):
    """
    Get user initials for avatar display

    Args:
        user: Django User object

    Returns:
        String with user initials (max 2 characters)
    """
    if user.first_name and user.last_name:
        return f"{user.first_name[0]}{user.last_name[0]}".upper()
    elif user.first_name:
        return user.first_name[0].upper()
    elif user.username:
        return user.username[0].upper()
    else:
        return "U"


def format_number(number, format_type='short'):
    """
    Format numbers for display

    Args:
        number: Number to format
        format_type: 'short' for 1K, 1M format or 'full' for comma-separated

    Returns:
        Formatted number string
    """
    if format_type == 'short':
        if number >= 1000000:
            return f"{number/1000000:.1f}M"
        elif number >= 1000:
            return f"{number/1000:.1f}K"
        else:
            return str(number)
    else:
        return f"{number:,}"


def safe_json_encode(data):
    """
    Safely encode data to JSON for template use

    Args:
        data: Data to encode

    Returns:
        JSON string safe for template embedding
    """
    import json
    from django.utils.safestring import mark_safe
    from django.core.serializers.json import DjangoJSONEncoder

    return mark_safe(json.dumps(data, cls=DjangoJSONEncoder))
