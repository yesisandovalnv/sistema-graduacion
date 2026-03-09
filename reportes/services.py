from django.db.models import Avg, Case, Count, DurationField, ExpressionWrapper, F, FloatField, Max, Q, Value, When
from django.db.models.functions import Coalesce, Now, TruncMonth
from io import BytesIO
import os
from django.conf import settings
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill

from documentos.models import DocumentoPostulacion
from modalidades.models import Modalidad
from postulantes.models import Postulacion, Postulante


def porcentaje_avance_postulacion(postulacion_id: int) -> float:
    queryset = Postulacion.objects.filter(pk=postulacion_id).annotate(
        total_etapas=Count('modalidad__etapas', filter=Q(modalidad__etapas__activo=True), distinct=True)
    )
    queryset = queryset.annotate(
        etapas_completadas=Case(
            When(estado_general='TITULADO', then=F('total_etapas')),
            When(etapa_actual__orden__isnull=False, then=F('etapa_actual__orden') - Value(1)),
            default=Value(0),
        )
    ).annotate(
        porcentaje=Case(
            When(total_etapas=0, then=Value(0.0)),
            default=ExpressionWrapper(
                100.0 * F('etapas_completadas') / F('total_etapas'),
                output_field=FloatField(),
            ),
            output_field=FloatField(),
        )
    )

    result = queryset.values('porcentaje').first()
    if not result:
        return 0.0
    return round(result['porcentaje'] or 0.0, 2)


def documentos_rechazados_por_postulacion(postulacion_id: int) -> dict:
    rejected_docs = list(
        DocumentoPostulacion.objects.filter(postulacion_id=postulacion_id, estado='rechazado')
        .select_related('tipo_documento')
        .values(
            'id',
            'tipo_documento_id',
            'tipo_documento__nombre',
            'comentario_revision',
            'fecha_revision',
        )
        .order_by('-fecha_revision', '-id')
    )
    return {
        'postulacion_id': postulacion_id,
        'total_rechazados': len(rejected_docs),
        'documentos': rejected_docs,
    }


