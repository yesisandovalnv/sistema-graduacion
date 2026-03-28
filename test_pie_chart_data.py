#!/usr/bin/env python
"""
Test para verificar datos del pie chart
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from reportes.services import get_dashboard_chart_data

# Obtener datos del endpoint
dashboard_data = get_dashboard_chart_data(meses=6)

print("\n" + "="*60)
print("📊 DATOS DEL PIE CHART DEL BACKEND")
print("="*60 + "\n")

if dashboard_data.get('pieChartData'):
    pie_data = dashboard_data['pieChartData']
    
    print("✅ pieChartData exists:")
    print(f"   Total items: {len(pie_data)}\n")
    
    total_count = 0
    print("Items recibidos:")
    for item in pie_data:
        print(f"   - {item['name']:15} value={item['value']:3} color={item['color']}")
        total_count += item['value']
    
    print(f"\n   Total Count: {total_count}")
    
    print("\n✅ Cálculo de Porcentajes:")
    for item in pie_data:
        percentage = (item['value'] / total_count * 100) if total_count > 0 else 0
        print(f"   - {item['name']:15} {item['value']:3} registros = {percentage:5.1f}%")
    
else:
    print("❌ No pieChartData en respuesta")

print("\n" + "="*60)
print("💡 RECOMENDACIÓN:")
print("="*60)
print("""
El backend devuelve COUNTS (números absolutos).
Para mostrar porcentajes en el gráfico, debemos:

OPCIÓN A (Backend calcula porcentajes):
  1. Modificar services.py para calcular % en backend
  2. Devolver 'value' como porcentaje (0-100)
  3. El frontend solo muestra el valor

OPCIÓN B (Frontend calcula porcentajes):
  1. Backend devuelve counts (ACTUAL)
  2. Frontend suma total
  3. Frontend calcula % = (value / total) * 100
  4. Muestra como porcentaje

RECOMENDACIÓN: Usar OPCIÓN B (frontend calcula)
porque preserva datos originales en backend.
""")
print("="*60 + "\n")
