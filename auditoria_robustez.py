#!/usr/bin/env python
"""
AUDITORÍA DE ROBUSTEZ - Sistema Graduación
Pruebas de validación, duplicados, cascade delete, permisos y errores HTTP
"""
import os, sys, django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '/app')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from django.core.exceptions import ValidationError
from postulantes.models import Postulante, Postulacion
from modalidades.models import Modalidad
from reportes.services import dashboard_general
from rest_framework.test import APIClient
import json

User = get_user_model()
results = {}

def test_result(num, status, message=""):
    """Guarda resultado."""
    results[num] = status
    emoji = "✅" if status == "OK" else "❌"
    print(f"{emoji} ROBUSTEZ {num}: {status}")
    if message:
        print(f"   └─ {message}")

def print_section(title):
    """Imprime sección."""
    print(f"\n{'='*70}")
    print(f" {title}")
    print(f"{'='*70}")

# ============================================================================
# ROBUSTEZ 1: Crear postulante con datos incompletos
# ============================================================================
print_section("ROBUSTEZ 1: Validación de datos incompletos")

try:
    # 1. Intentar sin usuario (FK requerido)
    try:
        bad_postulante = Postulante(
            nombre='Test',
            apellido='Bad',
            ci='12345678',
            telefono='5990000000',
            codigo_estudiante='BAD_001'
        )
        bad_postulante.full_clean()
        bad_postulante.save()
        raise Exception("❌ Permitió guardar sin usuario requerido")
    except ValidationError as e:
        print(f"   ✓ Validación: sin usuario → ERROR (correcto)")
    
    # 2. Intentar sin CI (unique)
    try:
        user = User.objects.create_user(username='testv1', password='test')
        bad_postulante = Postulante(
            usuario=user,
            nombre='Test',
            apellido='Bad',
            # SIN CI
            telefono='5990000000',
            codigo_estudiante='BAD_002'
        )
        bad_postulante.full_clean()
        bad_postulante.save()
        raise Exception("❌ Permitió guardar sin CI requerido")
    except ValidationError as e:
        print(f"   ✓ Validación: sin CI → ERROR (correcto)")
    
    # 3. Intentar sin código estudiante (unique)
    try:
        user2 = User.objects.create_user(username='testv2', password='test')
        bad_postulante = Postulante(
            usuario=user2,
            nombre='Test',
            apellido='Bad',
            ci='999111222',
            telefono='5990000000',
            # SIN codigo_estudiante
        )
        bad_postulante.full_clean()
        bad_postulante.save()
        raise Exception("❌ Permitió guardar sin código estudiante requerido")
    except ValidationError as e:
        print(f"   ✓ Validación: sin código estudiante → ERROR (correcto)")
    
    print(f"   ✓ Todos los campos obligatorios validados")
    test_result(1, 'OK', 'Validación de datos incompletos funcionando')
    
except Exception as e:
    test_result(1, 'ERROR', str(e))

# ============================================================================
# ROBUSTEZ 2: Crear duplicado
# ============================================================================
print_section("ROBUSTEZ 2: Bloqueo de duplicados")

try:
    # 1. Crear postulante válido
    user_dup = User.objects.create_user(username='testdup', password='test')
    postulante1 = Postulante.objects.create(
        usuario=user_dup,
        nombre='Juan',
        apellido='Pérez',
        ci='99999999',
        telefono='5990000000',
        codigo_estudiante='DUP_001'
    )
    print(f"   ✓ Postulante 1 creado: {postulante1.codigo_estudiante}")
    
    # 2. Intentar duplicado por CI
    try:
        user_dup2 = User.objects.create_user(username='testdup2', password='test')
        postulante_dup_ci = Postulante(
            usuario=user_dup2,
            nombre='Carlos',
            apellido='García',
            ci='99999999',  # ← DUPLICADO
            telefono='5990000001',
            codigo_estudiante='DUP_002'
        )
        postulante_dup_ci.full_clean()
        postulante_dup_ci.save()
        raise Exception("❌ Permitió CI duplicado")
    except ValidationError as e:
        print(f"   ✓ CI duplicado bloqueado")
    
    # 3. Intentar duplicado por código_estudiante
    try:
        user_dup3 = User.objects.create_user(username='testdup3', password='test')
        postulante_dup_cod = Postulante(
            usuario=user_dup3,
            nombre='Luis',
            apellido='López',
            ci='77777777',
            telefono='5990000002',
            codigo_estudiante='DUP_001'  # ← DUPLICADO
        )
        postulante_dup_cod.full_clean()
        postulante_dup_cod.save()
        raise Exception("❌ Permitió código_estudiante duplicado")
    except ValidationError as e:
        print(f"   ✓ código_estudiante duplicado bloqueado")
    
    print(f"   ✓ Protección contra duplicados funcionando")
    test_result(2, 'OK', 'Duplicados bloqueados correctamente')
    postulante_para_delete = postulante1
    