def dashboard_general(fecha_inicio=None, fecha_fin=None, year=None) -> dict:
    postulaciones_base = Postulacion.objects.all()
    postulantes_base = Postulante.objects.all()
    documentos_base = DocumentoPostulacion.objects.all()

    if year:
        try:
            year_int = int(year)
            postulaciones_base = postulaciones_base.filter(fecha_postulacion__year=year_int)
            postulantes_base = postulantes_base.filter(creado_en__year=year_int)
            documentos_base = documentos_base.filter(fecha_subida__year=year_int)
        except (ValueError, TypeError):
            pass

    if fecha_inicio:
        postulaciones_base = postulaciones_base.filter(fecha_postulacion__date__gte=fecha_inicio)
        postulantes_base = postulantes_base.filter(creado_en__date__gte=fecha_inicio)
        documentos_base = documentos_base.filter(fecha_subida__date__gte=fecha_inicio)

    if fecha_fin:
        postulaciones_base = postulaciones_base.filter(fecha_postulacion__date__lte=fecha_fin)
        postulantes_base = postulantes_base.filter(creado_en__date__lte=fecha_fin)
        documentos_base = documentos_base.filter(fecha_subida__date__lte=fecha_fin)

    total_postulaciones = postulaciones_base.aggregate(total=Count('id'))['total']
    total_postulantes = postulantes_base.count()
    total_modalidades = Modalidad.objects.filter(activo=True).count()
    total_documentos = documentos_base.count()

    postulaciones_por_etapa = list(
        postulaciones_base.values('etapa_actual_id', 'etapa_actual__nombre')
        .annotate(total=Count('id'))
        .order_by('etapa_actual__nombre', 'etapa_actual_id')
    )
    
    # Distribución por Estado General para el gráfico
    postulaciones_por_estado = list(
        postulaciones_base.values('estado_general')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    # Postulaciones por mes
    postulaciones_por_mes = list(
        postulaciones_base.annotate(month=TruncMonth('fecha_postulacion'))
        .values('month')
        .annotate(total=Count('id'))
        .order_by('month')
    )

    # Documentos aprobados/rechazados por mes (basado en fecha de revisión)
    documentos_revision_base = DocumentoPostulacion.objects.filter(
        estado__in=['aprobado', 'rechazado'], 
        fecha_revision__isnull=False
    )
    if year:
        documentos_revision_base = documentos_revision_base.filter(
            fecha_revision__year=int(year)
        )
    if fecha_inicio:
        documentos_revision_base = documentos_revision_base.filter(fecha_revision__date__gte=fecha_inicio)
    if fecha_fin:
        documentos_revision_base = documentos_revision_base.filter(fecha_revision__date__lte=fecha_fin)

    documentos_por_mes = list(
        documentos_revision_base.annotate(month=TruncMonth('fecha_revision'))
        .values('month')
        .annotate(aprobados=Count('id', filter=Q(estado='aprobado')), rechazados=Count('id', filter=Q(estado='rechazado')))
        .order_by('month')
    )

    # Tiempo promedio de titulación por mes (para titulados)
    tiempos_por_mes = list(
        postulaciones_base.filter(estado_general='TITULADO')
        .annotate(
            fecha_fin=Coalesce(Max('documentos__fecha_revision'), Now())
        )
        .annotate(
            month=TruncMonth('fecha_fin'),
            duracion=ExpressionWrapper(
                F('fecha_fin') - F('fecha_postulacion'),
                output_field=DurationField(),
            )
        )
        .values('month')
        .annotate(tiempo_promedio=Avg('duracion'))
        .order_by('month')
    )

    documentos_resumen = documentos_base.aggregate(
        documentos_pendientes=Count('id', filter=Q(estado='pendiente')),
        documentos_rechazados=Count('id', filter=Q(estado='rechazado')),
    )

    tiempos = (
        postulaciones_base.filter(estado_general='TITULADO')
        .annotate(
            fecha_fin=Coalesce(Max('documentos__fecha_revision'), Now()),
            duracion=ExpressionWrapper(
                F('fecha_fin') - F('fecha_postulacion'),
                output_field=DurationField(),
            ),
        )
        .aggregate(
            tiempo_promedio=Avg('duracion'),
            total_titulados=Count('id'),
        )
    )

    tiempo_promedio = tiempos['tiempo_promedio']
    tiempo_promedio_dias = round(tiempo_promedio.total_seconds() / 86400, 2) if tiempo_promedio else 0.0

    return {
        'total_postulaciones': total_postulaciones,
        'total_postulantes': total_postulantes,
        'total_modalidades': total_modalidades,
        'total_documentos': total_documentos,
        'postulaciones_por_estado_general': [
            {
                'estado': item['estado_general'],
                'total': item['total']
            }
            for item in postulaciones_por_estado
        ],
        'postulaciones_por_mes': [
            {
                'mes': item['month'].strftime('%Y-%m'),
                'total': item['total']
            }
            for item in postulaciones_por_mes
        ],
        'documentos_por_mes': [
            {
                'mes': item['month'].strftime('%Y-%m'),
                'aprobados': item['aprobados'],
                'rechazados': item['rechazados']
            }
            for item in documentos_por_mes
        ],
        'tiempo_promedio_por_mes': [
            {
                'mes': item['month'].strftime('%Y-%m'),
                'dias': round(item['tiempo_promedio'].total_seconds() / 86400, 2) if item['tiempo_promedio'] else 0.0
            }
            for item in tiempos_por_mes
        ],
        'postulaciones_por_etapa': [
            {
                'etapa_id': item['etapa_actual_id'],
                'etapa_nombre': item['etapa_actual__nombre'] or 'Sin etapa',
                'total': item['total'],
            }
            for item in postulaciones_por_etapa
        ],
        'documentos_pendientes': documentos_resumen['documentos_pendientes'],
        'documentos_rechazados': documentos_resumen['documentos_rechazados'],
        'total_titulados': tiempos['total_titulados'],
        'tiempo_promedio_proceso_dias': tiempo_promedio_dias,
    }


def generar_pdf_dashboard(data: dict, fecha_inicio: str | None, fecha_fin: str | None, year: str | None) -> HttpResponse:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, rightMargin=inch/2, leftMargin=inch/2, topMargin=inch/2, bottomMargin=inch/2)
    
    styles = getSampleStyleSheet()
    styles['h1'].textColor = colors.HexColor('#1A6FAB')
    styles['h2'].textColor = colors.HexColor('#1A6FAB')
    story = []

    # --- Logo y Título ---
    # NOTA: ReportLab tiene soporte limitado para SVG. Se recomienda usar un logo en formato PNG o JPG.
    # Coloca tu logo en 'static/logo.png' en la raíz del proyecto.
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'logo.png')
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=1.2*inch, height=0.6*inch)
        logo.hAlign = 'LEFT'
        story.append(logo)
        story.append(Spacer(1, 0.1*inch))

    story.append(Paragraph("Reporte de Dashboard Académico", styles['h1']))
    story.append(Spacer(1, 0.2*inch))

    # --- Rango de Fechas ---
    if year:
        story.append(Paragraph(f"Año Fiscal: {year}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
    elif fecha_inicio or fecha_fin:
        rango = f"Periodo: {fecha_inicio or 'N/A'} al {fecha_fin or 'N/A'}"
        story.append(Paragraph(rango, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))

    # --- Colores Corporativos ---
    primary_color = colors.HexColor('#1A6FAB')
    background_light = colors.HexColor('#EFF8FF')
    text_light = colors.white

    # --- Resumen General ---
    story.append(Paragraph("Resumen General", styles['h2']))
    cards_data = [
        ['Modalidades Activas', data.get('total_modalidades', 0)],
        ['Postulantes Registrados', data.get('total_postulantes', 0)],
        ['Postulaciones Totales', data.get('total_postulaciones', 0)],
        ['Documentos Cargados', data.get('total_documentos', 0)],
        ['Total Titulados', data.get('total_titulados', 0)],
        ['Promedio Proceso (días)', f"{data.get('tiempo_promedio_proceso_dias', 0.0):.2f}"],
    ]
    cards_table = Table(cards_data, colWidths=[3*inch, 1.5*inch])
    cards_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), background_light),
        ('GRID', (0, 0), (-1, -1), 1, primary_color),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (-1, -1), primary_color),
    ]))
    story.append(cards_table)
    story.append(Spacer(1, 0.3*inch))

    # --- Distribución por Estado ---
    story.append(Paragraph("Distribución por Estado General", styles['h2']))
    estado_data = [['Estado', 'Total']]
    for item in data.get('postulaciones_por_estado_general', []):
        estado_data.append([item['estado'].replace('_', ' '), item['total']])
    
    estado_table = Table(estado_data, colWidths=[3*inch, 1.5*inch])
    estado_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), text_light),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, primary_color),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ]))
    story.append(estado_table)

    doc.build(story)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte-dashboard.pdf"'
    return response


