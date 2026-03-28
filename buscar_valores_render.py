#!/usr/bin/env python
"""
Buscar TODOS los lugares donde se muestran texto/valores en el componente
"""
import re

file_path = r"c:\Users\luisfer\Documents\Visual-Code\sistema-graduacion\frontend\src\components\Charts.jsx"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Obtener el return statement
return_idx = content.find('return (')
if return_idx == -1:
    return_idx = content.find('return(')

if return_idx != -1:
    render_part = content[return_idx:]
    
    print("\n" + "="*80)
    print("BUSQUEDA: Dónde se muestran los valores 45%, 30%, 15%, 10%")
    print("="*80 + "\n")
    
    # Buscar todos los <span>, <div>, <p> que contienen texto
    print("BUSCAR: Textos hardcodeados en el render\n")
    
    # Buscar patrones de texto literal con números
    patterns = [
        r'"[^"]*\d+[%]?[^"]*"',  # Strings con números
        r"'[^']*\d+[%]?[^']*'",   # Strings con números
        r'\{[^}]*Completado[^}]*\}',  # Cualquier Completado
        r'\{[^}]*Rechazado[^}]*\}',   # Cualquier Rechazado
        r'\{[^}]*En Proceso[^}]*\}',  # Cualquier En Proceso
        r'\{[^}]*Por Revisar[^}]*\}', # Cualquier Por Revisar
    ]
    
    found_hardcoded = False
    
    # Buscar spans, divs, h3, p con contenido
    text_elements = re.findall(r'<(span|div|h3|h4|p|label)[^>]*>([^<]*)</\1>', render_part)
    
    print("Elementos de texto en render:\n")
    for tag, text in text_elements:
        if text.strip():  # Si tiene contenido
            # Limpiarse
            clean_text = text.replace('\n', '').replace('  ', ' ').strip()
            if len(clean_text) > 80:
                clean_text = clean_text[:80] + "..."
            print(f"  <{tag}> {clean_text}")
            
            # Buscar valores 45, 30, 15, 10
            if any(val in text for val in ['45', '30', '15', '10', '87', '24']):
                print(f"     ^ CONTIENE NÚMERO")
            
            # Buscar nombre de estado
            if any(name in text for name in ['Completado', 'Rechazado', 'En Proceso', 'Por Revisar']):
                print(f"     ^ CONTIENE NOMBRE DE ESTADO")
    
    print("\n" + "="*80)
    print("ANALISIS ESTRUCTURA PIE CHART")
    print("="*80 + "\n")
    
    # Buscar la sección del pie chart
    pie_idx = render_part.find('Distribución por Estado')
    if pie_idx != -1:
        pie_section = render_part[pie_idx:pie_idx+2000]
        
        # Buscar <Pie
        pie_tag_idx = pie_section.find('<Pie')
        if pie_tag_idx != -1:
            print("✅ <Pie component encontrado")
            pie_tag = pie_section[pie_tag_idx:pie_tag_idx+500]
            if 'data={pieChartData}' in pie_tag:
                print("   ✅ Usa data={pieChartData} dinámicamente")
            if 'dataKey="value"' in pie_tag:
                print("   ✅ Usa dataKey=\"value\"")
        
        # Buscar leyenda personalizada
        legend_idx = pie_section.find('Leyenda personalizada')
        if legend_idx != -1:
            print("\n✅ Leyenda personalizada encontrada")
            legend_section = pie_section[legend_idx:legend_idx+1000]
            if 'pieChartData.map' in legend_section:
                print("   ✅ Usa pieChartData.map() dinámicamente")
                print("   ✅ Contenido: {item.name}: {item.value}%")
            else:
                print("   ❌ NO usa pieChartData.map()")
                print("   CONTENIDO:")
                print(legend_section[:500])

print("\n" + "="*80 + "\n")
