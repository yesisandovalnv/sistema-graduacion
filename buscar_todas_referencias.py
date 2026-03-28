#!/usr/bin/env python
"""
Buscar TODAS las líneas que contengan "45" o "30" o"15" o "10" en el archivo
"""

file_path = r"c:\Users\luisfer\Documents\Visual-Code\sistema-graduacion\frontend\src\components\Charts.jsx"
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("\n" + "="*80)
print("BUSQUEDA: TODAS las líneas con 45, 30, 15, 10")
print("="*80 + "\n")

for i, line in enumerate(lines, 1):
    # Buscar líneas con estos valores
    if any(val in line for val in ['45', '30', '15', '10']):
        # Evitar líneas de CSS o comentarios que coincidan
        if not line.strip().startswith('//'):
            print(f"Línea {i}: {line.rstrip()}")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80 + "\n")

print("""
Si arriba solo ves:
- Definición de mockData (línea ~28-31)
- Estilos CSS con números (height, padding, etc)
- Datos de barras y líneas (45, 52, etc en otro contexto)

SIGNIFICA:
✅ NO hay valores 45%, 30%, 15%, 10% hardcodeados
✅ La leyenda es completamente dinámica (usa pieChartData)
✅ El problema es que pieChartData NO se está actualizando

SOLUCION:
Verificar en browser F12 Console:
- [ACTION] Calling setPieChartData... → SI APARECE = estado cambió
- [RENDER] pieChartData = 30 ... → SI APARECE= re-render sucedió
- Si ambos aparecen pero pie chart no se actualiza → Problema de Recharts
- Si NO aparecen → useEffect no ejecutaró setPieChartData
""")

print("="*80 + "\n")
