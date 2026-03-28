#!/usr/bin/env python
"""
OPERATIVO 2: Crear 10 postulantes seguidos - Verificar estabilidad del sistema
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.test import Client
import json
import time
from datetime import datetime

print("\n" + "="*70)
print(" OPERATIVO 2: 10 CREACIONES SEGUIDAS DE POSTULANTES")
print("="*70)

client = Client()
start_time = time.time()

# Login admin
response = client.post('/api/auth/login/', 
    data=json.dumps({'username': 'admin', 'password': 'password'}),
    content_type='application/json'
)
admin_token = response.json().get('access')

if not admin_token:
    print("❌ No se pudo obtener token admin")
    exit(1)

print("\n🔧 Setup: Token admin obtenido")

# Crear 10 usuarios y postulantes
successful = 0
failed = 0
timings = []

for i in range(1, 11):
    iter_start = time.time()
    
    try:
        # Crear usuario
        ts = str(int(time.time()))[-8:] + f"_{i}"
        username = f'user_op2_{ts}'
        
        user_resp = client.post('/api/usuarios/',
            data=json.dumps({
                'username': username,
                'email': f'{username}@test.local',
                'password': 'password123',
                'role': 'estudiante'
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {admin_token}'
        )
        
        if user_resp.status_code != 201:
            raise Exception(f"User creation failed: {user_resp.status_code}")
        
        user_id = user_resp.json()['id']
        
        # Crear postulante
        post_resp = client.post('/api/postulantes/',
            data=json.dumps({
                'usuario': user_id,
                'nombre': f'User {i}',
                'apellido': f'Operativo2',
                'ci': f'OP2{ts}',
                'telefono': f'599000{i:04d}',
                'codigo_estudiante': f'EST_OP2_{ts}'
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {admin_token}'
        )
        
        if post_resp.status_code != 201:
            raise Exception(f"Postulant creation failed: {post_resp.status_code}")
        
        iter_time = time.time() - iter_start
        timings.append(iter_time)
        successful += 1
        
        print(f"   ✅ Iteración {i:2d}: Postulante creado (usuario: {user_id}, {iter_time:.3f}s)")
        
    except Exception as e:
        failed += 1
        iter_time = time.time() - iter_start
        timings.append(iter_time)
        print(f"   ❌ Iteración {i:2d}: Error - {str(e)[:50]} ({iter_time:.3f}s)")

total_time = time.time() - start_time
avg_time = sum(timings) / len(timings) if timings else 0
min_time = min(timings) if timings else 0
max_time = max(timings) if timings else 0

print("\n" + "="*70)
print(" RESUMEN OPERATIVO 2")
print("="*70)
print(f"✅ Exitosas: {successful}/10")
print(f"❌ Fallidas: {failed}/10")
print(f"⏱️  Tiempo total: {total_time:.2f}s")
print(f"   Promedio: {avg_time:.3f}s/creación")
print(f"   Mínimo: {min_time:.3f}s")
print(f"   Máximo: {max_time:.3f}s")
print("="*70 + "\n")

if successful == 10 and failed == 0:
    print("🎉 OPERATIVO 2: OK - Todas las creaciones exitosas")
else:
    print(f"⚠️  OPERATIVO 2: ERROR - {failed} fallos detectados")
