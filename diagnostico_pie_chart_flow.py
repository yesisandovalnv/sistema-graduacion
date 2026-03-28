#!/usr/bin/env python
"""
DIAGNÓSTICO DEL PIE CHART

Simular exactamente lo que pasa en Charts.jsx:
1. Estado inicial con mockData
2. Obtener datos del backend
3. Transformar a porcentajes
4. Ver qué se renderiza
"""

import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from reportes.services import get_dashboard_chart_data

print("\n" + "="*80)
print("🔍 DIAGNÓSTICO COMPLETO DEL PIE CHART")
print("="*80 + "\n")

# ============================================================================
print("📍 PASO 1: DEFINICIÓN INICIAL (mockPieChartData) -> CÓDIGO EN LÍNEA 28-32")
print("-" * 80)
mockPieChartData = [
    {"name": "Completado", "value": 45, "color": "#10b981"},
    {"name": "En Proceso", "value": 30, "color": "#f59e0b"},
    {"name": "Por Revisar", "value": 15, "color": "#3b82f6"},
    {"name": "Rechazado", "value": 10, "color": "#ef4444"},
]
print("mockPieChartData = [")
for item in mockPieChartData:
    print(f"  {item},")
print("]")
print(f"\n✅ INICIO: pieChartData = mockPieChartData = {mockPieChartData}")
print("   (Lo que ve el usuario sin backend)")

# ============================================================================
print("\n📍 PASO 2: INICIALIZACIÓN DEL STATE -> CÓDIGO EN LÍNEA 41")
print("-" * 80)
pieChartData = mockPieChartData.copy()
print(f"const [pieChartData, setPieChartData] = useState(mockPieChartData);")
print(f"\n⚠️  pieChartData comienza con mockData:")
print(f"   Valores: 45%, 30%, 15%, 10%")
print(f"   (ESTO ES LO QUE MOSTRÓ INICIALMENTE)")

# ============================================================================
print("\n📍 PASO 3: USO EN PIE CHART -> CÓDIGO EN LÍNEA 221")
print("-" * 80)
print(f"<Pie")
print(f'  data={{pieChartData}')  
print(f'  label={{({{ name, value }}) => `${{name}}: ${{value}}%`}}')
print(f"/>")
print(f"\n⚠️  El pie chart usa directamente pieChartData para renderizar")
print(f"   Si es mockData → muestra 45%, 30%, 15%, 10%")
print(f"   Si es backend data → muestra datos del backend")

# ============================================================================
print("\n📍 PASO 4: FETCH DEL BACKEND -> CÓDIGO EN LÍNEA 43-107")
print("-" * 80)

backend_data = get_dashboard_chart_data(meses=6)

print(f"✅ Backend devuelve pieChartData:")
if backend_data.get('pieChartData'):
    for item in backend_data['pieChartData']:
        print(f"   - {item['name']:15} value: {item['value']:3}")
    
    backend_pie = backend_data['pieChartData']
    
    # ========================================================================
    print("\n📍 PASO 5: TRANSFORMACIÓN (LÍNEAS 85-89)")
    print("-" * 80)
    print("Frontend JavaScript:")
    js_code = """
    const total = data.pieChartData.reduce((sum, item) => sum + (item.value || 0), 0);
    const pieDataWithPercentages = data.pieChartData.map(item => ({
      ...item,
      value: total > 0 ? Math.round((item.value / total) * 100 * 10) / 10 : 0
    }));
    setPieChartData(pieDataWithPercentages);
    """
    print(js_code)
    
    # Simular la transformación
    total = sum(item['value'] for item in backend_pie)
    print(f"   total = {' + '.join(str(item['value']) for item in backend_pie)} = {total}")
    
    transformed = []
    print(f"\n   Transformación:")
    for item in backend_pie:
        percentage = (item['value'] / total) * 100 if total > 0 else 0
        rounded = round(percentage * 10) / 10
        transformed.append({**item, "value": rounded})
        print(f"   - {item['name']:15} {item['value']:3} → ({item['value']}/{total})*100 = {rounded:.1f}%")
    
    print(f"\n   pieDataWithPercentages = {json.dumps(transformed, indent=2)}")
    
    # ========================================================================
    print("\n📍 PASO 6: RESULTADO FINAL EN PIE CHART")
    print("-" * 80)
    print(f"✅ setPieChartData(pieDataWithPercentages) ejecutado")
    print(f"   pieChartData ahora tiene DATOS DEL BACKEND (no mock)")
    print(f"\n   El pie chart renderiza:")
    for item in transformed:
        print(f"   - {item['name']:15}: {item['value']:.1f}%")
    
    # ========================================================================
    print("\n📍 PASO 7: COMPARACIÓN")
    print("-" * 80)
    print(f"❌ MOCK (inicial):      45%, 30%, 15%, 10%")
    print(f"✅ REAL (esperado):     {', '.join(f\"{item['value']:.0f}%\" for item in transformed)}")
    
else:
    print("❌ Backend NO devuelve pieChartData")

# ============================================================================
print("\n" + "="*80)
print("🔍 POSIBLES PROBLEMAS")
print("="*80)
print("""
1. ❌ SIN TOKEN:
   - Si no hay localStorage.getItem('access_token')
   - useEffect retorna en línea 47-48
   - pieChartData se queda con mockData
   - FIX: Asegúrate de tener JWT token en localStorage

2. ❌ BACKEND DEVUELVE ERROR:
   - Si response.ok es false (línea 58)
   - No ejecuta las líneas 73-92
   - pieChartData se queda con mockData
   - FIX: Verifica logs en F12 → Console → "Backend returned non-200"

3. ❌ BACKEND DEVUELVE VACÍO:
   - Si data.pieChartData es null o undefined (línea 81)
   - No ejecuta las líneas 82-92
   - pieChartData se queda con mockData
   - FIX: Verifica logs en F12 → Console → hasPie: false

4. ❌ JAVASCRIPT ERROR EN TRANSFORMACIÓN:
   - Si reduce() o map() falla en líneas 85-89
   - Se captura en catch() (línea 97)
   - pieChartData se queda con mockData
   - FIX: Abre F12 → Console → busca errores rojos

5. ✅ TODO CORRECTO:
   - useEffect ejecuta completamente
   - setPieChartData se llama con datos transformados
   - pieChartData tiene valores del backend (30%, 30%, 24%, 16%)
   - Pie chart renderiza DATOS REALES
""")

print("="*80 + "\n")
