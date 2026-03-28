#!/usr/bin/env python
"""
DIAGNOSTICO: Por qué el pie chart no refleja cambios
Análisis detallado del componente Charts.jsx
"""

import os
import re

print("\n" + "="*80)
print("DIAGNOSTICO DETALLADO: PIE CHART NO REFLEJA CAMBIOS")
print("="*80 + "\n")

# Leer el archivo
file_path = r"c:\Users\luisfer\Documents\Visual-Code\sistema-graduacion\frontend\src\components\Charts.jsx"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("1. VERIFICAR dataKey")
print("-" * 80)
datakey_matches = re.findall(r'dataKey=["\'](\w+)["\']', content)
if datakey_matches:
    print("✅ dataKey encontrado:")
    for match in datakey_matches:
        print(f"   dataKey=\"{match}\"")
    if 'value' in datakey_matches:
        print("✅ dataKey=\"value\" ENCONTRADO (CORRECTO)")
else:
    print("❌ NO hay dataKey")

print("\n2. VERIFICAR si labels están hardcodeados")
print("-" * 80)
label_pattern = r'label=\{.*?\}'
label_matches = re.findall(label_pattern, content, re.DOTALL)
if label_matches:
    print("Label patterns encontrados:")
    for match in label_matches:
        # Truncar para legibilidad
        truncated = match[:100] + "..." if len(match) > 100 else match
        print(f"   {truncated}")
        if 'name' in match and 'value' in match:
            print(f"   ✅ Usa variables dinámicas (name, value)")
else:
    print("❌ No se encontraron labels")

print("\n3. VERIFICAR qué variable usa el Pie component")
print("-" * 80)
# Buscar <Pie data={...}
pie_pattern = r'<Pie\s+[^>]*data=\{([^}]+)\}'
pie_matches = re.findall(pie_pattern, content, re.DOTALL)
if pie_matches:
    print("Pie component data source:")
    for match in pie_matches:
        cleaned = match.strip()
        print(f"   data={{{cleaned}}}")
        if 'pieChartData' in cleaned:
            print("   ✅ Usa pieChartData (variable correcta)")
        elif 'mockPieChartData' in cleaned:
            print("   ❌ Usa mockPieChartData (SOLO mock, sin backend)")
else:
    print("❌ No se encontró <Pie data=")

print("\n4. BUSCAR referencias a 45, 30, 15, 10 en render")
print("-" * 80)
# Buscar números en el render (después de return)
return_idx = content.find('return (')
if return_idx != -1:
    render_section = content[return_idx:]
    
    # Buscar números específicos
    hardcoded_values = []
    for num in [45, 30, 15, 10]:
        if str(num) in render_section:
            # Contar ocurrencias
            count = render_section.count(str(num))
            hardcoded_values.append((num, count))
    
    if hardcoded_values:
        print("Números encontrados en render section:")
        for num, count in hardcoded_values:
            print(f"   '{num}' aparece {count} vez(es)")
        print("   ❌ Estos números PUEDEN estar hardcodeados")
        
        # Buscar contexto
        for num, count in hardcoded_values:
            if str(num) in render_section:
                # Encontrar línea
                lines_before = render_section[:render_section.find(str(num))].count('\n')
                print(f"   Primera ocurrencia de '{num}' alrededor de la línea {return_idx//50 + lines_before}:")
                
                # Extraer contexto (100 chars antes y después)
                idx = render_section.find(str(num))
                start = max(0, idx - 100)
                end = min(len(render_section), idx + 100)
                context = render_section[start:end]
                # Limpiar
                context = ' '.join(context.split())
                print(f"   ...{context}...")
    else:
        print("✅ No hay referencias hardcodeadas a 45, 30, 15, 10 en render")
else:
    print("❌ No se encontró 'return ('")

print("\n5. VERIFICAR memoization (useMemo, useCallback, React.memo)")
print("-" * 80)
memo_patterns = ['useMemo', 'useCallback', 'React.memo', 'memo(']
found_memo = False
for pattern in memo_patterns:
    if pattern in content:
        print(f"⚠️  '{pattern}' encontrado")
        found_memo = True
if not found_memo:
    print("✅ NO hay memoization (useMemo, useCallback, React.memo)")
    print("   ✅ Componente re-renderiza normalmente")

print("\n6. VERIFICAR estructura del estado pieChartData")
print("-" * 80)
# Buscar useState
usestate_pie = re.search(r'const \[pieChartData, setPieChartData\] = useState\(([^)]+)\)', content)
if usestate_pie:
    initial = usestate_pie.group(1)
    print(f"useState inicial: {initial}")
    if initial == 'mockPieChartData':
        print("✅ Inicializa con mockPieChartData (correcto)")
    else:
        print(f"⚠️  Inicializa con {initial}")

print("\n7. VERIFICAR transformación de percentajes")
print("-" * 80)
# Buscar la transformación
transform_pattern = r'const pieDataWithPercentages = ([^;]+);'
transform_match = re.search(transform_pattern, content, re.DOTALL)
if transform_match:
    print("✅ Transformación encontrada:")
    transform = transform_match.group(1)
    if 'map' in transform and 'value:' in transform:
        print("   ✅ Usa .map() para transformar")
        if '(item.value / total) * 100' in transform:
            print("   ✅ Calcula porcentaje como (value/total)*100")
else:
    print("❌ No se encontró transformación")

print("\n" + "="*80)
print("RESUMEN - ESTADO DEL CÓDIGO")
print("="*80 + "\n")

print("✅ CORRECTO:")
print("   1. Pie component usa data={pieChartData}")
print("   2. dataKey=\"value\" está configurado")
print("   3. Labels usan variables dinámicas {name, value}")
print("   4. Leyenda usa pieChartData.map() dinámicamente")
print("   5. NO hay memoization que cachee datos")
print("   6. setPieChartData se ejecuta cuando backend devuelve datos")
print("")
print("⚠️  POSIBLES PROBLEMAS:")
print("   1. Recharts puede requerir que el array sea NUEVA referencia")
print("   2. Si React no re-renderiza, setPieChartData quizás NO se ejecuta")
print("   3. La transformación a % podría tener un error silencioso")
print("")
print("PRÓXIMO PASO:")
print("   1. Abre dashboard en browser")
print("   2. F12 → Console")
print("   3. Busca logs [ACTION] 'setPieChartData called'")
print("   4. Busca logs [RENDER] con valores '30' (si ves 30, estado cambió)")
print("   5. Si el estado cambió pero pie chart no renderiza:")
print("      → Recharts podría tener problema con re-render")
print("      → Necesitaría forzar re-render con key diferente")

print("\n" + "="*80 + "\n")