def estadisticas_tutores(year=None, carrera_id=None) -> list[dict]:
    """
    Calcula estadísticas de rendimiento de tutores:
    - Total de alumnos titulados.
    - Tiempo promedio de titulación (en días).
    """
    queryset = Postulacion.objects.filter(
        estado_general='TITULADO',
        tutor_ref__isnull=False
    )

    if carrera_id:
        try:
            queryset = queryset.filter(postulante__carrera_ref_id=int(carrera_id))
        except (ValueError, TypeError):
            pass

    if year:
        try:
            year_int = int(year)
            # Filtrar por año de titulación (estimado por la última revisión de documento)
            queryset = queryset.annotate(
                fecha_fin_filter=Coalesce(Max('documentos__fecha_revision'), Now())
            ).filter(fecha_fin_filter__year=year_int)
        except (ValueError, TypeError):
            pass

    stats = (
        queryset.annotate(
            fecha_fin=Coalesce(Max('documentos__fecha_revision'), Now()),
            duracion=ExpressionWrapper(
                F('fecha_fin') - F('fecha_postulacion'),
                output_field=DurationField(),
            )
        )
        .values('tutor_ref__id', 'tutor_ref__nombre', 'tutor_ref__apellido', 'tutor_ref__titulo_academico')
        .annotate(
            total_titulados=Count('id', distinct=True),
            tiempo_promedio=Avg('duracion')
        )
        .order_by('-total_titulados')
    )

    return [
        {
            'tutor_id': item['tutor_ref__id'],
            'nombre': f"{item['tutor_ref__titulo_academico'] or ''} {item['tutor_ref__nombre']} {item['tutor_ref__apellido']}".strip(),
            'total_titulados': item['total_titulados'],
            'tiempo_promedio_dias': round(item['tiempo_promedio'].total_seconds() / 86400, 2) if item['tiempo_promedio'] else 0.0
        }
        for item in stats
    ]


