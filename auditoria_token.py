#!/usr/bin/env python
"""Test /api/token/ endpoint"""
import urllib.request
import json

print("🔍 AUDITORÍA: Verificar endpoint /api/token/")
print("=" * 70)
print()

# Test 1: Endpoint disponible
print("[1] Verificar que endpoint responde:")
try:
    data = json.dumps({"username": "admin", "password": "password"}).encode()
    req = urllib.request.Request(
        'http://localhost/api/token/',
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    response = urllib.request.urlopen(req, timeout=5)
    result = json.loads(response.read())
    print(f"✅ Status: {response.status}")
    print(f"✅ Response: {result}")
except urllib.error.HTTPError as e:
    print(f"❌ HTTP Error: {e.code}")
    try:
        error_data = json.loads(e.read())
        print(f"   Error: {error_data}")
    except:
        print(f"   Body: {e.read()}")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")

print()
print("=" * 70)
print("CONCLUSIÓN:")
print("• Si ves 'CustomUser matching query does not exist' → Usuario no existe en DB")
print("• Si ves 'unauthorized' → Credenciales incorrectas")
print("• Si ves 'internal server error' → Error en el backend")
