#!/usr/bin/env python
"""
AUDITORÍA HTTP COMPLETA - Sistema Graduación
Usando Django Test Client para validar todos endpoints de API
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User
import json
from datetime import datetime

print("\n" + "="*80)
print(" AUDITORÍA HTTP REAL - SISTEMA GRADUACIÓN 2026")
print("="*80)

client = Client()
results = {}

def test_result(num, status, message=""):
    """Registra resultado de prueba."""
    results[num] = status
    emoji = "✅" if status == "OK" else "❌"
    print(f"\n{emoji} HTTP {num}: {status}")
    if message:
        print(f"   └─ {message[:100]}")

def get_admin_token():
    """Obtiene token JWT del admin."""
    response = client.post('/api/auth/login/', 
        data=json.dumps({'username': 'admin', 'password': 'password'}),
        content_type='application/json'
    )
    if response.status_code == 200:
        return response.json().get('access')
    return None

def create_normal_user(username=None):
    """Crea usuario normal (no admin)."""
    if not username:
        username = f'httpuser_{datetime.now().strftime("%Y%m%d%H%M%S")}'
    
    admin_token = get_admin_token()
    if not admin_token:
        raise Exception("No se pudo obtener token admin")
    
    response = client.post('/api/usuarios/',
        data=json.dumps({
            'username': username,
            'email': f'{username}@test.local',
            'password': 'password123',
            'role': 'estudiante'
        }),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {admin_token}'
    )
    
    if response.status_code != 201:
        error_detail = response.json()
        raise Exception(f"Error creando usuario: {response.status_code} - {error_detail}")
    
    return response.json()

def create_postulant(user_id, admin_token):
    """Crea postulante."""
    import time
    ts = str(int(time.time()))[-8:]  # Últimos 8 dígitos del timestamp
    response = client.post('/api/postulantes/',
        data=json.dumps({
            'usuario': user_id,
            'nombre': 'Test User',
            'apellido': f'Postulant{ts}',
            'ci': f'CI{ts}',
            'telefono': '5990000000',
            'codigo_estudiante': f'EST{ts}'
        }),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {admin_token}'
    )
    
    if response.status_code != 201:
        print(f"   DEBUG: Postulante response {response.status_code}: {response.json()}")
        raise Exception(f"Error creando postulante: {response.status_code}")
    
    return response.json()

# ============================================================================
# SETUP INICIAL
# ============================================================================
print("\n🔧 Setup inicial...")

admin_token = get_admin_token()
if not admin_token:
    print("❌ No se pudo obtener token admin - deteniendo.")
    exit(1)

print("   ✓ Token admin obtenido")

try:
    normal_user = create_normal_user()
    normal_user_id = normal_user['id']
    print(f"   ✓ Usuario normal creado (ID: {normal_user_id})")
    
    postulant = create_postulant(normal_user_id, admin_token)
    print(f"   ✓ Postulante creado (ID: {postulant['id']})")
except Exception as e:
    print(f"   ❌ Setup falló: {e}")
    exit(1)

# ============================================================================
# HTTP 1: Usuario normal intentar endpoint admin (403 Forbidden)
# ============================================================================
print("\n" + "="*80)
print(" HTTP 1: Usuario normal intentar endpoint admin (esperado: 403 Forbidden)")
print("="*80)

try:
    normal_user_login = client.post('/api/auth/login/',
        data=json.dumps({
            'username': normal_user['username'],
            'password': 'password123'
        }),
        content_type='application/json'
    )
    
    if normal_user_login.status_code != 200:
        raise Exception(f"User login falló: {normal_user_login.status_code}")
    
    normal_token = normal_user_login.json().get('access')
    print("   ✓ Usuario normal logueado")
    
    # Intentar crear otro usuario (endpoint admin)
    response = client.post('/api/usuarios/',
        data=json.dumps({
            'username': 'shouldfail',
            'email': 'fail@test.local',
            'password': 'fail123',
            'role': 'estudiante'
        }),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {normal_token}'
    )
    
    print(f"   Respuesta: {response.status_code}")
    
    if response.status_code == 403:
        test_result(1, 'OK', 'Usuario normal rechazado con 403 Forbidden')
    elif response.status_code == 400:
        test_result(1, 'ERROR', 'Endpoint retornó 400 en lugar de 403')
    else:
        test_result(1, 'ERROR', f'Esperaba 403, obtuvo {response.status_code}')

except Exception as e:
    test_result(1, 'ERROR', str(e))

# ============================================================================
# HTTP 2: Token inválido (401 Unauthorized)
# ============================================================================
print("\n" + "="*80)
print(" HTTP 2: Token inválido (esperado: 401 Unauthorized)")
print("="*80)

try:
    bad_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.token'
    
    response = client.get('/api/postulantes/',
        HTTP_AUTHORIZATION=f'Bearer {bad_token}'
    )
    
    print(f"   GET /api/postulantes/ con token inválido: {response.status_code}")
    
    if response.status_code == 401:
        test_result(2, 'OK', 'Token inválido rechazado con 401 Unauthorized')
    else:
        test_result(2, 'ERROR', f'Esperaba 401, obtuvo {response.status_code}')

except Exception as e:
    test_result(2, 'ERROR', str(e))

# ============================================================================
# HTTP 3: Datos incompletos (400 Bad Request con detalles)
# ============================================================================
print("\n" + "="*80)
print(" HTTP 3: Datos incompletos (esperado: 400 Bad Request con detalles)")
print("="*80)

try:
    response = client.post('/api/postulantes/',
        data=json.dumps({
            'nombre': 'Incomplete',
            'apellido': 'User'
            # Faltan: usuario, ci, telefono, codigo_estudiante
        }),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {admin_token}'
    )
    
    print(f"   POST /api/postulantes/ incompleto: {response.status_code}")
    
    if response.status_code == 400:
        error_data = response.json()
        required_fields = list(error_data.keys())
        print(f"   Campos requeridos no completados: {required_fields}")
        test_result(3, 'OK', f'400 Bad Request con detalles: {required_fields}')
    else:
        test_result(3, 'ERROR', f'Esperaba 400, obtuvo {response.status_code}')

except Exception as e:
    test_result(3, 'ERROR', str(e))

# ============================================================================
# HTTP 4: Datos duplicados (400 o 409 Conflict)
# ============================================================================
print("\n" + "="*80)
print(" HTTP 4: Datos duplicados (esperado: 400/409 Conflict)")
print("="*80)

try:
    # Crear usuario 1
    user1 = create_normal_user()
    user1_id = user1['id']
    
    # Crear postulante 1 con CI específico
    import time
    ts = str(int(time.time()))[-8:]
    ci_duplicado = f'DUP{ts}'
    
    response1 = client.post('/api/postulantes/',
        data=json.dumps({
            'usuario': user1_id,
            'nombre': 'Postulant',
            'apellido': 'One',
            'ci': ci_duplicado,
            'telefono': '5990000000',
            'codigo_estudiante': f'EST1{ts}'
        }),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {admin_token}'
    )
    
    if response1.status_code != 201:
        raise Exception(f"Error creando postulante 1: {response1.status_code}")
    
    print("   ✓ Postulante 1 creado con CI: " + ci_duplicado)
    
    # Intentar crear postulante 2 con mismo CI
    user2 = create_normal_user()
    user2_id = user2['id']
    
    response2 = client.post('/api/postulantes/',
        data=json.dumps({
            'usuario': user2_id,
            'nombre': 'Postulant',
            'apellido': 'Two',
            'ci': ci_duplicado,  # DUPLICADO
            'telefono': '5990000001',
            'codigo_estudiante': f'EST2{ts}'
        }),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {admin_token}'
    )
    
    print(f"   Postulante 2 con CI duplicado: {response2.status_code}")
    
    if response2.status_code in [400, 409]:
        error_msg = response2.json()
        print(f"   Mensaje de error: {error_msg}")
        test_result(4, 'OK', f'{response2.status_code} Conflict - Duplicado controlado')
    else:
        test_result(4, 'ERROR', f'Esperaba 400/409, obtuvo {response2.status_code}')

except Exception as e:
    test_result(4, 'ERROR', str(e))

# ============================================================================
# HTTP 5: ALLOWED_HOSTS correcto (sin DisallowedHost)
# ============================================================================
print("\n" + "="*80)
print(" HTTP 5: ALLOWED_HOSTS correcto (sin DisallowedHost)")
print("="*80)

try:
    endpoints = [
        ('/api/postulantes/', 'GET'),
        ('/api/postulaciones/', 'GET'),
        ('/api/documentos-postulaciones/', 'GET'),
        ('/api/reportes/dashboard-general/', 'GET'),
    ]
    
    has_disallowed_host = False
    success_count = 0
    
    for endpoint, method in endpoints:
        if method == 'GET':
            response = client.get(endpoint, HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        else:
            response = client.post(endpoint, HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        
        # Verificar si hay DisallowedHost en la respuesta
        if response.status_code == 400:
            try:
                body = response.json()
                if 'DisallowedHost' in str(body) or 'DisallowedHost' in response.content.decode():
                    has_disallowed_host = True
                    print(f"   ❌ {endpoint}: DisallowedHost detectado")
            except:
                pass
        
        # Endpoint debería responder (2xx, 4xx, etc - cualquier cosa que no sea 500)
        if response.status_code < 500:
            success_count += 1
            print(f"   ✓ {endpoint}: {response.status_code}")
        else:
            print(f"   ⚠ {endpoint}: {response.status_code}")
    
    if not has_disallowed_host and success_count == len(endpoints):
        test_result(5, 'OK', 'No hay DisallowedHost, todos endpoints responden correctamente')
    elif has_disallowed_host:
        test_result(5, 'ERROR', 'DisallowedHost detectado en respuestas')
    else:
        test_result(5, 'ERROR', f'Solo {success_count}/{len(endpoints)} endpoints respondieron correctamente')

except Exception as e:
    test_result(5, 'ERROR', str(e))

# ============================================================================
# RESUMEN FINAL
# ============================================================================
print("\n" + "="*80)
print(" RESUMEN AUDITORÍA HTTP")
print("="*80)

for test_num in range(1, 6):
    status = results.get(test_num, 'SKIP')
    emoji = "✅" if status == "OK" else "❌" if status == "ERROR" else "⏭️"
    print(f"{emoji} HTTP {test_num}: {status}")

ok_count = sum(1 for v in results.values() if v == "OK")
total = len(results)

print("\n" + "="*80)
print(f" RESULTADO FINAL: {ok_count}/{total} PRUEBAS HTTP ✨")
print("="*80 + "\n")

# Salida para parsing
if ok_count == total:
    print("🎉 TODAS LAS PRUEBAS PASARON")
else:
    print(f"⚠️  {ok_count} de {total} pruebas pasaron")
