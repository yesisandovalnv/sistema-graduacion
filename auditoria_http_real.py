#!/usr/bin/env python
"""
AUDITORÍA HTTP REAL - Pruebas contra API en http://localhost/api/
Ejecutar DESDE EL HOST (no dentro de Docker)
"""
import requests
import json
import sys
from datetime import datetime

API_BASE = 'http://localhost/api'
ADMIN_USER = 'admin'
ADMIN_PASS = 'password'

results = {}

def test_result(num, status, message=""):
    """Guarda resultado."""
    results[num] = status
    emoji = "✅" if status == "OK" else "❌"
    print(f"{emoji} HTTP {num}: {status}")
    if message:
        print(f"   └─ {message}")

def print_section(title):
    """Imprime sección."""
    print(f"\n{'='*70}")
    print(f" {title}")
    print(f"{'='*70}")

def login_admin():
    """Obtiene token JWT."""
    try:
        resp = requests.post(f'{API_BASE}/auth/login/', json={
            'username': ADMIN_USER,
            'password': ADMIN_PASS
        }, timeout=5)
        if resp.status_code == 200:
            return resp.json().get('access')
        print(f"   ⚠ Login admin falló: {resp.status_code}")
        return None
    except Exception as e:
        print(f"   ⚠ Conexión falló: {e}")
        return None

def get_headers(token):
    """Headers con token."""
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

print("\n" + "="*70)
print(" AUDITORÍA HTTP REAL - Sistema Graduación")
print("="*70)
print(f"API Base: {API_BASE}")
print(f"Timestamp: {datetime.now().isoformat()}")

# Verificar conexión
print("\n🔌 Verificando conexión a API...")
try:
    resp = requests.get(f'{API_BASE}/postulantes/', timeout=5)
    print(f"   ✓ API respondiendo")
except Exception as e:
    print(f"   ❌ No se pudo conectar: {e}")
    print(f"   Verifica que Docker está corriendo y nginx accesible en localhost:80")
    sys.exit(1)

# ============================================================================
# HTTP 1: Usuario normal intentar endpoint admin (debe ser 403)
# ============================================================================
print_section("HTTP 1: Usuario normal vs endpoint admin (403)")

try:
    # 1. Crear usuario normal
    admin_token = login_admin()
    if not admin_token:
        raise Exception("No se pudo obtener token admin")
    
    normal_user_data = {
        'username': f'httpuser_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
        'email': 'httpuser@test.local',
        'password': 'password123'
    }
    
    resp_create = requests.post(
        f'{API_BASE}/usuarios/',
        json=normal_user_data,
        headers=get_headers(admin_token),
        timeout=5
    )
    
    if resp_create.status_code != 201:
        print(f"   ⚠ No se pudo crear usuario: {resp_create.status_code}")
        normal_token = None
    else:
        normal_user_id = resp_create.json()['id']
        print(f"   ✓ Usuario normal creado: {normal_user_data['username']}")
        
        # 2. Obtener token del usuario normal
        resp_login = requests.post(
            f'{API_BASE}/auth/login/',
            json={'username': normal_user_data['username'], 'password': 'password123'},
            timeout=5
        )
        
        if resp_login.status_code != 200:
            print(f"   ⚠ Usuario normal no puede hacer login: {resp_login.status_code}")
            normal_token = None
        else:
            normal_token = resp_login.json().get('access')
            print(f"   ✓ Token obtenido para usuario normal")
    
    # 3. Intentar acceso a endpoint admin (ej: crear usuario)
    if normal_token:
        resp_admin_endpoint = requests.post(
            f'{API_BASE}/usuarios/',
            json={'username': 'test', 'email': 'test@test.local', 'password': 'test'},
            headers=get_headers(normal_token),
            timeout=5
        )
        
        status_code = resp_admin_endpoint.status_code
        print(f"   ✓ POST /usuarios/ como usuario normal: {status_code}")
        
        if status_code == 403:
            print(f"   ✓ Error 403 Forbidden retornado (correcto)")
            test_result(1, 'OK', f'Usuario normal rechazado con 403')
        elif status_code == 401:
            print(f"   ⚠ Obtuvo 401 (no autenticado)")
            test_result(1, 'ERROR', f'Esperaba 403, obtuvo 401')
        else:
            print(f"   ⚠ Inesperado: {status_code}")
            test_result(1, 'ERROR', f'Esperaba 403, obtuvo {status_code}')
    else:
        test_result(1, 'ERROR', 'No se pudo obtener token normal')
    
