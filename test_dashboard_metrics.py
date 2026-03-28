#!/usr/bin/env python
"""
Test Script: Verificar que el backend retorna las nuevas métricas
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from reportes.services import dashboard_general

print("\n" + "="*70)
print("🧪 TEST: Verificar datos de dashboard_general()")
print("="*70 + "\n")

try:
    result = dashboard_general()
    
    print("📊 RESULTADO:")
    print("-" * 70)
    
    # Métricas principales
    print("\n✅ MÉTRICAS BÁSICAS:")
    print(f"   • Total Postulantes: {result.get('total_postulantes', 0)}")
    print(f"   • Total Postulaciones: {result.get('total_postulaciones', 0)}")
    print(f"   • Total Titulados: {result.get('total_titulados', 0)}")
    print(f"   • Documentos Pendientes: {result.get('documentos_pendientes', 0)}")
    print(f"   • Documentos Rechazados: {result.get('documentos_rechazados', 0)}")
    
    # NUEVAS MÉTRICAS (FASE 3)
    print("\n✅ NUEVAS MÉTRICAS (FASE 3 - SIN HARDCODE):")
    print(f"   • Tasa de Aprobación: {result.get('tasa_aprobacion', 0)}%")
    print(f"   • Promedio Procesamiento: {result.get('promedio_procesamiento_dias', 0)} días")
    print(f"   • Satisfacción: {result.get('satisfaccion_score', 0)}/10")
    print(f"   • Proyección Mes: {result.get('proyeccion_mes_porcentaje', 0)}%")
    
    print("\n" + "="*70)
    print("✅ RESULTADO ESPERADO: TODAS LAS MÉTRICAS RETORNADAS (pueden ser 0 si no hay datos)")
    print("="*70)
    
    # Validaciones
    print("\n🔍 VALIDACIONES:")
    required_keys = [
        'total_postulantes',
        'total_postulaciones', 
        'total_titulados',
        'tasa_aprobacion',
        'promedio_procesamiento_dias',
        'satisfaccion_score',
        'proyeccion_mes_porcentaje'
    ]
    
    missing = [k for k in required_keys if k not in result]
    
    if missing:
        print(f"❌ FALTAN CLAVES: {missing}")
    else:
        print("✅ TODAS LAS CLAVES PRESENTES")
    
    print("\n" + "="*70)
    print("JSON COMPLETO:")
    print("="*70)
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
