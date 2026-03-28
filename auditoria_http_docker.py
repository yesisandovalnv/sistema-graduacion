#!/usr/bin/env python
"""
AUDITORÍA HTTP REAL - Usando urllib
Conectar directamente a backend (no via Nginx) para debug
"""
import json
import sys
import urllib.request
import urllib.error
from datetime import datetime

# Intentar primero backend directo, luego Nginx
API_BASES = [
    'http://sistema_backend:8000/api',  # Directo al backend
    'http://sistema_nginx/api'           # Via Nginx
]

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
            return e.code, {'error': body[:100]}
    except Exception as e:
        raise e

def login_admin(api_base):
    """Obtiene token JWT."""
    try:
        status, data = http_request('POST', f'{api_base}/auth/login/', {
            'username': ADMIN_USER,
            'password': ADMIN_PASS
        })
        if status == 200:
            return data.get('access')
        return None
    except:
        return None

print("\n" + "="*70)
print(" AUDITORÍA HTTP REAL - Sistema Graduación")
print("="*70)

# Detectar API_BASE correcta
API_BASE = None
print("\n🔌 Detectando API disponible...")
for base in API_BASES:
    try:
        status, _ = http_request('GET', f'{base}/postulantes/')
        if status in [200, 400, 401, 403]:  # Respuesta de API (no rechazo de proxy)
            API_BASE = base
            print(f"   ✓ API encontrada en: {base}")
            break
    except:
        continue

if not API_BASE:
    print(f"   ❌ No se pudo conectar a ninguna API")
    sys.exit(1)

# ============================================================================
# HTTP 1: Usuario normal intentar endpoint admin (403)
# ============================================================================
print_section("HTTP 1: Usuario normal vs endpoint admin (403)")

try:
    admin_token = login_admin(API_BASE)
    if not admin_token:
        raise Exception("No se pudo obtener token admin")
    print(f"   ✓ Token admin obtenido")
    
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
        test_result(1, 'ERROR', f'Crear usuario retornó {status_create}')
    else:
        print(f"   ✓ Usuario normal creado")
        
        status_login, data_login = http_request('POST', f'{API_BASE}/auth/login/', {
            'username': normal_user_data['username'],
            'password': 'password123'
        })
        
        if status_login != 200:
            print(f"   ⚠ Usuario normal no puede login: {status_login}")
            test_result(1, 'ERROR', 'Usuario normal no puede login')
        else:
            normal_token = data_login.get('access')
            print(f"   ✓ Token obtenido para usuario normal")
            
            status_admin_ep, _ = http_request('POST', f'{API_BASE}/usuarios/', {
                'username': 'test', 'email': 'test@test.local', 'password': 'test'
            }, token=normal_token)
            
            print(f"   ✓ POST /usuarios/ como normal: {status_admin_ep}")
            
            if status_admin_ep == 403:
                print(f"   ✓ Error 403 Forbidden (correcto)")
                test_result(1, 'OK', 'Usuario normal rechazado con 403')
            else:
                test_result(1, 'ERROR', f'Esperaba 403, obtuvo {status_admin_ep}')

except Exception as e:
    test_result(1, 'ERROR', str(e))

# ============================================================================
# HTTP 2: Token inválido (401)
# ============================================================================
print_section("HTTP 2: Token inválido (401)")

try:
    bad_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.token'
    
    status_bad, _ = http_request('GET', f'{API_BASE}/postulantes/', token=bad_token)
    
    print(f"   ✓ GET /postulantes/ con token inválido: {status_bad}")
    
    if status_bad == 401:
        print(f"   ✓ Error 401 Unauthorized (correcto)")
        test_result(2, 'OK', 'Token inválido rechazado con 401')
    else:
        test_result(2, 'ERROR', f'Esperaba 401, obtuvo {status_bad}')

except Exception as e:
    test_result(2, 'ERROR', str(e))

# ============================================================================
# HTTP 3: Datos incompletos (400)
# ============================================================================
print_section("HTTP 3: Datos incompletos (400 con mensaje claro)")

