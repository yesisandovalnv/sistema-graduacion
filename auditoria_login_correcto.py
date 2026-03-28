#!/usr/bin/env python
"""Test /api/auth/login/ endpoint (URL correcta)"""
import urllib.request
import json

print("🔍 AUDITORÍA: Verificar endpoint /api/auth/login/")
print("=" * 70)
print()

# Test 1: Endpoint disponible
print("[1] Verificar que endpoint responde:")
try:
    data = json.dumps({"username": "admin", "password": "password"}).encode()
    req = urllib.request.Request(
        'http://localhost/api/auth/login/',
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    response = urllib.request.urlopen(req, timeout=5)
    result = json.loads(response.read())
    print(f"✅ Status: {response.status}")
    print(f"✅ Response: {json.dumps(result, indent=2)}")
except urllib.error.HTTPError as e:
    print(f"❌ HTTP Error: {e.code}")
    body = e.read()
    print(f"   Body: {body}")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")

print()
print("=" * 70)
print("NOTA: El endpoint correcto es /api/auth/login/ (no /api/token/)")