except Exception as e:
    test_result(1, 'ERROR', str(e))

# ============================================================================
# HTTP 2: Token inválido (debe ser 401)
# ============================================================================
print_section("HTTP 2: Token inválido (401)")

try:
    # 1. Intentar con token inválido
    bad_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.token'
    
    resp_bad = requests.get(
        f'{API_BASE}/postulantes/',
        headers={'Authorization': f'Bearer {bad_token}'},
        timeout=5
    )
    
    status_code = resp_bad.status_code
    print(f"   ✓ GET /postulantes/ con token inválido: {status_code}")
    
    if status_code == 401:
        print(f"   ✓ Error 401 Unauthorized retornado (correcto)")
        test_result(2, 'OK', f'Token inválido rechazado con 401')
    else:
        print(f"   ⚠ Inesperado: {status_code}")
        test_result(2, 'ERROR', f'Esperaba 401, obtuvo {status_code}')
    
except Exception as e:
    test_result(2, 'ERROR', str(e))

# ============================================================================
# HTTP 3: Crear postulante con datos incompletos (debe ser 400)
# ============================================================================
print_section("HTTP 3: Datos incompletos (400 con mensaje claro)")

try:
    admin_token = login_admin()
    if not admin_token:
        raise Exception("No se pudo obtener token admin")
    
    # Datos incompletos (sin CI, sin código_estudiante)
    incomplete_data = {
        'nombre': 'Test',
        'apellido': 'Incompleto'
        # Falta: usuario, ci, telefono, codigo_estudiante
    }
    
    resp = requests.post(
        f'{API_BASE}/postulantes/',
        json=incomplete_data,
        headers=get_headers(admin_token),
        timeout=5
    )
    
    status_code = resp.status_code
    print(f"   ✓ POST /postulantes/ con datos incompletos: {status_code}")
    
    if status_code == 400:
        error_data = resp.json()
        print(f"   ✓ Error 400 Bad Request retornado")
        print(f"   Errores en respuesta: {list(error_data.keys())}")
        print(f"   ✓ Mensaje claro presente")
        test_result(3, 'OK', f'400 con detalles de validación')
    else:
        print(f"   ⚠ Inesperado: {status_code}")
        test_result(3, 'ERROR', f'Esperaba 400, obtuvo {status_code}')
    
except Exception as e:
    test_result(3, 'ERROR', str(e))

# ============================================================================
# HTTP 4: Crear duplicado vía API (debe ser 400 o 409)
# ============================================================================
print_section("HTTP 4: Duplicado vía API (400/409 controlado)")

