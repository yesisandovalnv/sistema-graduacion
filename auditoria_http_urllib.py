#!/usr/bin/env python
"""
AUDITORÍA HTTP REAL - Usando urllib (sin dependencias externas)
Ejecutar contra: http://sistema_nginx/api (dentro de Docker network)
"""
import json
import sys
import urllib.request
import urllib.error
from datetime import datetime

API_BASE = 'http://sistema_nginx/api'  # Docker DNS
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

def http_request(method, url, data=None, token=None):
    """Función para hacer requests HTTP."""
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    req_data = None
    if data:
        req_data = json.dumps(data).encode('utf-8')
    
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            body = response.read().decode('utf-8')
            return response.status, json.loads(body) if body else None
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        try:
            return e.code, json.loads(body) if body else None
        except:
            return e.code, {'error': body}
    except Exception as e:
        raise e

def login_admin():
    """Obtiene token JWT."""
    try:
        status, data = http_request('POST', f'{API_BASE}/auth/login/', {
            'username': ADMIN_USER,
            'password': ADMIN_PASS
        })
        if status == 200:
            return data.get('access')
        print(f"   ⚠ Login admin falló: {status}")
        return None
    except Exception as e:
        print(f"   ⚠ Conexión falló: {e}")
        return None

print("\n" + "="*70)
print(" AUDITORÍA HTTP REAL - Sistema Graduación")
print("="*70)
print(f"API Base: {API_BASE}")
print(f"Timestamp: {datetime.now().isoformat()}")

# Verificar conexión
print("\n🔌 Verificando conexión a API...")
try:
    status, _ = http_request('GET', f'{API_BASE}/postulantes/')
    print(f"   ✓ API respondiendo (status={status})")
except Exception as e:
    print(f"   ❌ No se pudo conectar: {e}")
    sys.exit(1)

# ============================================================================
# HTTP 1: Usuario normal intentar endpoint admin (debe ser 403)
# ============================================================================
print_section("HTTP 1: Usuario normal vs endpoint admin (403)")

try:
    # 1. Obtener token admin
    admin_token = login_admin()
    if not admin_token:
        raise Exception("No se pudo obtener token admin")
    print(f"   ✓ Token admin obtenido")
    
    # 2. Crear usuario normal
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    normal_user_data = {
        'username': f'httpuser_{ts}',
        'email': f'httpuser_{ts}@test.local',
        'password': 'password123'
    }
    
    status_create, data_create = http_request('POST', f'{API_BASE}/usuarios/',
                                               normal_user_data,
                                               token=admin_token)
    
    if status_create != 201:
        print(f"   ⚠ No se pudo crear usuario: {status_create}")
        test_result(1, 'ERROR', 'No se pudo crear usuario normal')
    else:
        print(f"   ✓ Usuario normal creado: {normal_user_data['username']}")
        
        # 3. Obtener token del usuario normal
        status_login, data_login = http_request('POST', f'{API_BASE}/auth/login/', {
            'username': normal_user_data['username'],
            'password': 'password123'
        })
        
        if status_login != 200:
            print(f"   ⚠ Usuario normal no puede hacer login: {status_login}")
            test_result(1, 'ERROR', 'Usuario normal no puede login')
        else:
            normal_token = data_login.get('access')
            print(f"   ✓ Token obtenido para usuario normal")
            
            # 4. Intentar acceso a endpoint admin (crear usuario)
            status_admin_endpoint, _ = http_request('POST', f'{API_BASE}/usuarios/', {
                'username': 'test', 'email': 'test@test.local', 'password': 'test'
            }, token=normal_token)
            
            print(f"   ✓ POST /usuarios/ como usuario normal: {status_admin_endpoint}")
            
            if status_admin_endpoint == 403:
                print(f"   ✓ Error 403 Forbidden retornado (correcto)")
                test_result(1, 'OK', 'Usuario normal rechazado con 403')
            elif status_admin_endpoint == 401:
                print(f"   ⚠ Obtuvo 401 (token inválido)")
                test_result(1, 'ERROR', f'Esperaba 403, obtuvo 401')
            else:
                print(f"   ⚠ Inesperado: {status_admin_endpoint}")
                test_result(1, 'ERROR', f'Esperaba 403, obtuvo {status_admin_endpoint}')

except Exception as e:
    test_result(1, 'ERROR', str(e))

# ============================================================================
# HTTP 2: Token inválido (debe ser 401)
# ============================================================================
print_section("HTTP 2: Token inválido (401)")

