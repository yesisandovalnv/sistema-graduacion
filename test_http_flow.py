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

BASE_URL = "http://localhost:8000"

try:
    print("=" * 80)
    print("STEP 1: Login and get token")
    print("=" * 80)
    
    login_data = json.dumps({
        "username": "admin",
        "password": "password"
    }).encode('utf-8')
    
    login_req = urllib.request.Request(
        f"{BASE_URL}/api/auth/login/",
        data=login_data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        login_response = urllib.request.urlopen(login_req)
        login_body = login_response.read().decode('utf-8')
        print(f"Login Status: {login_response.status}")
        
        token_data = json.loads(login_body)
        access_token = token_data.get('access')
        
        if not access_token:
            print(f"❌ No token in response: {token_data}")
            sys.exit(1)
        
        print(f"✅ Got access token: {access_token[:50]}...")
        
    except urllib.error.HTTPError as e:
        print(f"❌ Login Error {e.code}: {e.read().decode()[:200]}")
        sys.exit(1)
    
    print("\n" + "=" * 80)
    print("STEP 2: Call dashboard endpoint with token")
    print("=" * 80)
    
    dashboard_req = urllib.request.Request(
        f"{BASE_URL}/api/reportes/dashboard-general/",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        },
        method="GET"
    )
    
    try:
        dashboard_response = urllib.request.urlopen(dashboard_req)
        dashboard_body = dashboard_response.read().decode('utf-8')
        
        print(f"Dashboard Status: {dashboard_response.status}")
        print(f"Dashboard Response (first 500 chars): {dashboard_body[:500]}")
        
        data = json.loads(dashboard_body)
        print(f"\n✅ SUCCESS - Status {dashboard_response.status}")
        print(f"✅ Response is valid JSON")
        print(f"✅ Keys in response: {list(data.keys())}")
        
    except urllib.error.HTTPError as e:
        print(f"❌ Dashboard Error {e.code}")
        error_body = e.read().decode('utf-8')
        print(f"Error response:\n{error_body[:1000]}")
        
        try:
            error_json = json.loads(error_body)
            print(f"JSON error: {error_json}")
        except:
            print(f"Raw error:\n{error_body}")

except Exception as e:
    print("❌ ERROR:")
    print("=" * 80)
    print(traceback.format_exc())
    print("=" * 80)
    sys.exit(1)
