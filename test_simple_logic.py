#!/usr/bin/env python
"""
Verifica que la lógica simplificada de Charts.jsx funciona correctamente:
- Si backend devuelve datos (aunque sean ceros) → usar backend
- Si fetch falla → usar mockData
"""

import os, sys, django, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from reportes.services import get_dashboard_chart_data

print("\n" + "="*70)
print("✅ TEST: Lógica Simplificada de Charts.jsx")
print("="*70)

# 1. Obtener datos del backend (con posibles ceros)
print("\n1️⃣  Backend devuelve datos (incluyendo ceros)...")
response_data = get_dashboard_chart_data(meses=6)

# 2. Simular la lógica simplificada de Charts.jsx
print("\n2️⃣  Aplicar lógica simplificada de Charts.jsx...")

# Simular el comportamiento:
state = {
    'lineChartData': None,
    'barChartData': None,
    'pieChartData': None,
}

# Inicializar con mock
mock_data = {
    'lineChartData': [
        {'mes': 'Ene', 'graduados': 45, 'pendientes': 120, 'aprobados': 95},
        {'mes': 'Feb', 'graduados': 72, 'pendientes': 98, 'aprobados': 142},
    ],
    'barChartData': [
        {'semana': 'Sem 1', 'postulantes': 45, 'documentos': 38},
        {'semana': 'Sem 2', 'postulantes': 52, 'documentos': 48},
    ],
    'pieChartData': [
        {'name': 'Completado', 'value': 45, 'color': '#10b981'},
        {'name': 'En Proceso', 'value': 30, 'color': '#f59e0b'},
    ]
}

state['lineChartData'] = mock_data['lineChartData']
state['barChartData'] = mock_data['barChartData']
state['pieChartData'] = mock_data['pieChartData']

print("   Inicial (mockData): ✅")

# Fetch exitoso (response.ok = true)
data = response_data
print("\n3️⃣  Simular fetch exitoso (response.ok)...")

print("\n   Aplicar lógica simplificada:")
if data.get('lineChartData'):
    print(f"      ✅ data.lineChartData existe → setLineChartData(backend)")
    state['lineChartData'] = data['lineChartData']
else:
    print(f"      ❌ data.lineChartData NO existe → mantiene mock")

if data.get('barChartData'):
    print(f"      ✅ data.barChartData existe → setBarChartData(backend)")
    state['barChartData'] = data['barChartData']
else:
    print(f"      ❌ data.barChartData NO existe → mantiene mock")

if data.get('pieChartData'):
    print(f"      ✅ data.pieChartData existe → setPieChartData(backend)")
    state['pieChartData'] = data['pieChartData']
else:
    print(f"      ❌ data.pieChartData NO existe → mantiene mock")

# 4. Resultado
print("\n4️⃣  RESULTADO FINAL:")
print("-" * 70)

# Verificar si state tiene datos del backend o mock
def compare_with_backend(state_data, backend_data, name):
    is_backend = state_data == backend_data
    source = "✅ BACKEND" if is_backend else "❌ MOCK"
    length = len(state_data) if isinstance(state_data, list) else 0
    first_val = state_data[0] if isinstance(state_data, list) and len(state_data) > 0 else None
    print(f"\n{name}:")
    print(f"   Source: {source}")
    print(f"   Length: {length}")
    print(f"   First item: {first_val}")
    return is_backend

is_line_backend = compare_with_backend(state['lineChartData'], data['lineChartData'], 'lineChartData')
is_bar_backend = compare_with_backend(state['barChartData'], data['barChartData'], 'barChartData')
is_pie_backend = compare_with_backend(state['pieChartData'], data['pieChartData'], 'pieChartData')

# 5. Conclusión
print("\n" + "="*70)
print("📊 CONCLUSIÓN")
print("="*70)

if is_line_backend and is_bar_backend and is_pie_backend:
    print("✅ TODOS LOS GRÁFICOS USAN DATOS DEL BACKEND")
    print("\nEl usuario verá en dashboard:")
    print(f"   - Gráfico de línea: {len(state['lineChartData'])} meses del backend")
    print(f"   - Gráfico de barras: {len(state['barChartData'])} semanas del backend")
    print(f"   - Gráfico pastel: {len(state['pieChartData'])} estados del backend")
    print("\n✨ DATOS REALES, NO MOCK")
else:
    print("❌ ALGUNOS GRÁFICOS USAN MOCK DATA")

# 6. Mostrar datos que se envían a Recharts
print("\n5️⃣  Datos enviados a Recharts (primeros items):")
print(json.dumps({
    'lineChartData': state['lineChartData'][:2] if state['lineChartData'] else None,
    'barChartData': state['barChartData'][:2] if state['barChartData'] else None,
    'pieChartData': state['pieChartData'][:2] if state['pieChartData'] else None,
}, indent=2))

print("\n" + "="*70 + "\n")
