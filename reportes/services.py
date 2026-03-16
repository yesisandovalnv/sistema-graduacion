from django.db.models import Avg, Case, Count, DurationField, ExpressionWrapper, F, FloatField, Max, Q, Value, When
from django.db.models.functions import Coalesce, Now, TruncMonth
from io import BytesIO
import os
import zlib
from django.conf import settings
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter

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
    """
    Dashboard general con validaciones defensivas para NULL values.
    Cada sección está protegida contra fallos.
    FASE 2C: Optimizado con aggregate() para documentos
    """
    try:
        # --- SECCIÓN 1: Conteos simples (SAFE) ---
        try:
            total_postulantes = Postulante.objects.count() or 0
            total_postulaciones = Postulacion.objects.count() or 0
            total_modalidades = Modalidad.objects.filter(activa=True).count() or 0
        except Exception as e:
            print(f"⚠️ Error en conteos simples: {e}")
            total_postulantes = 0
            total_postulaciones = 0
            total_modalidades = 0
        
        # --- SECCIÓN 2: Resumen de documentos CONSOLIDADO (SAFE NULL HANDLING) ---
        # FASE 2C: Una query en lugar de 2 (1 count + 1 aggregate →1 aggregate)
        total_documentos = 0
        docs_pendientes = 0
        docs_rechazados = 0
        try:
            documentos_resumen = DocumentoPostulacion.objects.aggregate(
                total_documentos=Count('id'),  # FASE 2C: Consolidado aquí
                documentos_pendientes=Count('id', filter=Q(estado='pendiente')),
                documentos_rechazados=Count('id', filter=Q(estado='rechazado')),
            )
            total_documentos = int(documentos_resumen.get('total_documentos') or 0)
            docs_pendientes = int(documentos_resumen.get('documentos_pendientes') or 0)
            docs_rechazados = int(documentos_resumen.get('documentos_rechazados') or 0)
        except Exception as e:
            print(f"⚠️ Error en documentos_resumen: {e}")
            total_documentos = 0
            docs_pendientes = 0
            docs_rechazados = 0
        
        # --- SECCIÓN 3: Postulaciones por estado (SAFE NULL HANDLING) ---
        postulaciones_estado_list = []
        try:
            postulaciones_por_estado = list(
                Postulacion.objects.values('estado_general')
                .annotate(total=Count('id'))
                .order_by('-total')
            )
            postulaciones_estado_list = [
                {
                    'estado': (item.get('estado_general') or 'Sin estado'),
                    'total': int(item.get('total') or 0)
                }
                for item in postulaciones_por_estado
            ]
        except Exception as e:
            print(f"⚠️ Error en postulaciones_por_estado: {e}")
            postulaciones_estado_list = []
        
        # --- SECCIÓN 4: Total titulados (SAFE) ---
        total_titulados = 0
        try:
            total_titulados = Postulacion.objects.filter(estado_general='TITULADO').count() or 0
        except Exception as e:
            print(f"⚠️ Error en total_titulados: {e}")
            total_titulados = 0

        # --- RETORNO: Estructura garantizada (NUNCA NULL) ---
        return {
            'total_postulaciones': int(total_postulaciones),
            'total_postulantes': int(total_postulantes),
            'total_modalidades': int(total_modalidades),
            'total_documentos': int(total_documentos),
            'postulaciones_por_estado_general': postulaciones_estado_list,
            'postulaciones_por_mes': [],
            'documentos_por_mes': [],
            'tiempo_promedio_por_mes': [],
            'postulaciones_por_etapa': [],
            'documentos_pendientes': int(docs_pendientes),
            'documentos_rechazados': int(docs_rechazados),
            'total_titulados': int(total_titulados),
            'tiempo_promedio_proceso_dias': 0.0,
        }
        
    except Exception as e:
        import traceback
        print(f"❌ ERROR CRÍTICO en dashboard_general: {str(e)}")
        print(traceback.format_exc())
        # Safety net - SIEMPRE devuelve estructura válida
        return {
            'total_postulaciones': 0,
            'total_postulantes': 0,
            'total_modalidades': 0,
            'total_documentos': 0,
            'postulaciones_por_estado_general': [],
            'postulaciones_por_mes': [],
            'documentos_por_mes': [],
            'tiempo_promedio_por_mes': [],
            'postulaciones_por_etapa': [],
            'documentos_pendientes': 0,
            'documentos_rechazados': 0,
            'total_titulados': 0,
            'tiempo_promedio_proceso_dias': 0.0,
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
    try:
        queryset = Postulacion.objects.filter(estado_general='TITULADO').exclude(tutor__isnull=True).exclude(tutor='')

        if carrera_id:
            try:
                carrera_value = str(carrera_id).strip()
                if carrera_value:
                    queryset = queryset.filter(postulante__carrera__iexact=carrera_value)
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
            .values('tutor')
            .annotate(
                total_titulados=Count('id', distinct=True),
                tiempo_promedio=Avg('duracion')
            )
            .order_by('-total_titulados')
        )

        results = []
        for item in stats:
            try:
                # Validación segura de campos
                tutor_nombre = (item.get('tutor') or '').strip()
                total_titulados = int(item.get('total_titulados') or 0)
                tiempo_promedio = item.get('tiempo_promedio')
                
                # Cálculo seguro de días
                tiempo_dias = 0.0
                if tiempo_promedio is not None:
                    try:
                        tiempo_dias = round(tiempo_promedio.total_seconds() / 86400, 2)
                    except (AttributeError, TypeError):
                        tiempo_dias = 0.0
                
                results.append({
                    'tutor_id': _tutor_hash(tutor_nombre),
                    'nombre': tutor_nombre,
                    'total_titulados': total_titulados,
                    'tiempo_promedio_dias': tiempo_dias
                })
            except Exception as e:
                print(f"⚠️ Error procesando item de tutor: {e}")
                continue
        
        return results
    
    except Exception as e:
        import traceback
        print(f"❌ Error en estadisticas_tutores: {str(e)}")
        print(traceback.format_exc())
        return []


