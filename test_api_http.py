#!/usr/bin/env python
"""
Test Script: Verificar endpoint HTTP en puerto 8000
(como lo hace el frontend desde el navegador)
"""
import requests
import json
import sys

print("\n" + "="*70)
print("🧪 TEST: Verificar endpoint HTTP /api/reportes/dashboard-general/")
print("="*70 + "\n")

# Credenciales
USERNAME = 'admin'
PASSWORD = 'password'

try:
    # 1. Obtener token
    print("[1/3] 🔑 Obteniendo token de autenticación...")
    token_url = 'http://localhost:8000/api/token/'
    token_response = requests.post(token_url, json={
        'username': USERNAME,
        'password': PASSWORD
    }, timeout=5)
    
    if token_response.status_code != 200:
        print(f"❌ Error obteniendo token: {token_response.status_code}")
        print(f"   Response: {token_response.text}")
        sys.exit(1)
    
    token_data = token_response.json()
    access_token = token_data.get('access')
    
    if not access_token:
        print("❌ No se recibió access token")
        sys.exit(1)
    
    print(f"✅ Token obtenido: {access_token[:30]}...")
    
    # 2. Llamar endpoint dashboard-general
    print("\n[2/3] 📊 Llamando /api/reportes/dashboard-general/...")
    dashboard_url = 'http://localhost:8000/api/reportes/dashboard-general/'
    dashboard_response = requests.get(
        dashboard_url,
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        },
        timeout=5
    )
    
    if dashboard_response.status_code != 200:
        print(f"❌ Error en endpoint: {dashboard_response.status_code}")
        print(f"   Response: {dashboard_response.text}")
        sys.exit(1)
    
    dashboard_data = dashboard_response.json()
    print(f"✅ Endpoint respondió (Status: {dashboard_response.status_code})")
    
    # 3. Verificar métricas
    print("\n[3/3] 🔍 Verificando que las métricas estén presentes...")
    
    required_metrics = [
        ('total_postulantes', 'Total Postulantes'),
        ('total_postulaciones', 'Total Postulaciones'),
        ('total_documentos', 'Total Documentos'),
        ('total_titulados', 'Total Titulados'),
        ('tasa_aprobacion', 'Tasa de Aprobación'),
        ('promedio_procesamiento_dias', 'Promedio Procesamiento (días)'),
        ('satisfaccion_score', 'Satisfacción'),
        ('proyeccion_mes_porcentaje', 'Proyección Mes'),
    ]
    
    print("\n📋 MÉTRICAS RECIBIDAS:")
    print("-" * 70)
    
    all_present = True
    for key, label in required_metrics:
        if key in dashboard_data:
            value = dashboard_data[key]
            print(f"   ✅ {label:30} = {value}")
        else:
            print(f"   ❌ {label:30} = [FALTA]")
            all_present = False
    
    print("\n" + "="*70)
    if all_present:
        print("✅ TODO CORRECTO - Todas las métricas presentes")
        print("="*70)
        print("\n📡 RESPONSE JSON COMPLETO:")
        print(json.dumps(dashboard_data, indent=2, ensure_ascii=False))
        print("\n" + "="*70)
        print("✨ DASHBOARD FUNCIONAL - Listo para el navegador")
        print("="*70 + "\n")
    else:
        print("❌ FALTAN ALGUNAS MÉTRICAS")
        print("="*70 + "\n")
        sys.exit(1)
        
except requests.exceptions.ConnectionError:
    print("❌ No se puede conectar a http://localhost:8000")
    print("   ¿El servidor Django está corriendo?")
    print("   Intenta: python manage.py runserver")
    sys.exit(1)
    
except requests.exceptions.Timeout:
    print("❌ Timeout: El servidor tardó demasiado")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Error inesperado: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
