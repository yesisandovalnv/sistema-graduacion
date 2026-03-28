#!/usr/bin/env python
"""Debug profundo del filtro de fechas"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from dateutil.relativedelta import relativedelta
from postulantes.models import Postulacion
from documentos.models import DocumentoPostulacion

# Calcular rango (mismo que en get_dashboard_chart_data)
meses = 6
fecha_fin = timezone.now()
fecha_inicio = fecha_fin - relativedelta(months=meses)

print(f"Rango de fecha: {fecha_inicio} a {fecha_fin}")
print(f"Tipo: {type(fecha_fin)}")

# Ver todos los datos
todos = Postulacion.objects.all()
print(f"\nTotal postulaciones en BD: {todos.count()}")

# Ver primeras 3
for p in todos[:3]:
    print(f"  - {p.id}: fecha={p.fecha_postulacion}, estado={p.estado_general}")

# Aplicar filtro
filtrados = Postulacion.objects.filter(fecha_postulacion__gte=fecha_inicio, fecha_postulacion__lte=fecha_fin)
print(f"\nPostulaciones dentro del rango: {filtrados.count()}")

# Ver por mes
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth

por_mes = list(
    filtrados
    .annotate(mes=TruncMonth('fecha_postulacion'))
    .values('mes')
    .annotate(
        total=Count('id'),
        graduados=Count('id', filter=Q(estado_general='TITULADO'))
    )
    .order_by('mes')
)

print(f"\nPor mes: {len(por_mes)}")
for item in por_mes:
    print(f"  - {item}")
