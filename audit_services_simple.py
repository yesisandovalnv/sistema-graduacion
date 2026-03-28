#!/usr/bin/env python
"""
Script simple: Leer el archivo services.py y mostrar exactamente qué línea  
asigna a satisfaccion_score
"""

with open('reportes/services.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("🔍 BÚSQUEDA EN reportes/services.py")
print("═" * 70)

# Buscar líneas que asignen satisfaccion_score
for i, line in enumerate(lines, 1):
    if 'satisfaccion_score' in line and '=' in line:
        # Mostrar contexto: 2 líneas antes y después
        start = max(0, i - 3)
        end = min(len(lines), i + 2)
        
        print(f"\n📍 Línea {i}:")
        print("-" * 70)
        for j in range(start, end):
            marker = ">>> " if j == i - 1 else "    "
            print(f"{marker}{j+1:4d}: {lines[j]}", end='')
        print()
        
print("═" * 70)
print("\n✅ ANÁLISIS:")
print("  • Si vez 'satisfaccion_score = \"N/A\"' → Backend está correcto")
print("  • Si vez 'satisfaccion_score = 0.0' → Backend tiene el valor viejo")
print("  • Múltiples líneas = múltiples asignaciones en diferentes ramas")