try:
    admin_token = login_admin(API_BASE)
    if not admin_token:
        raise Exception("No se pudo obtener token admin")
    
    incomplete_data = {
        'nombre': 'Test',
        'apellido': 'Incompleto'
    }
    
    status, error_data = http_request('POST', f'{API_BASE}/postulantes/',
                                      incomplete_data,
                                      token=admin_token)
    
    print(f"   ✓ POST /postulantes/ incompleto: {status}")
    
    if status == 400:
        error_keys = list(error_data.keys()) if isinstance(error_data, dict) else []
        print(f"   ✓ Error 400, campos: {error_keys}")
        test_result(3, 'OK', f'400 con detalles: {error_keys}')
    else:
        test_result(3, 'ERROR', f'Esperaba 400, obtuvo {status}')

except Exception as e:
    test_result(3, 'ERROR', str(e))

# ============================================================================
# HTTP 4: Duplicado (400 o 409)
# ============================================================================
print_section("HTTP 4: Duplicado vía API (400/409)")

try:
    admin_token = login_admin(API_BASE)
    if not admin_token:
        raise Exception("No se pudo obtener token admin")
    
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    
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
    print(f"   ✓ Usuario creado")
    
    ts2 = datetime.now().strftime("%Y%m%d_%H%M%S")
    postulante_data = {
        'usuario': user_id,
        'nombre': 'Test',
        'apellido': 'Dup',
        'ci': f'DUP{ts2}',
        'telefono': '5990000000',
        'codigo_estudiante': f'DUP_{ts2}'
    }
    
    status1, data1 = http_request('POST', f'{API_BASE}/postulantes/',
                                  postulante_data,
                                  token=admin_token)
    
    if status1 != 201:
        print(f"   ⚠ No se pudo crear postulante: {status1}")
        test_result(4, 'ERROR', f'Crear postulante retornó {status1}')
    else:
        print(f"   ✓ Postulante creado")
        
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
            'apellido': 'Dup2',
            'ci': f'DUP{ts2}',  # DUPLICADO
            'telefono': '5990000001',
            'codigo_estudiante': f'DUP2_{ts3}'
        }
        
        status2, data2 = http_request('POST', f'{API_BASE}/postulantes/',
                                      postulante_dup_data,
                                      token=admin_token)
        
        print(f"   ✓ POST duplicado: {status2}")
        
        if status2 in [400, 409]:
            print(f"   ✓ Error {status2} retornado")
            test_result(4, 'OK', f'Duplicado controlado con {status2}')
        else:
            test_result(4, 'ERROR', f'Esperaba 400/409, obtuvo {status2}')

except Exception as e:
    test_result(4, 'ERROR', str(e))

# ============================================================================
# HTTP 5: ALLOWED_HOSTS correcto
# ============================================================================
print_section("HTTP 5: ALLOWED_HOSTS correcto (sin DisallowedHost)")

try:
    admin_token = login_admin(API_BASE)
    if not admin_token:
        raise Exception("No se pudo obtener token admin")
    
    endpoints = [
        '/postulantes/',
        '/postulaciones/',
        '/documentos-postulaciones/',
        '/reportes/dashboard-general/',
    ]
    
    all_ok = True
    for endpoint in endpoints:
        try:
            status, data = http_request('GET', f'{API_BASE}{endpoint}',
                                       token=admin_token)
            
            if isinstance(data, dict) and 'DisallowedHost' in str(data):
                print(f"   ❌ DisallowedHost en {endpoint}")
                all_ok = False
            elif status in [200, 400, 401, 403, 404]:
                print(f"   ✓ {endpoint}: {status}")
            else:
                print(f"   ⚠ {endpoint}: {status}")
        except Exception as e:
            print(f"   ⚠ {endpoint}: {e}")
            all_ok = False
    
    if all_ok:
        print(f"   ✓ ALLOWED_HOSTS OK")
        test_result(5, 'OK', 'No hay DisallowedHost, endpoints respondiendo')
    else:
        test_result(5, 'ERROR', 'DisallowedHost detectado')

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
print(f"{'='*70}")
print(f"API usado: {API_BASE}\n")
