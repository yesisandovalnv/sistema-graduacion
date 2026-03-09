from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
import ast

from django_filters.rest_framework import DjangoFilterBackend
from config.permissions import PuedeVerAuditoriaPermission

from .models import AuditoriaLog
from .serializers import AuditoriaLogSerializer


class AuditoriaLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditoriaLog.objects.select_related('usuario').all()
    serializer_class = AuditoriaLogSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['usuario__username', 'accion', 'modelo_afectado', 'objeto_id']
    ordering_fields = ['fecha', 'accion', 'modelo_afectado']
    ordering = ['-fecha']
    permission_classes = [PuedeVerAuditoriaPermission]

