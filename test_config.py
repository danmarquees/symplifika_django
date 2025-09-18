#!/usr/bin/env python
"""
Simple test script to validate Symplifika configuration
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'symplifika.settings')
django.setup()

from core.utils import validate_api_configuration, EnvironmentHelper, APIEndpoints
from django.conf import settings

def main():
    print('=== Symplifika Configuration Validation ===\n')
    
    # Validate API configuration
    config_status = validate_api_configuration()
    
    print('📡 API Configuration:')
    for key, status in config_status.items():
        status_icon = '✅' if status else '❌'
        print(f'  {status_icon} {key.replace("_", " ").title()}: {status}')
    
    print('\n🌐 Environment:')
    print(f'  📍 Environment: {"Production" if EnvironmentHelper.is_production() else "Development"}')
    print(f'  🔗 API Base URL: {settings.API_BASE_URL}')
    print(f'  🖥️  Frontend URL: {settings.FRONTEND_URL}')
    
    print('\n💳 Payment Configuration:')
    stripe_status = '✅ Configured' if EnvironmentHelper.is_stripe_configured() else '❌ Not configured'
    print(f'  💰 Stripe: {stripe_status}')
    
    print('\n🤖 AI Configuration:')
    ai_status = '✅ Configured' if EnvironmentHelper.is_ai_configured() else '❌ Not configured'
    print(f'  🧠 Gemini API: {ai_status}')
    
    print('\n🔍 API Endpoints Available:')
    try:
        endpoints = APIEndpoints.get_all_endpoints()
        for category, category_endpoints in endpoints.items():
            print(f'  📂 {category.title()}:')
            for endpoint_name in category_endpoints.keys():
                print(f'    - {endpoint_name}')
    except Exception as e:
        print(f'  ❌ Error loading endpoints: {e}')
    
    # Test specific endpoint retrieval
    print('\n🧪 Testing Endpoint Retrieval:')
    try:
        login_endpoint = APIEndpoints.get_endpoint('auth', 'login')
        print(f'  ✅ Auth login endpoint: {login_endpoint}')
        
        checkout_endpoint = APIEndpoints.get_endpoint('payments', 'create_checkout_session')
        print(f'  ✅ Payment checkout endpoint: {checkout_endpoint}')
        
        shortcuts_endpoint = APIEndpoints.get_endpoint('shortcuts', 'list')
        print(f'  ✅ Shortcuts list endpoint: {shortcuts_endpoint}')
    except Exception as e:
        print(f'  ❌ Error testing endpoints: {e}')
    
    # Check for common issues
    print('\n🔍 Potential Issues:')
    issues = []
    
    if not config_status['stripe_configured']:
        issues.append('Stripe not configured - payment features will not work')
    
    if not config_status['ai_configured']:
        issues.append('AI not configured - AI features will not work')
    
    if settings.DEBUG and 'localhost' not in settings.API_BASE_URL:
        issues.append('DEBUG=True but API_BASE_URL is not localhost')
    
    if not issues:
        print('  ✅ No issues found!')
    else:
        for issue in issues:
            print(f'  ⚠️  {issue}')
    
    print('\n' + '='*50)

if __name__ == '__main__':
    main()
