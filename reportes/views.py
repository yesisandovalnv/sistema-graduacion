import logging
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from config.permissions import PuedeVerDashboardInstitucionalPermission
from .health import HealthCheckService  # FASE 4: Health check

from .services import dashboard_general, detalle_alumnos_titulados_por_tutor, estadisticas_tutores, generar_excel_tutores, reporte_eficiencia_carreras

logger = logging.getLogger(__name__)


class DashboardGeneralView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            logger.info("Dashboard request por usuario: %s", request.user.id)
            logger.debug("Request headers: %s", dict(request.headers))
            logger.debug("Request path: %s", request.path)
            logger.debug("Request method: %s", request.method)
            
            data = dashboard_general()
            
            logger.debug("Dashboard data prepared: %s", str(data)[:200])
            return Response(data, status=200)
            
        except Exception as e:
            logger.error("❌ ERROR en DashboardGeneralView: %s", str(e), exc_info=True)
            import traceback
            logger.error("Traceback completo:\n%s", traceback.format_exc())
            return Response(
                {'detail': 'Internal server error', 'error': str(e)},
                status=500
            )


class EstadisticasTutoresView(APIView):
    permission_classes = [PuedeVerDashboardInstitucionalPermission]

    def get(self, request):
        try:
            logger.info("EstadisticasTutoresView request - year: %s, carrera_id: %s", 
                       request.query_params.get('year'), request.query_params.get('carrera_id'))
            year = request.query_params.get('year')
            carrera_id = request.query_params.get('carrera_id')
            data = estadisticas_tutores(year, carrera_id)
            
            # Si no hay datos, retornar lista vacía con estructura válida
            if data is None:
                data = []
            
            paginator = PageNumberPagination()
            paginator.page_size = 20
            result_page = paginator.paginate_queryset(data, request)
            return paginator.get_paginated_response(result_page)
        except Exception as e:
            logger.error("Error en EstadisticasTutoresView: %s", str(e), exc_info=True)
            return Response(
                {'detail': 'Internal server error'},
                status=500
            )


class ExportarEstadisticasTutoresView(APIView):
    permission_classes = [PuedeVerDashboardInstitucionalPermission]

    def get(self, request):
        try:
            logger.info("ExportarEstadisticasTutoresView request - year: %s, carrera_id: %s", 
                       request.query_params.get('year'), request.query_params.get('carrera_id'))
            year = request.query_params.get('year')
            carrera_id = request.query_params.get('carrera_id')
            data = estadisticas_tutores(year, carrera_id)
            if not data:
                logger.warning("No data available for export - year: %s, carrera_id: %s", year, carrera_id)
                return Response({'detail': 'No data available'}, status=400)
            return generar_excel_tutores(data)
        except Exception as e:
            logger.error("Error en ExportarEstadisticasTutoresView: %s", str(e), exc_info=True)
            return Response(
                {'detail': 'Internal server error'},
                status=500
            )


class DetalleAlumnosTutorView(APIView):
    permission_classes = [PuedeVerDashboardInstitucionalPermission]

    def get(self, request, tutor_id):
        try:
            logger.info("DetalleAlumnosTutorView request - tutor_id: %s", tutor_id)
            result = detalle_alumnos_titulados_por_tutor(tutor_id)
            if result is None:
                result = []
            return Response(result, status=200)
        except Exception as e:
            logger.error("Error en DetalleAlumnosTutorView (tutor_id: %s): %s", tutor_id, str(e), exc_info=True)
            return Response(
                {'detail': 'Internal server error'},
                status=500
            )


class ReporteEficienciaCarrerasView(APIView):
    permission_classes = [PuedeVerDashboardInstitucionalPermission]

    def get(self, request):
        try:
            logger.info("ReporteEficienciaCarrerasView request - year: %s", request.query_params.get('year'))
            year = request.query_params.get('year')
            result = reporte_eficiencia_carreras(year)
            if result is None:
                result = []
            return Response(result, status=200)
        except Exception as e:
            logger.error("Error en ReporteEficienciaCarrerasView: %s", str(e), exc_info=True)
            return Response(
                {'detail': 'Internal server error'},
                status=500
            )


# FASE 4: Health Check Endpoint (sin autenticación)
class HealthCheckView(APIView):
    """
    Health check endpoint para monitoreo del sistema
    Verifica: PostgreSQL, Redis/Cache, estado general
    """
    permission_classes = [AllowAny]  # No requiere autenticación
    
    def get(self, request):
        try:
            health_data = HealthCheckService.check_overall_health()
            # HTTP 200 si todo está OK, 503 si algo está mal
            status_code = 200 if health_data['status'] == 'healthy' else 503
            return Response(health_data, status=status_code)
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}", exc_info=True)
            return Response(
                {
                    'status': 'unhealthy',
                    'error': str(e),
                    'service': 'Sistema de Graduación'
                },
                status=503
            )
