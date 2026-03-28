#!/usr/bin/env python
"""
DIAGNOSTICO DEL PIE CHART - Flujo preciso
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from reportes.services import get_dashboard_chart_data

print("\n" + "="*80)
print("DIAGNOSTICO COMPLETO DEL PIE CHART")
print("="*80 + "\n")

print("PASO 1: DEFINICION INICIAL")
print("-" * 80)
print("Archivo: frontend/src/components/Charts.jsx")
print("Linea 28-32: mockPieChartData definido como:")
print("""
const mockPieChartData = [
  { name: 'Completado', value: 45, color: '#10b981' },
  { name: 'En Proceso', value: 30, color: '#f59e0b' },
  { name: 'Por Revisar', value: 15, color: '#3b82f6' },
  { name: 'Rechazado', value: 10, color: '#ef4444' },
];
""")
print("RESULTADO: Pie chart INICIA mostrando 45%, 30%, 15%, 10%")

print("\nPASO 2: INICIALIZACION DEL STATE")
print("-" * 80)
print("Linea 41: const [pieChartData, setPieChartData] = useState(mockPieChartData);")
print("RESULTADO: pieChartData = mockPieChartData (45%, 30%, 15%, 10%)")

print("\nPASO 3: RENDERIZADO DEL PIE CHART")
print("-" * 80)
print("Linea 221: <Pie data={pieChartData}")
print("Linea 222: label={({ name, value }) => `${name}: ${value}%`}")
print("RESULTADO: Pie chart mostra los valores de pieChartData")
print("           Si es mock -> 45%, 30%, 15%, 10%")
print("           Si es backend -> datos del backend")

print("\nPASO 4: FETCH DEL BACKEND (useEffect)")
print("-" * 80)
print("Linea 43: const token = localStorage.getItem('access_token');")
print("Linea 44: if (!token) { return; } <- SI NO HAY TOKEN, RETORNA AQUI")
print("Resultado hasta aqui: pieChartData sigue siendo mockData")
print("")
print("Linea 51: const response = await fetch('/api/reportes/dashboard-chart-data/?meses=6', ...)")
print("Linea 58: if (response.ok) { ... }")
print("         SI RESPONSE NO ES 200 OK -> NO EJECUTA fetchChartData")
print("         Resultado: pieChartData sigue siendo mockData")
print("")
print("Linea 81: if (data.pieChartData) { <- AQUI VERIFICA SI BACKEND DEVUELVE DATOS")
backend_data = get_dashboard_chart_data(meses=6)

if backend_data.get('pieChartData'):
    print("VERIFICACION: Backend SI devuelve pieChartData:")
    for item in backend_data['pieChartData']:
        print("  - " + item['name'].ljust(15) + " valor: " + str(item['value']))
    
    backend_pie = backend_data['pieChartData']
    total = sum(item['value'] for item in backend_pie)
    
    print("\nPASO 5: TRANSFORMACION A PORCENTAJES (Linea 85-90)")
    print("-" * 80)
    print("Javascript:")
    print("  const total = data.pieChartData.reduce(...) = " + str(total))
    print("  const pieDataWithPercentages = data.pieChartData.map(item => ({")
    print("    ...item,")
    print("    value: (item.value / total) * 100")
    print("  }))")
    print("  setPieChartData(pieDataWithPercentages);")
    print("")
    print("Simulacion:")
    for item in backend_pie:
        percentage = (item['value'] / total) * 100
        print("  - " + item['name'].ljust(15) + " " + str(item['value']).rjust(2) + " / " + str(total) + " * 100 = " + str(round(percentage, 1)) + "%")
    
    print("\nPASO 6: RESULTADO EN PIE CHART")
    print("-" * 80)
    print("setPieChartData se llama con datos transformados")
    print("Pie chart renderiza: DATOS DEL BACKEND (no mock)")
    transformed_values = []
    for item in backend_pie:
        percentage = (item['value'] / total) * 100
        transformed_values.append(str(round(percentage, 1)) + "%")
    
    print("Valores mostrados: " + ", ".join(transformed_values))
    
    print("\n" + "="*80)
    print("DIAGNOSTICO FINAL")
    print("="*80)
    print("Si el pie chart muestra 45%, 30%, 15%, 10% (MOCK):")
    print("  -> Una de estas causas es el problema:")
    print("     1. Si no hay token en localStorage (retorna en linea 47-48)")
    print("     2. Si backend retorna error (response.ok = false)")
    print("     3. Si backend retorna pieChartData vacio")
    print("     4. Si hay error en JavaScript (catch en linea 97)")
    print("     5. Si setPieChartData no se llama")
    print("")
    print("Si el pie chart muestra " + ", ".join(transformed_values) + " (REAL):")
    print("  -> TODO FUNCIONA CORRECTAMENTE")

else:
    print("ERROR: Backend NO devuelve pieChartData")

print("\n" + "="*80 + "\n")
