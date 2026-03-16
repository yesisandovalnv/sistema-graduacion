#!/usr/bin/env python
import os
import sys
import django
import traceback
import json
import urllib.request
import urllib.parse

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Test through NGINX (port 80) like the frontend does
BASE_URL = "http://localhost/api"

try:
    print("=" * 80)
    print("Testing through NGINX port 80 (like frontend)")
    print("=" * 80)
    
    print("\nSTEP 1: Login")
    login_data = json.dumps({
        "username": "admin",
        "password": "password"
    }).encode('utf-8')
    
    login_req = urllib.request.Request(
        f"{BASE_URL}/auth/login/",
        data=login_data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        login_response = urllib.request.urlopen(login_req)
        login_body = login_response.read().decode('utf-8')
        print(f"✅ Login Status: {login_response.status}")
        
        token_data = json.loads(login_body)
        access_token = token_data.get('access')
        print(f"✅ Got token: {access_token[:50]}...")
        
    except urllib.error.HTTPError as e:
        print(f"❌ Login Error {e.code}")
        print(e.read().decode()[:200])
        sys.exit(1)
    
    print("\nSTEP 2: Dashboard through NGINX")
    dashboard_req = urllib.request.Request(
        f"{BASE_URL}/reportes/dashboard-general/",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        },
        method="GET"
    )
    
    try:
        dashboard_response = urllib.request.urlopen(dashboard_req)
        dashboard_body = dashboard_response.read().decode('utf-8')
        
        print(f"✅ Dashboard Status: {dashboard_response.status}")
        print(f"✅ Response length: {len(dashboard_body)} bytes")
        print(f"✅ Response: {dashboard_body[:200]}...")
        
        data = json.loads(dashboard_body)
        print(f"✅ Valid JSON with {len(data)} keys")
        
    except urllib.error.HTTPError as e:
        print(f"❌ Dashboard Error {e.code}")
        error_body = e.read().decode('utf-8')
        print(f"Error:\n{error_body[:500]}")

except Exception as e:
    print("❌ ERROR:")
    print(traceback.format_exc())
    sys.exit(1)