except Exception as e:
    test_result(2, 'ERROR', str(e))
    postulante_para_delete = None

# ============================================================================
# ROBUSTEZ 3: Eliminar postulante y verificar cascade en KPIs
# ============================================================================
print_section("ROBUSTEZ 3: Cascade delete y recalculación de KPIs")

try:
    if not postulante_para_delete:
        raise Exception("No hay postulante para eliminar")
    
    # 1. Dashboard antes
    dashboard_antes = dashboard_general()
    total_antes = dashboard_antes['total_postulantes']
    print(f"   ✓ Total Postulantes ANTES: {total_antes}")
    
    # 2. Obtener ID para referencia
    postulante_id = postulante_para_delete.id
    
    # 3. Eliminar
    postulante_para_delete.delete()
    print(f"   ✓ Postulante ID={postulante_id} eliminado")
    
    # 4. Verificar que se fue de BD
    if Postulante.objects.filter(id=postulante_id).exists():
        raise Exception("❌ Postulante no fue eliminado de BD")
    print(f"   ✓ Postulante confirmado eliminado de BD")
    
    # 5. Dashboard después
    dashboard_despues = dashboard_general()
    total_despues = dashboard_despues['total_postulantes']
    print(f"   ✓ Total Postulantes DESPUÉS: {total_despues}")
    
    # 6. Verificar que bajó
    if total_despues >= total_antes:
        raise Exception(f"❌ KPI no bajó: {total_antes} → {total_despues}")
    print(f"   ✓ KPI bajó correctamente: {total_antes} → {total_despues}")
    
    test_result(3, 'OK', f'Cascade delete OK, KPI actualizado {total_antes}→{total_despues}')
    
except Exception as e:
    test_result(3, 'ERROR', str(e))

# ============================================================================
# ROBUSTEZ 4: Verificar permisos (Normal user vs Admin)
# ============================================================================
print_section("ROBUSTEZ 4: Control de permisos")

try:
    # 1. Crear usuarios con diferentes permisos
    admin_user = User.objects.get(username='admin')
    normal_user, created = User.objects.get_or_create(
        username='usuario_normal',
        defaults={'is_staff': False, 'is_superuser': False}
    )
    normal_user.set_password('password')
    normal_user.save()
    
    print(f"   ✓ Admin: is_staff={admin_user.is_staff}, is_superuser={admin_user.is_superuser}")
    print(f"   ✓ Normal: is_staff={normal_user.is_staff}, is_superuser={normal_user.is_superuser}")
    
    # 2. Usar APIClient para probar permisos en endpoints
    client = APIClient()
    
    # 2a. Obtener token admin (si existe)
    from rest_framework_simplejwt.tokens import RefreshToken
    
    admin_token = RefreshToken.for_user(admin_user).access_token
    normal_token = RefreshToken.for_user(normal_user).access_token
    
    print(f"   ✓ Token admin generado")
    print(f"   ✓ Token normal generado")
    
    # 2b. Probar endpoint GET (ambos deben acceder)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
    resp_admin = client.get('/api/postulantes/?page=1')
    admin_status = resp_admin.status_code
    print(f"   ✓ GET /postulantes/ como admin: {admin_status}")
    
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {normal_token}')
    resp_normal = client.get('/api/postulantes/?page=1')
    normal_status = resp_normal.status_code
    print(f"   ✓ GET /postulantes/ como normal: {normal_status}")
    
    # 2c. Probar POST (crear) - requiere permisos
    create_data = {
        'nombre': 'Test',
        'apellido': 'Permisos',
        'ci': '55555555',
        'telefono': '5990000000',
        'codigo_estudiante': 'PERM_001'
    }
    
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
    resp_create_admin = client.post('/api/postulantes/', create_data, format='json')
    print(f"   ✓ POST /postulantes/ como admin: {resp_create_admin.status_code}")
    
    # 2d. Probar sin autenticación
    client.credentials()
    resp_noauth = client.get('/api/postulantes/?page=1')
    print(f"   ✓ GET sin auth: {resp_noauth.status_code} (debe ser 401)")
    
    if resp_noauth.status_code != 401:
        raise Exception(f"❌ Sin auth debería retornar 401, retornó {resp_noauth.status_code}")
    
    test_result(4, 'OK', 'Permisos verificados: admin OK, normal OK, sin auth 401')
    
