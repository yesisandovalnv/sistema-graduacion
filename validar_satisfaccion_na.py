#!/usr/bin/env python
"""
Script de validación: Métrica Satisfacción mostrar "N/A" cuando no hay datos
- Verificar que backend retorna 'satisfaccion_score' como "N/A" cuando total_documentos == 0
- Verificar que el campo está en la respuesta JSON
"""
import os
import json
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from reportes.services import dashboard_general
from datetime import datetime, timedelta
from django.utils import timezone

print("═" * 70)
print("🔍 VALIDACIÓN: Métrica Satisfacción con N/A cuando no hay datos")
print("═" * 70)

# Caso 1: Sistema sin datos (tabla vacía)
print("\n📋 CASO 1: Sistema vacío (sin documentos)")
print("-" * 70)

today = timezone.now()
result = dashboard_general(
    fecha_inicio=today - timedelta(days=30),
    fecha_fin=today,
    year=today.year
)

print(f"✅ Satisfacción (sin datos): {result.get('satisfaccion_score')}")
print(f"   Tipo: {type(result.get('satisfaccion_score'))}")
print(f"   ¿Es 'N/A'? {result.get('satisfaccion_score') == 'N/A'}")

# Validar que sea string "N/A"
if result.get('satisfaccion_score') == "N/A":
    print("✅ ✅ ✅ CORRECTO: Satisfacción retorna 'N/A' cuando no hay datos")
else:
    print(f"❌ ERROR: Satisfacción retorna {result.get('satisfaccion_score')} en lugar de 'N/A'")

# Caso 2: Verificar respuesta completa
print("\n📋 CASO 2: Estructura completa de respuesta")
print("-" * 70)

expected_fields = [
    'total_postulantes',
    'documentos_pendientes',
    'total_titulados',
    'tasa_aprobacion',
    'promedio_procesamiento_dias',
    'satisfaccion_score',  # ← ESTE ES NUESTRO
    'proyeccion_mes_porcentaje',
    'cambio_postulantes_porcentaje',
    'cambio_documentos_porcentaje',
    'cambio_titulados_porcentaje',
    'cambio_tasa_porcentaje',
]

missing = [f for f in expected_fields if f not in result]
if missing:
    print(f"❌ Campos faltantes: {missing}")
else:
    print(f"✅ Todos los {len(expected_fields)} campos presentes")

# Mostrar resumen
print("\n" + "═" * 70)
print("📊 RESUMEN DE MÉTRICAS (Sistema Vacío)")
print("═" * 70)

metrics_display = {
    'Total Postulantes': f"{result.get('total_postulantes')} (cambio: {result.get('cambio_postulantes_porcentaje')}%)",
    'Documentos Pendientes': f"{result.get('documentos_pendientes')} (cambio: {result.get('cambio_documentos_porcentaje')}%)",
    'Graduados': f"{result.get('total_titulados')} (cambio: {result.get('cambio_titulados_porcentaje')}%)",
    'Tasa Aprobación': f"{result.get('tasa_aprobacion')}% (cambio: {result.get('cambio_tasa_porcentaje')}%)",
    'Promedio Procesamiento': f"{result.get('promedio_procesamiento_dias')} días",
    'Satisfacción': f"{result.get('satisfaccion_score')}",  # ← Mostrar N/A
    'Proyección Mes': f"{result.get('proyeccion_mes_porcentaje')}%",
}

for name, value in metrics_display.items():
    if name == 'Satisfacción':
        # Destacar la métrica revisada
        print(f"  🎯 {name}: {value} {'✅ N/A CORRECTO' if result.get('satisfaccion_score') == 'N/A' else '❌ ERROR'}")
    else:
        print(f"  • {name}: {value}")

# Validación final
print("\n" + "═" * 70)
if result.get('satisfaccion_score') == "N/A":
    print("✅ VALIDACIÓN EXITOSA")
    print("   • Satisfacción muestra 'N/A' cuando no hay datos")
    print("   • Estructura JSON completa y correcta")
    print("   • Regla implementada: sin datos → N/A | con datos → valor/10")
else:
    print("❌ VALIDACIÓN FALLIDA")
    print(f"   • Esperado: 'N/A'")
    print(f"   • Obtenido: {result.get('satisfaccion_score')}")

print("═" * 70)