def detalle_alumnos_titulados_por_tutor(tutor_id: int) -> list[dict]:
    """
    Obtiene el detalle de los alumnos titulados bajo la tutoría de un docente específico.
    """
    queryset = Postulacion.objects.filter(
        estado_general='TITULADO',
        tutor_ref_id=tutor_id
    ).select_related('postulante', 'modalidad').annotate(
        fecha_fin=Coalesce(Max('documentos__fecha_revision'), Now()),
        duracion=ExpressionWrapper(
            F('fecha_fin') - F('fecha_postulacion'),
            output_field=DurationField(),
        )
    ).order_by('-fecha_fin')

    return [
        {
            'postulacion_id': p.id,
            'alumno_nombre': f"{p.postulante.nombre} {p.postulante.apellido}",
            'alumno_codigo': p.postulante.codigo_estudiante,
            'modalidad': p.modalidad.nombre,
            'titulo_trabajo': p.titulo_trabajo,
            'gestion': p.gestion,
            'fecha_inicio': p.fecha_postulacion.strftime('%Y-%m-%d'),
            'fecha_fin': p.fecha_fin.strftime('%Y-%m-%d') if hasattr(p, 'fecha_fin') else None,
            'duracion_dias': p.duracion.days if hasattr(p, 'duracion') and p.duracion else 0,
        }
        for p in queryset
    ]


def reporte_eficiencia_carreras(year=None) -> list[dict]:
    """
    Genera un reporte de eficiencia por carrera universitaria:
    - Total de procesos iniciados.
    - Tasa de titulación (Titulados / Iniciados).
    - Tiempo promedio de titulación (en días).
    """
    queryset = Postulacion.objects.select_related('postulante__carrera_ref')

    if year:
        try:
            year_int = int(year)
            queryset = queryset.filter(fecha_postulacion__year=year_int)
        except (ValueError, TypeError):
            pass

    # Agrupar por carrera para conteos
    stats = queryset.values(
        'postulante__carrera_ref__id',
        'postulante__carrera_ref__nombre'
    ).annotate(
        total_iniciados=Count('id'),
        total_titulados=Count('id', filter=Q(estado_general='TITULADO')),
    ).order_by('-total_titulados')

    # Calcular tiempos promedio solo para los titulados
    tiempos_queryset = queryset.filter(estado_general='TITULADO').annotate(
        fecha_fin=Coalesce(Max('documentos__fecha_revision'), Now()),
        duracion=ExpressionWrapper(
            F('fecha_fin') - F('fecha_postulacion'),
            output_field=DurationField(),
        )
    ).values('postulante__carrera_ref__id').annotate(
        tiempo_promedio=Avg('duracion')
    )
    
    tiempos_map = {item['postulante__carrera_ref__id']: item['tiempo_promedio'] for item in tiempos_queryset}

    return [
        {
            'carrera': item['postulante__carrera_ref__nombre'] or 'Sin Carrera Asignada',
            'total_iniciados': item['total_iniciados'],
            'total_titulados': item['total_titulados'],
            'tasa_titulacion': round((item['total_titulados'] / item['total_iniciados'] * 100), 2) if item['total_iniciados'] > 0 else 0.0,
            'tiempo_promedio_dias': round(tiempos_map.get(item['postulante__carrera_ref__id']).total_seconds() / 86400, 2) if tiempos_map.get(item['postulante__carrera_ref__id']) else 0.0
        }
        for item in stats
    ]


def generar_excel_tutores(data: list[dict]) -> HttpResponse:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Rendimiento Tutores"

    # Encabezados
    headers = ["ID", "Nombre", "Total Titulados", "Tiempo Promedio (Días)"]
    ws.append(headers)

    # Estilo de encabezados
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1A6FAB", end_color="1A6FAB", fill_type="solid")
    
    for cell in ws[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")

    # Datos
    for item in data:
        ws.append([
            item['tutor_id'],
            item['nombre'],
            item['total_titulados'],
            item['tiempo_promedio_dias']
        ])

    # Ajustar ancho de columnas
    for column_cells in ws.columns:
        length = max(len(str(cell.value) or "") for cell in column_cells)
        ws.column_dimensions[column_cells[0].column_letter].width = length + 2

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="estadisticas_tutores.xlsx"'
    return response