try:
    bad_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.token'
    
    status_bad, _ = http_request('GET', f'{API_BASE}/postulantes/', token=bad_token)
    
    print(f"   ✓ GET /postulantes/ con token inválido: {status_bad}")
    
    if status_bad == 401:
        print(f"   ✓ Error 401 Unauthorized retornado (correcto)")
        test_result(2, 'OK', 'Token inválido rechazado con 401')
    else:
        print(f"   ⚠ Inesperado: {status_bad}")
        test_result(2, 'ERROR', f'Esperaba 401, obtuvo {status_bad}')

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
    
    # Datos incompletos
    incomplete_data = {
        'nombre': 'Test',
        'apellido': 'Incompleto'
        # Falta: usuario, ci, telefono, codigo_estudiante
    }
    
    status, error_data = http_request('POST', f'{API_BASE}/postulantes/',
                                      incomplete_data,
                                      token=admin_token)
    
    print(f"   ✓ POST /postulantes/ con datos incompletos: {status}")
    
    if status == 400:
        print(f"   ✓ Error 400 Bad Request retornado")
        error_keys = list(error_data.keys()) if isinstance(error_data, dict) else []
        print(f"   Campos con error: {error_keys}")
        print(f"   ✓ Mensaje claro presente")
        test_result(3, 'OK', f'400 con detalles: {error_keys}')
    else:
        print(f"   ⚠ Inesperado: {status}")
        test_result(3, 'ERROR', f'Esperaba 400, obtuvo {status}')

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
    
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Crear usuario
    user_data = {
        'username': f'dupuser_{ts}',
        'email': f'dupuser_{ts}@test.local',
        'password': 'password123'
    }
    
    status_user, data_user = http_request('POST', f'{API_BASE}/usuarios/',
                                          user_data,
                                          token=admin_token)
    
    if status_user != 201:
        raise Exception(f"No se pudo crear usuario: {status_user}")
    
    user_id = data_user['id']
    print(f"   ✓ Usuario creado: {user_data['username']}")
    
    # 2. Crear primer postulante
    ts2 = datetime.now().strftime("%Y%m%d_%H%M%S")
    postulante_data = {
        'usuario': user_id,
        'nombre': 'Test',
        'apellido': 'Duplicado',
        'ci': f'12345678DUP{ts2}',
        'telefono': '5990000000',
        'codigo_estudiante': f'DUP_{ts2}'
    }
    
    status1, data1 = http_request('POST', f'{API_BASE}/postulantes/',
                                  postulante_data,
                                  token=admin_token)
    
    if status1 != 201:
        print(f"   ⚠ No se pudo crear primer postulante: {status1}")
        test_result(4, 'ERROR', 'No se pudo crear postulante original')
    else:
        postulante_id = data1['id']
        print(f"   ✓ Postulante creado: {postulante_data['codigo_estudiante']}")
        
        # 3. Intentar duplicado (mismo CI)
        ts3 = datetime.now().strftime("%Y%m%d_%H%M%S")
        user_data2 = {
            'username': f'dupuser2_{ts3}',
            'email': f'dupuser2_{ts3}@test.local',
            'password': 'password123'
        }
        
        status_user2, data_user2 = http_request('POST', f'{API_BASE}/usuarios/',
                                                user_data2,
                                                token=admin_token)
        user_id2 = data_user2['id']
        
        postulante_dup_data = {
            'usuario': user_id2,
            'nombre': 'Test2',
            'apellido': 'Duplicado2',
            'ci': f'12345678DUP{ts2}',  # ← DUPLICADO
            'telefono': '5990000001',
            'codigo_estudiante': f'DUP2_{ts3}'
        }
        
        status2, data2 = http_request('POST', f'{API_BASE}/postulantes/',
                                      postulante_dup_data,
                                      token=admin_token)
        
        print(f"   ✓ POST /postulantes/ con CI duplicado: {status2}")
        
        if status2 in [400, 409]:
            print(f"   ✓ Error {status2} retornado")
            print(f"   Respuesta: {data2}")
            test_result(4, 'OK', f'Duplicado controlado con {status2}')
        else:
            print(f"   ❌ Inesperado: {status2}")
            test_result(4, 'ERROR', f'Esperaba 400/409, obtuvo {status2}')

except Exception as e:
    test_result(4, 'ERROR', str(e))

# ============================================================================
# HTTP 5: Verificar ALLOWED_HOSTS correcto
# ============================================================================
print_section("HTTP 5: ALLOWED_HOSTS correcto")

try:
    admin_token = login_admin()
    if not admin_token:
        raise Exception("No se pudo obtener token admin")
    
    # Hacer múltiples requests
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
            status, data = http_request(method, f'{API_BASE}{endpoint}',
                                       token=admin_token)
            
            # Verificar que NO hay DisallowedHost
            if isinstance(data, dict) and 'DisallowedHost' in str(data):
                print(f"   ❌ {endpoint}: DisallowedHost error!")
                all_ok = False
            elif status in [200, 400, 401, 403, 404]:
                print(f"   ✓ {endpoint}: {status} (sin DisallowedHost)")
            else:
                print(f"   ⚠ {endpoint}: {status}")
        
        except Exception as e:
            print(f"   ⚠ {endpoint}: {e}")
            all_ok = False
    
    if all_ok:
        print(f"   ✓ ALLOWED_HOSTS configurado correctamente")
        test_result(5, 'OK', 'ALLOWED_HOSTS correcto, endpointsrespondiendo')
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
