#!/usr/bin/env python
"""
Auditoría HTTP usando Django Test Client
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.test import Client
import json

print("\n" + "="*70)
print(" AUDITORÍA HTTP - Django Test Client")
print("="*70)

client = Client()

# ========== TEST 1: Login ==========
print("\n📝 Test 1: Login admin")
response = client.post('/api/auth/login/', 
    data=json.dumps({'username': 'admin', 'password': 'password'}),
    content_type='application/json'
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    token = data.get('access')
    print(f"✓ Token: {token[:40]}...")
else:
    print(f"Body: {response.json()}")
    print("\n❌ NO SE PUDO OBTENER TOKEN")
    exit(1)

# ========== TEST 2: GET sin token (esperado: 401) ==========
print("\n📝 Test 2: GET /postulantes/ sin token")
resp = client.get('/api/postulantes/')
print(f"Status: {resp.status_code}")
if resp.status_code == 401:
    print("✅ 401 Unauthorized (correcto)")
else:
    print(f"⚠ Esperaba 401, obtuvo {resp.status_code}")

# ========== TEST 3: GET con token inválido (esperado: 401) ==========
print("\n📝 Test 3: GET /postulantes/ con token inválido")
resp = client.get('/api/postulantes/', HTTP_AUTHORIZATION='Bearer invalid_token_xyz')
print(f"Status: {resp.status_code}")
if resp.status_code == 401:
    print("✅ 401 Unauthorized (correcto)")
else:
    print(f"⚠ Esperaba 401, obtuvo {resp.status_code}")

# ========== TEST 4: GET con token válido ==========
print("\n📝 Test 4: GET /postulantes/ con token válido")
resp = client.get('/api/postulantes/', HTTP_AUTHORIZATION=f'Bearer {token}')
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    count = data.get('count', len(data)) if isinstance(data, (dict, list)) else 0
    print(f"✅ 200 OK - {count} postulantes")
else:
    print(f"⚠ Status: {resp.status_code}")

# ========== TEST 5: POST datos incompletos ==========
print("\n📝 Test 5: POST /postulantes/ datos incompletos (esperado: 400)")
resp = client.post('/api/postulantes/',
    data=json.dumps({'nombre': 'Test', 'apellido': 'Incomplete'}),
    content_type='application/json',
    HTTP_AUTHORIZATION=f'Bearer {token}'
)
print(f"Status: {resp.status_code}")
if resp.status_code == 400:
    errors = resp.json()
    print(f"✅ 400 Bad Request - Campos requeridos: {list(errors.keys())}")
else:
    print(f"⚠ Esperaba 400, obtuvo {resp.status_code}")

# ========== ESTADÍSTICAS ==========
print("\n" + "="*70)
print(" ✨ PRUEBAS COMPLETADAS")
print("="*70 + "\n")