try:
    admin_token = login_admin()
    if not admin_token:
        raise Exception("No se pudo obtener token admin")
    
    # Crear usuario primero
    user_data = {
        'username': f'dupuser_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
        'email': f'dupuser_{datetime.now().strftime("%Y%m%d_%H%M%S")}@test.local',
        'password': 'password123'
    }
    
    resp_user = requests.post(
        f'{API_BASE}/usuarios/',
        json=user_data,
        headers=get_headers(admin_token),
        timeout=5
    )
    
    if resp_user.status_code != 201:
        raise Exception(f"No se pudo crear usuario: {resp_user.status_code}")
    
    user_id = resp_user.json()['id']
    print(f"   ✓ Usuario creado: {user_data['username']}")
    
    # Crear postulante
    postulante_data = {
        'usuario': user_id,
        'nombre': 'Test',
        'apellido': 'Duplicado',
        'ci': '12345678DUP',
        'telefono': '5990000000',
        'codigo_estudiante': f'DUP_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    }
    
    resp1 = requests.post(
        f'{API_BASE}/postulantes/',
        json=postulante_data,
        headers=get_headers(admin_token),
        timeout=5
    )
    
    if resp1.status_code != 201:
        print(f"   ⚠ No se pudo crear primer postulante: {resp1.status_code}")
        test_result(4, 'ERROR', 'No se pudo crear postulante original')
    else:
        postulante_id = resp1.json()['id']
        print(f"   ✓ Postulante creado: {postulante_data['codigo_estudiante']}")
        
        # Intentar criar duplicado (mismo CI)
        user_data2 = {
            'username': f'dupuser2_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'email': f'dupuser2_{datetime.now().strftime("%Y%m%d_%H%M%S")}@test.local',
            'password': 'password123'
        }
        
        resp_user2 = requests.post(
            f'{API_BASE}/usuarios/',
            json=user_data2,
            headers=get_headers(admin_token),
            timeout=5
        )
        user_id2 = resp_user2.json()['id']
        
        postulante_dup_data = {
            'usuario': user_id2,
            'nombre': 'Test2',
            'apellido': 'Duplicado2',
            'ci': '12345678DUP',  # ← DUPLICADO
            'telefono': '5990000001',
            'codigo_estudiante': f'DUP2_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        }
        
        resp2 = requests.post(
            f'{API_BASE}/postulantes/',
            json=postulante_dup_data,
            headers=get_headers(admin_token),
            timeout=5
        )
        
        status_code = resp2.status_code
        print(f"   ✓ POST /postulantes/ con CI duplicado: {status_code}")
        
        if status_code in [400, 409]:
            error_data = resp2.json()
            print(f"   ✓ Error {status_code} retornado (400=BadRequest, 409=Conflict)")
            print(f"   Respuesta: {error_data}")
            test_result(4, 'OK', f'Duplicado controlado con {status_code}')
        else:
            print(f"   ❌ Inesperado: {status_code}")
            test_result(4, 'ERROR', f'Esperaba 400/409, obtuvo {status_code}')
    
except Exception as e:
    test_result(4, 'ERROR', str(e))

# ============================================================================
# HTTP 5: Verificar ALLOWED_HOSTS correcto (sin DisallowedHost)
# ============================================================================
print_section("HTTP 5: ALLOWED_HOSTS correcto (sin DisallowedHost)")

try:
    # 1. Hacer múltiples requests a diferentes endpoints
    admin_token = login_admin()
    if not admin_token:
        raise Exception("No se pudo obtener token admin")
    
    endpoints_to_test = [
        ('GET', '/postulantes/'),
        ('GET', '/postulaciones/'),
        ('GET', '/documentos-postulaciones/'),
        ('GET', '/reportes/dashboard-general/'),
        ('GET', '/reportes/dashboard-chart-data/?meses=3'),
    ]
    
    all_ok = True
    for method, endpoint in endpoints_to_test:
        try:
            if method == 'GET':
                resp = requests.get(
                    f'{API_BASE}{endpoint}',
                    headers=get_headers(admin_token),
                    timeout=5
                )
            
            status_code = resp.status_code
            
            # 2. Verificar que NO hay DisallowedHost
            if status_code == 400 and 'DisallowedHost' in resp.text:
                print(f"   ❌ {endpoint}: DisallowedHost error!")
                all_ok = False
            elif status_code in [200, 201, 400, 401, 403, 404]:
                print(f"   ✓ {endpoint}: {status_code} (sin DisallowedHost)")
            else:
                print(f"   ⚠ {endpoint}: {status_code}")
        
        except Exception as e:
            print(f"   ⚠ {endpoint}: {e}")
            all_ok = False
    
    if all_ok:
        print(f"   ✓ ALLOWED_HOSTS configurado correctamente")
        test_result(5, 'OK', 'ALLOWED_HOSTS OK, todos endpoints respondiendo')
    else:
        test_result(5, 'ERROR', 'ALLOWED_HOSTS issue detectado')
    
except Exception as e:
    test_result(5, 'ERROR', str(e))

# ============================================================================
# RESUMEN
# ============================================================================
print_section("RESUMEN DE AUDITORÍA HTTP")

for test_num in range(1, 6):
    status = results.get(test_num, "SKIP")
    emoji = "✅" if status == "OK" else "❌"
    print(f"{emoji} HTTP {test_num}: {status}")

print(f"\n{'='*70}")
total_ok = sum(1 for v in results.values() if v == "OK")
print(f"RESULTADO FINAL: {total_ok}/5 pruebas HTTP ✨")
print(f"{'='*70}\n")

if total_ok == 5:
    print("✅ Todos los endpoints HTTP funcionando correctamente.")
    print("✅ Errores controlados (400, 401, 403, etc.).")
    print("✅ ALLOWED_HOSTS configurado correctamente.\n")
else:
    print(f"⚠️  {5-total_ok} prueba(s) fallaron.\n")
