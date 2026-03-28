#!/usr/bin/env python
"""
Simula el comportamiento de Charts.jsx para verificar que los datos reales
se retornan correctamente del backend sin valores mock

Este script prueba que:
1. El endpoint devuelve datos reales
2. Los datos tienen valores > 0 (no solo arrays vacíos)
3. La validación funciona correctamente
"""

import os, sys, django, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from reportes.services import get_dashboard_chart_data
from django.utils import timezone

print("\n" + "="*70)
print("🧪 TEST: Simulación del comportamiento de Charts.jsx")
print("="*70)

# 1. Obtener datos como lo haría el endpoint
print("\n1️⃣  Llamando get_dashboard_chart_data()...")
response_data = get_dashboard_chart_data(meses=6)

# 2. Simular la validación que hace Charts.jsx
print("\n2️⃣  Validando datos como lo hace Charts.jsx...")

# Verificar lineChartData
hasLineData = (response_data['lineChartData'] and 
               isinstance(response_data['lineChartData'], list) and 
               len(response_data['lineChartData']) > 0 and
               any((item.get('graduados', 0) or 0) + 
                   (item.get('pendientes', 0) or 0) + 
                   (item.get('aprobados', 0) or 0) > 0 
                   for item in response_data['lineChartData']))

# Verificar barChartData
hasBarData = (response_data['barChartData'] and 
              isinstance(response_data['barChartData'], list) and 
              len(response_data['barChartData']) > 0 and
              any((item.get('postulantes', 0) or 0) + 
                  (item.get('documentos', 0) or 0) > 0 
                  for item in response_data['barChartData']))

# Verificar pieChartData
hasPieData = (response_data['pieChartData'] and 
              isinstance(response_data['pieChartData'], list) and 
              len(response_data['pieChartData']) > 0)

print(f"\n✓ hasLineData (con validación de valores): {hasLineData}")
print(f"✓ hasBarData (con validación de valores): {hasBarData}")
print(f"✓ hasPieData: {hasPieData}")

# 3. Mostrar qué datos serían asignados
print("\n3️⃣  Decisión de actualización de estado...")

if hasLineData:
    print("\n✅ [STATE] setLineChartData() sería llamado")
    print(f"   Primer item: {response_data['lineChartData'][0]}")
    suma = sum((item.get('graduados', 0) or 0) for item in response_data['lineChartData'])
    print(f"   Total graduados: {suma}")
else:
    print("❌ [STATE] setLineChartData() NO sería llamado (mantiene mock)")

if hasBarData:
    print("\n✅ [STATE] setBarChartData() sería llamado")
    print(f"   Primer item: {response_data['barChartData'][0]}")
    suma = sum((item.get('postulantes', 0) or 0) for item in response_data['barChartData'])
    print(f"   Total postulantes: {suma}")
else:
    print("❌ [STATE] setBarChartData() NO sería llamado (mantiene mock)")

if hasPieData:
    print("\n✅ [STATE] setPieChartData() sería llamado")
    print(f"   Primer item: {response_data['pieChartData'][0]}")
    suma = sum((item.get('value', 0) or 0) for item in response_data['pieChartData'])
    print(f"   Total registros: {suma}")
else:
    print("❌ [STATE] setPieChartData() NO sería llamado (mantiene mock)")

# 4. Resumen
print("\n" + "="*70)
print("📊 RESUMEN")
print("="*70)

if hasLineData and hasBarData and hasPieData:
    print("✅ TODOS LOS DATOS SON REALES - Gráficos se actualizarán correctamente")
    print("\nEl usuario verá en Charts:")
    print(f"  - lineChartData: {len(response_data['lineChartData'])} meses con datos reales")
    print(f"  - barChartData: {len(response_data['barChartData'])} semanas con datos reales")
    print(f"  - pieChartData: {len(response_data['pieChartData'])} estados con datos reales")
else:
    print("⚠️  ALGUNOS DATOS NO SON REALES - Se mantendría mock data:")
    if not hasLineData:
        print("  ❌ lineChartData mantendría mock: [45, 72, 98, 125, 145, 156] graduados")
    if not hasBarData:
        print("  ❌ barChartData mantendría mock: [45, 52, 38, 61, 58, 72] postulantes")
    if not hasPieData:
        print("  ❌ pieChartData mantendría mock: [45, 30, 15, 10] valores")

# 5. Response completa as JSON (como React lo recibiría)
print("\n4️⃣  Response JSON como lo recibe Charts.jsx (primeros 2 items):")
print(json.dumps({
    'lineChartData': response_data['lineChartData'][:2],
    'barChartData': response_data['barChartData'][:2],
    'pieChartData': response_data['pieChartData'],
}, indent=2))

print("\n" + "="*70 + "\n")
