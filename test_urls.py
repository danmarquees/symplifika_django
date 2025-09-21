#!/usr/bin/env python
"""
Test script to verify URL routing for shortcuts API
"""
import os
import sys
import django
from django.conf import settings
from django.test import Client
from django.contrib.auth.models import User

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'symplifika.settings')
django.setup()

def test_urls():
    print("🔍 Testing URL routing...")
    
    # Create test client
    client = Client()
    
    # Test endpoints
    endpoints = [
        '/',
        '/admin/',
        '/shortcuts/api/',
        '/shortcuts/api/shortcuts/',
        '/shortcuts/api/categories/',
        '/shortcuts/api/shortcuts/stats/',
    ]
    
    for endpoint in endpoints:
        try:
            response = client.get(endpoint)
            status = response.status_code
            content_type = response.get('Content-Type', 'N/A')
            
            if status == 200:
                print(f"✅ {endpoint} -> {status} ({content_type})")
            elif status == 401:
                print(f"🔐 {endpoint} -> {status} (Authentication required)")
            elif status == 403:
                print(f"🚫 {endpoint} -> {status} (Forbidden)")
            elif status == 404:
                print(f"❌ {endpoint} -> {status} (Not Found)")
            else:
                print(f"⚠️  {endpoint} -> {status}")
                
        except Exception as e:
            print(f"💥 {endpoint} -> Error: {e}")
    
    # Test with authenticated user
    print("\n🔍 Testing with authenticated user...")
    try:
        user, created = User.objects.get_or_create(username='testuser')
        if created:
            user.set_password('testpass')
            user.save()
            print("✅ Test user created")
        
        client.force_login(user)
        
        auth_endpoints = [
            '/shortcuts/api/shortcuts/',
            '/shortcuts/api/categories/',
            '/shortcuts/api/shortcuts/stats/',
        ]
        
        for endpoint in auth_endpoints:
            try:
                response = client.get(endpoint)
                status = response.status_code
                
                if status == 200:
                    print(f"✅ {endpoint} -> {status} (Authenticated)")
                else:
                    print(f"❌ {endpoint} -> {status} (Authenticated)")
                    
            except Exception as e:
                print(f"💥 {endpoint} -> Error: {e}")
                
    except Exception as e:
        print(f"💥 Authentication test error: {e}")

if __name__ == '__main__':
    test_urls()