def detalle_alumnos_titulados_por_tutor(tutor_id: int) -> list[dict]:
    """
    Obtiene el detalle de los alumnos titulados bajo la tutoría de un docente específico.
    """
    try:
        tutor_id_value = int(tutor_id)
    except (ValueError, TypeError):
        return []

    try:
        queryset = Postulacion.objects.filter(
            estado_general='TITULADO',
        ).exclude(tutor__isnull=True).exclude(tutor='').select_related('postulante', 'modalidad').annotate(
            fecha_fin=Coalesce(Max('documentos__fecha_revision'), Now()),
            duracion=ExpressionWrapper(
                F('fecha_fin') - F('fecha_postulacion'),
                output_field=DurationField(),
            )
        ).order_by('-fecha_fin')

        results = []
        for p in queryset:
            try:
                if _tutor_hash((p.tutor or '').strip()) == tutor_id_value:
                    duracion_dias = 0
                    if hasattr(p, 'duracion') and p.duracion:
                        try:
                            duracion_dias = p.duracion.days
                        except (AttributeError, TypeError):
                            duracion_dias = 0
                    
                    fecha_fin = None
                    if hasattr(p, 'fecha_fin') and p.fecha_fin:
                        try:
                            fecha_fin = p.fecha_fin.strftime('%Y-%m-%d')
                        except (AttributeError, TypeError):
                            fecha_fin = None
                    
                    results.append({
                        'postulacion_id': p.id,
                        'alumno_nombre': f"{p.postulante.nombre} {p.postulante.apellido}",
                        'alumno_codigo': p.postulante.codigo_estudiante,
                        'modalidad': p.modalidad.nombre if p.modalidad else 'N/A',
                        'titulo_trabajo': p.titulo_trabajo,
                        'gestion': p.gestion,
                        'fecha_inicio': p.fecha_postulacion.strftime('%Y-%m-%d') if p.fecha_postulacion else 'N/A',
                        'fecha_fin': fecha_fin,
                        'duracion_dias': duracion_dias,
                    })
            except Exception as e:
                print(f"⚠️ Error procesando alumno: {e}")
                continue
        
        return results
    except Exception as e:
        import traceback
        print(f"❌ Error en detalle_alumnos_titulados_por_tutor: {str(e)}")
        print(traceback.format_exc())
        return []


def _tutor_hash(value: str) -> int:
    return zlib.adler32(value.encode('utf-8')) & 0xFFFFFFFF


def reporte_eficiencia_carreras(year=None) -> list[dict]:
    """
    Genera un reporte de eficiencia por carrera universitaria:
    - Total de procesos iniciados.
    - Tasa de titulación (Titulados / Iniciados).
    - Tiempo promedio de titulación (en días).
    """
    try:
        queryset = Postulacion.objects.select_related('postulante')

        if year:
            try:
                year_int = int(year)
                queryset = queryset.filter(fecha_postulacion__year=year_int)
            except (ValueError, TypeError):
                pass

        # Agrupar por carrera para conteos
        stats = queryset.values(
            'postulante__carrera',
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
        ).values('postulante__carrera').annotate(
            tiempo_promedio=Avg('duracion')
        )
        
        tiempos_map = {item['postulante__carrera']: item['tiempo_promedio'] for item in tiempos_queryset}

        results = []
        for item in stats:
            try:
                carrera = item['postulante__carrera'] or 'Sin Carrera Asignada'
                total_iniciados = int(item['total_iniciados'] or 0)
                total_titulados = int(item['total_titulados'] or 0)
                
                # Cálculo seguro de tasa de titulación
                tasa = 0.0
                if total_iniciados > 0:
                    tasa = round((total_titulados / total_iniciados * 100), 2)
                
                # Cálculo seguro de tiempo promedio
                tiempo_dias = 0.0
                tiempo_promedio = tiempos_map.get(item['postulante__carrera'])
                if tiempo_promedio is not None:
                    try:
                        tiempo_dias = round(tiempo_promedio.total_seconds() / 86400, 2)
                    except (AttributeError, TypeError):
                        tiempo_dias = 0.0
                
                results.append({
                    'carrera': carrera,
                    'total_iniciados': total_iniciados,
                    'total_titulados': total_titulados,
                    'tasa_titulacion': tasa,
                    'tiempo_promedio_dias': tiempo_dias
                })
            except Exception as e:
                print(f"⚠️ Error procesando carrera: {e}")
                continue
        
        return results
    except Exception as e:
        import traceback
        print(f"❌ Error en reporte_eficiencia_carreras: {str(e)}")
        print(traceback.format_exc())
        return []


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
    for i, column_cells in enumerate(ws.columns, 1):
        max_length = max(len(str(cell.value) or "") for cell in column_cells)
        column_letter = get_column_letter(i)
        ws.column_dimensions[column_letter].width = max_length + 2

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="estadisticas_tutores.xlsx"'
    return response
