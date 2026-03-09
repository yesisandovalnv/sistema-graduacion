from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView

from config.permissions import PuedeVerDashboardInstitucionalPermission

from .services import dashboard_general, detalle_alumnos_titulados_por_tutor, estadisticas_tutores, generar_excel_tutores, reporte_eficiencia_carreras


class DashboardGeneralView(APIView):
    permission_classes = [PuedeVerDashboardInstitucionalPermission]

    def get(self, request):
        return Response(dashboard_general())


class EstadisticasTutoresView(APIView):
    permission_classes = [PuedeVerDashboardInstitucionalPermission]

    def get(self, request):
        year = request.query_params.get('year')
        carrera_id = request.query_params.get('carrera_id')
        data = estadisticas_tutores(year, carrera_id)
        paginator = PageNumberPagination()
        paginator.page_size = 20
        result_page = paginator.paginate_queryset(data, request)
        return paginator.get_paginated_response(result_page)


class ExportarEstadisticasTutoresView(APIView):
    permission_classes = [PuedeVerDashboardInstitucionalPermission]

    def get(self, request):
        year = request.query_params.get('year')
        carrera_id = request.query_params.get('carrera_id')
        data = estadisticas_tutores(year, carrera_id)
        return generar_excel_tutores(data)


class DetalleAlumnosTutorView(APIView):
    permission_classes = [PuedeVerDashboardInstitucionalPermission]

    def get(self, request, tutor_id):
        return Response(detalle_alumnos_titulados_por_tutor(tutor_id))


class ReporteEficienciaCarrerasView(APIView):
    permission_classes = [PuedeVerDashboardInstitucionalPermission]

    def get(self, request):
        year = request.query_params.get('year')
        return Response(reporte_eficiencia_carreras(year))
