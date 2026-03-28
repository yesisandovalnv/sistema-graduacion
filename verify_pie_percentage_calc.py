#!/usr/bin/env python
"""
Simular la transformación de counts a porcentajes
(como hace el frontend en Charts.jsx)
"""

# Datos que devuelve el backend (counts absolutos)
backend_pie_data = [
    {"name": "Rechazado", "value": 15, "color": "#ef4444"},
    {"name": "Completado", "value": 15, "color": "#10b981"},
    {"name": "En Proceso", "value": 12, "color": "#f59e0b"},
    {"name": "Por Revisar", "value": 8, "color": "#3b82f6"},
]

print("\n" + "="*70)
print("📊 TRANSFORMACIÓN DE COUNTS A PORCENTAJES (SIMULACIÓN FRONTEND)")
print("="*70 + "\n")

print("✅ Datos del backend (counts absolutos):")
for item in backend_pie_data:
    print(f"   - {item['name']:15} value={item['value']:3}")

# Simular la transformación que hace el frontend
total = sum(item['value'] for item in backend_pie_data)
print(f"\n   Total count: {total}")

transformed_data = []
print("\n✅ Transformación (counts → porcentajes):")
for item in backend_pie_data:
    percentage = (item['value'] / total) * 100 if total > 0 else 0
    # Redondear a 1 decimal: Math.round((percentage) * 10) / 10
    rounded_percentage = round(percentage * 10) / 10
    
    transformed = {
        **item,
        "value": rounded_percentage
    }
    transformed_data.append(transformed)
    
    print(f"   - {item['name']:15} {item['value']:3} → {rounded_percentage:5.1f}% (label: '{item['name']}: {rounded_percentage}%')")

print(f"\n   Total porcentajes: {sum(t['value'] for t in transformed_data):.1f}%")

print("\n" + "="*70)
print("💡 VERIFICACIÓN EN GRÁFICO")
print("="*70)
print("""
✅ El pie chart mostrará:
   - Rechazado:      15 → 30.0% (label: "Rechazado: 30%")
   - Completado:     15 → 30.0% (label: "Completado: 30%")
   - En Proceso:     12 → 24.0% (label: "En Proceso: 24%")
   - Por Revisar:     8 → 16.0% (label: "Por Revisar: 16%")

✅ Los valores NO van a ser 45%, 30%, 15%, 10% del mock
✅ Los valores serán REALES del backend: 30%, 30%, 24%, 16%

✨ DIFERENCIA VISUAL CLARA:
   Mock: Dominado por "Completado 45%" (mucho mayor)
   Real: "Completado 30%" y "Rechazado 30%" (iguales)
""")
print("="*70 + "\n")
