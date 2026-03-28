#!/usr/bin/env python
"""Debug del mapeo de diccionario"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from dateutil.relativedelta import relativedelta
from postulantes.models import Postulacion
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth

meses = 6
fecha_fin = timezone.now()
fecha_inicio = fecha_fin - relativedelta(months=meses)

# 1. Obtener datos
postulaciones_por_mes = list(
    Postulacion.objects
    .filter(fecha_postulacion__gte=fecha_inicio, fecha_postulacion__lte=fecha_fin)
    .annotate(mes=TruncMonth('fecha_postulacion'))
    .values('mes')
    .annotate(
        postulantes=Count('id'),
        graduados=Count('id', filter=Q(estado_general='TITULADO')),
        pendientes=Count('id', filter=Q(estado_general='EN_PROCESO')),
        aprobados=Count('id', filter=Q(estado_general='APROBADO')),
    )
    .order_by('mes')
)

print(f"Datos consultados ({len(postulaciones_por_mes)} meses):")
for item in postulaciones_por_mes:
    print(f"  mes={item['mes']}, type={type(item['mes'])}, postulantes={item['postulantes']}")

# 2. Mapper a diccionario
postulaciones_dict = {item['mes']: item for item in postulaciones_por_mes}
print(f"\nDiccionario keys:")
for key in postulaciones_dict.keys():
    print(f"  {key}, type={type(key)}")

# 3. Generar lineChartData (como en el código)
print(f"\nGenerando lineChartData para {meses} meses:")
lineChartData = []
for i in range(meses):
    fecha = fecha_inicio + relativedelta(months=i)
    mes_label = fecha.strftime('%b')
    
    # AQUÍ ESTÁ EL PROBLEMA
    lookup_key = fecha.replace(day=1)
    print(f"  i={i}: fecha={fecha}, lookup_key={lookup_key}, type={type(lookup_key)}")
    
    postulacion = postulaciones_dict.get(lookup_key, {})
    print(f"         encontrado={len(postulacion) > 0}, postulantes={postulacion.get('postulantes', '?')}")
    
    lineChartData.append({
        'mes': mes_label,
        'graduados': int(postulacion.get('graduados', 0) or 0),
        'pendientes': int(postulacion.get('pendientes', 0) or 0),
        'aprobados': int(postulacion.get('aprobados', 0) or 0),
    })

print("\nlineChartData resultado:")
print(lineChartData)
