#!/usr/bin/env python
"""
OPERATIVO 4: Verificar expiración controlada de JWT
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.test import Client
import json
import time
from datetime import datetime, timedelta
from rest_framework_simplejwt.tokens import AccessToken

print("\n" + "="*70)
print(" OPERATIVO 4: EXPIRACIÓN CONTROLADA DE JWT")
print("="*70)

client = Client()

# ========== Test 1: Verificar que JWT tiene expiración ==========
print("\n📝 Test 1: JWT tiene tiempo de expiración configurado")

response = client.post('/api/auth/login/', 
    data=json.dumps({'username': 'admin', 'password': 'password'}),
    content_type='application/json'
)

if response.status_code == 200:
    token_data = response.json()
    access_token = token_data.get('access')
    
    # Decodificar token
    try:
        decoded = AccessToken(access_token)
        exp_timestamp = decoded['exp']
        iat_timestamp = decoded['iat']
        
        exp_time = datetime.fromtimestamp(exp_timestamp)
        iat_time = datetime.fromtimestamp(iat_timestamp)
        duration_seconds = exp_timestamp - iat_timestamp
        duration_minutes = duration_seconds / 60
        
        print(f"   ✓ Token generado en: {iat_time}")
        print(f"   ✓ Token expira en: {exp_time}")
        print(f"   ✓ Duración: {duration_minutes:.1f} minutos ({duration_seconds}s)")
        
        if duration_seconds > 0:
            print(f"   ✅ JWT correctamente configurado con expiración")
            test1_ok = True
        else:
            print(f"   ❌ JWT con duración inválida")
            test1_ok = False
    except Exception as e:
        print(f"   ❌ Error decodificando token: {e}")
        test1_ok = False
else:
    print(f"   ❌ Error en login: {response.status_code}")
    test1_ok = False

# ========== Test 2: Verificar que token manualmente expirado es rechazado ==========
print("\n📝 Test 2: Token expirado es rechazado por API")

try:
    # Crear token expirado manualmente
    from rest_framework_simplejwt.tokens import AccessToken
    from rest_framework_simplejwt.settings import api_settings
    from rest_framework_simplejwt.backends import TokenBackend
    import jwt
    
    # Crear token con expiración en el pasado
    expired_payload = {
        'token_type': 'access',
        'exp': int(time.time()) - 3600,  # Hace 1 hora
        'iat': int(time.time()) - 7200,  # Hace 2 horas
        'jti': '1234567890',
        'user_id': '1'
    }
    
    algorithm = api_settings.ALGORITHM
    secret = api_settings.SIGNING_KEY
    expired_token = jwt.encode(expired_payload, secret, algorithm=algorithm)
    
    # Intentar usar token expirado
    resp = client.get('/api/postulantes/', 
        HTTP_AUTHORIZATION=f'Bearer {expired_token}'
    )
    
    if resp.status_code == 401:
        print(f"   ✓ Token expirado rechazado con 401")
        print(f"   ✅ Expiración JWT funciona correctamente")
        test2_ok = True
    else:
        print(f"   ❌ Token expirado NO fue rechazado (status: {resp.status_code})")
        test2_ok = False
        
except Exception as e:
    print(f"   ⚠️ Error en test de expiración: {e}")
    test2_ok = False

# ========== Test 3: Token válido sigue funcionando ==========
print("\n📝 Test 3: Token válido funciona correctamente")

try:
    response = client.post('/api/auth/login/', 
        data=json.dumps({'username': 'admin', 'password': 'password'}),
        content_type='application/json'
    )
    
    if response.status_code == 200:
        access_token = response.json().get('access')
        
        resp = client.get('/api/postulantes/', 
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        if resp.status_code == 200:
            print(f"   ✓ Token válido acepta GET /postulantes/ (200)")
            print(f"   ✅ JWT válido funciona")
            test3_ok = True
        else:
            print(f"   ❌ Token válido rechazado (status: {resp.status_code})")
            test3_ok = False
    else:
        print(f"   ❌ Error en login")
        test3_ok = False
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    test3_ok = False

# ========== RESUMEN ==========
print("\n" + "="*70)
print(" RESUMEN OPERATIVO 4")
print("="*70)

tests_ok = sum([test1_ok, test2_ok, test3_ok])
print(f"✅ Tests pasados: {tests_ok}/3")

if tests_ok == 3:
    print("\n🎉 OPERATIVO 4: OK - JWT correctamente configurado con expiración")
else:
    print(f"\n⚠️ OPERATIVO 4: ERROR - {3 - tests_ok} test(s) fallido(s)")

print("="*70 + "\n")
