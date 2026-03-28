#!/usr/bin/env python
"""
Test Script: Verificar endpoint /api/reportes/dashboard-chart-data/
Verifica que el endpoint devuelva datos reales del backend.
"""
import os
import sys
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from postulantes.models import Postulacion
from django.db.models import Count, Q
from django.utils import timezone

print("═" * 80)
print("🧪 TEST: Verificar endpoint /api/reportes/dashboard-chart-data/")
print("═" * 80)

# ===== 1. Verificar datos en base de datos =====
print("\n1️⃣ VERIFICAR DATOS EN BASE DE DATOS:")
print("─" * 80)

total_postulaciones = Postulacion.objects.count()
print(f"   📊 Total postulaciones: {total_postulaciones}")

if total_postulaciones == 0:
    print("   ⚠️  ADVERTENCIA: NO HAY POSTULACIONES EN LA BASE DE DATOS")
    print("   ► Ejecuta: python generate_test_data.py")
else:
    # Mostrar distribución por estado
    estados_stats = Postulacion.objects.values('estado_general').annotate(
        total=Count('id')
    ).order_by('-total')
    
    print("   📈 Distribución por estado:")
    for estado_item in estados_stats:
        estado = estado_item.get('estado_general', 'DESCONOCIDO')
        total = int(estado_item.get('total', 0))
        print(f"      • {estado}: {total}")

# ===== 2. Probar la función de backend =====
print("\n2️⃣ PROBAR FUNCIÓN get_dashboard_chart_data():")
print("─" * 80)

try:
    from reportes.services import get_dashboard_chart_data
    
    chart_data = get_dashboard_chart_data(meses=6)
    
    print("   ✅ Función ejecutada exitosamente")
    print(f"\n   📊 pieChartData (Distribución de Estados):")
    if chart_data.get('pieChartData'):
        for item in chart_data['pieChartData']:
            print(f"      • {item['name']}: {item['value']} (color: {item['color']})")
    else:
        print("      ❌ pieChartData vacío o no existe")
    
    print(f"\n   📊 barChartData (Postulantes & Documentos):")
    if chart_data.get('barChartData'):
        for item in chart_data['barChartData'][:3]:
            print(f"      • {item['semana']}: postulantes={item['postulantes']}, documentos={item['documentos']}")
        if len(chart_data['barChartData']) > 3:
            print(f"      • ... y {len(chart_data['barChartData']) - 3} más")
    else:
        print("      ❌ barChartData vacío o no existe")
    
    print(f"\n   📊 lineChartData (Progreso por Mes):")
    if chart_data.get('lineChartData'):
        for item in chart_data['lineChartData'][:3]:
            print(f"      • {item['mes']}: graduados={item['graduados']}, aprobados={item['aprobados']}, pendientes={item['pendientes']}")
        if len(chart_data['lineChartData']) > 3:
            print(f"      • ... y {len(chart_data['lineChartData']) - 3} más")
    else:
        print("      ❌ lineChartData vacío o no existe")
        
except Exception as e:
    print(f"   ❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

# ===== 3. Probar la vista =====
print("\n3️⃣ PROBAR VISTA DashboardChartDataView:")
print("─" * 80)

try:
    from rest_framework.test import APIRequestFactory
    from rest_framework_simplejwt.tokens import RefreshToken
    from reportes.views import DashboardChartDataView
    
    # Crear usuario de prueba
    test_user, _ = User.objects.get_or_create(
        username='test_dashboard',
        defaults={'is_active': True}
    )
    
    # Crear request autenticado
    factory = APIRequestFactory()
    request = factory.get('/api/reportes/dashboard-chart-data/?meses=6')
    request.user = test_user
    
    # Llamar la vista
    view = DashboardChartDataView.as_view()
    response = view(request)
    
    print(f"   📡 Response status: {response.status_code}")
    print(f"   ✅ Vista ejecutada exitosamente")
    
    if hasattr(response, 'data'):
        data = response.data
        
        print(f"\n   📊 pieChartData (desde vista):")
        if data.get('pieChartData'):
            for item in data['pieChartData']:
                print(f"      • {item['name']}: {item['value']}")
        else:
            print(f"      ❌ Vacío")
    
except Exception as e:
    print(f"   ❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "═" * 80)
print("✅ TEST COMPLETADO")
print("═" * 80)
print("\n📖 Siguiente paso:")
print("   1. Abre el navegador → Dashboard")
print("   2. Abre DevTools → Console (F12)")
print("   3. Haz clic en el botón 'Actualizar'")
print("   4. Busca los logs [CHARTS] para ver qué recibe el frontend")
print("═" * 80)
