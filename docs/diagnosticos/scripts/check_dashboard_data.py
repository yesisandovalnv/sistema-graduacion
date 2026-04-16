#!/usr/bin/env python3
"""
DIAGNÓSTICO PUNTUAL: Gráficos Vacíos en Dashboard
=================================================

Script para verificar SIN MODIFICAR NADA:
1. Qué JSON devuelve backend exactamente
2. Si arrays vienen vacíos
3. Qué campos de fecha usa el backend
4. Si existen datos en la BD
5. Causa raíz exacta del problema
"""

import os
import json
import sys
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '/app')

import django
django.setup()

# Imports después de setup
from django.utils import timezone
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth

from postulantes.models import Postulacion, Postulante
from documentos.models import DocumentoPostulacion
from reportes.services import get_dashboard_chart_data, dashboard_general

print("\n" + "="*80)
print("🔍 DIAGNÓSTICO PUNTUAL: GRÁFICOS VACÍOS EN DASHBOARD")
print("="*80)

# ============================================================================
# SECCIÓN 1: VERIFICAR DATOS EN BD
# ============================================================================
print("\n\n📊 SECCIÓN 1: VERIFICACIÓN DE DATOS EN BASEDATOS")
print("-" * 80)

total_postulantes = Postulante.objects.count()
total_postulaciones = Postulacion.objects.count()
total_documentos = DocumentoPostulacion.objects.count()

print(f"✅ Total Postulantes: {total_postulantes}")
print(f"✅ Total Postulaciones: {total_postulaciones}")
print(f"✅ Total Documentos: {total_documentos}")

# Verificar fechas
if total_postulaciones > 0:
    postulacion_mas_antigua = Postulacion.objects.order_by('fecha_postulacion').first()
    postulacion_mas_nueva = Postulacion.objects.order_by('-fecha_postulacion').first()
    
    print(f"\n📅 Rango de Postulaciones:")
    print(f"   - Más antigua: {postulacion_mas_antigua.fecha_postulacion}")
    print(f"   - Más nueva: {postulacion_mas_nueva.fecha_postulacion}")
    print(f"   - Diferencia: {(postulacion_mas_nueva.fecha_postulacion - postulacion_mas_antigua.fecha_postulacion).days} días")

if total_documentos > 0:
    doc_mas_antiguo = DocumentoPostulacion.objects.order_by('fecha_subida').first()
    doc_mas_nuevo = DocumentoPostulacion.objects.order_by('-fecha_subida').first()
    
    print(f"\n📅 Rango de Documentos:")
    print(f"   - Más antiguo: {doc_mas_antiguo.fecha_subida if doc_mas_antiguo.fecha_subida else 'NULL'}")
    print(f"   - Más nuevo: {doc_mas_nuevo.fecha_subida if doc_mas_nuevo.fecha_subida else 'NULL'}")
    
    # Contar NULLs en fecha_subida
    nulos_fecha_subida = DocumentoPostulacion.objects.filter(fecha_subida__isnull=True).count()
    print(f"   - ⚠️  NULL en fecha_subida: {nulos_fecha_subida}")

# ============================================================================
# SECCIÓN 2: VERIFICAR RANGO DE 6 MESES
# ============================================================================
print("\n\n🗓️  SECCIÓN 2: VERIFICACIÓN DE RANGO 6 MESES (ÚLTIMOS)")
print("-" * 80)

ahora = timezone.now()
hace_6_meses = ahora - relativedelta(months=6)

print(f"Fecha actual (timezone.now()): {ahora}")
print(f"Fecha hace 6 meses: {hace_6_meses}")

postulaciones_ultimas_6_meses = Postulacion.objects.filter(
    fecha_postulacion__gte=hace_6_meses,
    fecha_postulacion__lte=ahora
).count()

documentos_ultimas_6_meses = DocumentoPostulacion.objects.filter(
    fecha_subida__gte=hace_6_meses,
    fecha_subida__lte=ahora
).count()

print(f"\n✅ Postulaciones últimos 6 meses: {postulaciones_ultimas_6_meses}")
print(f"✅ Documentos últimos 6 meses: {documentos_ultimas_6_meses}")

if postulaciones_ultimas_6_meses == 0:
    print("\n⚠️  ALERTA: Sin postulaciones en últimos 6 meses!")
    # Buscar todas las postulaciones
    todas_postulaciones = Postulacion.objects.order_by('-fecha_postulacion')[:5]
    print("   Primeras 5 postulaciones más recientes:")
    for post in todas_postulaciones:
        print(f"      - {post.fecha_postulacion}")

# ============================================================================
# SECCIÓN 3: DETALLAR DATOS POR MES (ÚLTIMOS 6 MESES)
# ============================================================================
print("\n\n📈 SECCIÓN 3: DATOS AGREGADOS POR MES (ÚLTIMOS 6 MESES)")
print("-" * 80)