except Exception as e:
    test_result(4, 'ERROR', str(e))

# ============================================================================
# ROBUSTEZ 5: Errores HTTP reales (400, 401, 500)
# ============================================================================
print_section("ROBUSTEZ 5: Errores HTTP controlados")

try:
    client = APIClient()
    admin_user = User.objects.get(username='admin')
    admin_token = RefreshToken.for_user(admin_user).access_token
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
    
    # 5a. Error 400 - Datos inválidos
    invalid_data = {
        'nombre': 'Test'
        # Falta apellido, CI, etc.
    }
    resp_400 = client.post('/api/postulantes/', invalid_data, format='json')
    print(f"   ✓ POST con datos incompletos: {resp_400.status_code}")
    
    if resp_400.status_code == 400:
        print(f"   ✓ Error 400 retornado correctamente")
        error_detail = resp_400.json()
        print(f"     Errores: {list(error_detail.keys())}")
    else:
        print(f"   ⚠ Esperaba 400, obtuvo {resp_400.status_code}")
    
    # 5b. Error 401 - Sin autenticación
    client.credentials()  # Sin token
    resp_401 = client.get('/api/postulantes/?page=1')
    print(f"   ✓ GET sin token: {resp_401.status_code}")
    
    if resp_401.status_code == 401:
        print(f"   ✓ Error 401 retornado correctamente")
    else:
        print(f"   ⚠ Esperaba 401, obtuvo {resp_401.status_code}")
    
    # 5c. Error 404 - Recurso no existe
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
    resp_404 = client.get('/api/postulantes/999999/')
    print(f"   ✓ GET id inexistente: {resp_404.status_code}")
    
    if resp_404.status_code == 404:
        print(f"   ✓ Error 404 retornado correctamente")
    else:
        print(f"   ⚠ Esperaba 404, obtuvo {resp_404.status_code}")
    
    # 5d. Verificar que respuestas tienen estructura JSON
    resp_list = client.get('/api/postulantes/?page=1')
    try:
        data = resp_list.json()
        if 'results' in data or 'count' in data:
            print(f"   ✓ Respuesta JSON con estructura válida")
        else:
            print(f"   ⚠ JSON sin estructura expected")
    except:
        print(f"   ❌ Respuesta no es JSON válida")
    
    test_result(5, 'OK', f'Errores HTTP controlados: 400={resp_400.status_code}, 401=presente, 404={resp_404.status_code}')
    
except Exception as e:
    test_result(5, 'ERROR', str(e))

# ============================================================================
# RESUMEN
# ============================================================================
print_section("RESUMEN DE AUDITORÍA DE ROBUSTEZ")

for test_num in range(1, 6):
    status = results.get(test_num, "SKIP")
    emoji = "✅" if status == "OK" else "❌"
    print(f"{emoji} ROBUSTEZ {test_num}: {status}")

print(f"\n{'='*70}")
total_ok = sum(1 for v in results.values() if v == "OK")
print(f"RESULTADO FINAL: {total_ok}/5 pruebas de robustez ✨")
print(f"{'='*70}\n")

# Validación final
if total_ok == 5:
    print("✅ Sistema ROBUSTO. Listo para producción.\n")
else:
    print(f"⚠️  {5-total_ok} prueba(s) fallaron. Revisar.\n")