postulaciones_por_mes = list(
    Postulacion.objects
    .filter(fecha_postulacion__gte=hace_6_meses, fecha_postulacion__lte=ahora)
    .annotate(mes=TruncMonth('fecha_postulacion'))
    .values('mes')
    .annotate(
        postulantes=Count('id'),
        graduados=Count('id', filter=Q(estado_general='TITULADO')),
        pendientes=Count('id', filter=Q(estado_general='EN_PROCESO')),
        aprobados=Count('id', filter=Q(estado_general='APROBADO')),
        rechazados=Count('id', filter=Q(estado_general='RECHAZADO'))
    )
    .order_by('mes')
)

print(f"Registros de postulaciones por mes: {len(postulaciones_por_mes)}")
for item in postulaciones_por_mes:
    print(f"\n   {item['mes'].date()} (Mes):")
    print(f"      - postulantes: {item['postulantes']}")
    print(f"      - graduados (TITULADO): {item['graduados']}")
    print(f"      - pendientes (EN_PROCESO): {item['pendientes']}")
    print(f"      - aprobados (APROBADO): {item['aprobados']}")
    print(f"      - rechazados (RECHAZADO): {item['rechazados']}")

documentos_por_mes = list(
    DocumentoPostulacion.objects
    .filter(fecha_subida__gte=hace_6_meses, fecha_subida__lte=ahora)
    .annotate(mes=TruncMonth('fecha_subida'))
    .values('mes')
    .annotate(total=Count('id'))
    .order_by('mes')
)

print(f"\n\nRegistros de documentos por mes: {len(documentos_por_mes)}")
for item in documentos_por_mes:
    print(f"\n   {item['mes'].date() if item['mes'] else 'NULL'} (Mes):")
    print(f"      - total: {item['total']}")

# ============================================================================
# SECCIÓN 4: EJECUTAR FUNCIONES DE SERVICIO
# ============================================================================
print("\n\n🚀 SECCIÓN 4: RESPUESTA DE SERVICIOS backend")
print("-" * 80)

print("\n▶️  Ejecutando: get_dashboard_chart_data(meses=6)")
try:
    chart_data = get_dashboard_chart_data(meses=6)
    
    print("\n✅ Respuesta recibida exitosamente")
    print(f"\nJSON COMPLETO DE RESPUESTA BACKEND:")
    print(json.dumps(chart_data, indent=2, default=str))
    
    # Análisis puntual
    print("\n\n🔬 ANÁLISIS PUNTUAL:")
    print(f"   - barChartData es vacío? {len(chart_data['barChartData']) == 0}")
    print(f"   - lineChartData es vacío? {len(chart_data['lineChartData']) == 0}")
    print(f"   - pieChartData es vacío? {len(chart_data['pieChartData']) == 0}")
    
    if len(chart_data['barChartData']) > 0:
        print(f"   - Primer elemento barChartData: {json.dumps(chart_data['barChartData'][0], indent=4)}")
    if len(chart_data['lineChartData']) > 0:
        print(f"   - Primer elemento lineChartData: {json.dumps(chart_data['lineChartData'][0], indent=4)}")
    
    if chart_data.get('error'):
        print(f"\n   ⚠️  ERROR en respuesta: {chart_data['error']}")
        
except Exception as e:
    print(f"❌ Error ejecutando get_dashboard_chart_data: {e}")
    import traceback
    traceback.print_exc()

print("\n\n▶️  Ejecutando: dashboard_general()")
try:
    general_data = dashboard_general()
    
    print("\n✅ Respuesta recibida exitosamente")
    print(f"\nJSON COMPLETO DE RESPUESTA BACKEND:")
    print(json.dumps(general_data, indent=2, default=str))
    
except Exception as e:
    print(f"❌ Error ejecutando dashboard_general: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# SECCIÓN 5: DIAGNÓSTICO FINAL
# ============================================================================
print("\n\n" + "="*80)
print("📋 DIAGNÓSTICO FINAL")
print("="*80)

problemas_identificados = []

if total_postulaciones == 0:
    problemas_identificados.append("❌ NO HAY POSTULACIONES EN LA BD")
elif postulaciones_ultimas_6_meses == 0:
    problemas_identificados.append("❌ NO HAY POSTULACIONES EN LOS ÚLTIMOS 6 MESES (rango de consulta problemático)")
    
if total_documentos == 0:
    problemas_identificados.append("❌ NO HAY DOCUMENTOS EN LA BD")
elif documentos_ultimas_6_meses == 0:
    problemas_identificados.append("❌ NO HAY DOCUMENTOS EN LOS ÚLTIMOS 6 MESES")
    nulos = DocumentoPostulacion.objects.filter(fecha_subida__isnull=True).count()
    if nulos > 0:
        problemas_identificados.append(f"   ⚠️  {nulos} documentos tienen fecha_subida=NULL")

if not problemas_identificados:
    print("\n✅ CAUSA RAÍZ: Los datos SÍ EXISTEN en la BD")
    print("   → El problema es de TRANSFORMACIÓN/MAPEO en frontend o backend")
    print("   → Revisar propiedades esperadas en Charts.jsx vs propiedades reales en JSON")
else:
    print("\n🔴 PROBLEMAS ENCONTRADOS:")
    for problema in problemas_identificados:
        print(f"   {problema}")

print("\n" + "="*80)
print("✅ FIN DEL DIAGNÓSTICO")
print("="*80 + "\n")
