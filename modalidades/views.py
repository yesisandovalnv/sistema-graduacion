from rest_framework import filters, viewsets

from config.permissions import CRUDModelPermission
from .models import Etapa, Modalidad
from .serializers import EtapaSerializer, ModalidadSerializer


class ModalidadViewSet(viewsets.ModelViewSet):
    queryset = Modalidad.objects.all()
    serializer_class = ModalidadSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'creada_en', 'actualizada_en']
    ordering = ['nombre']

    def get_permissions(self):
        if self.action in {'create', 'update', 'partial_update', 'destroy'}:
            return [CRUDModelPermission()]
        return super().get_permissions()


class EtapaViewSet(viewsets.ModelViewSet):
    queryset = Etapa.objects.select_related('modalidad').all()
    serializer_class = EtapaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'modalidad__nombre']
    ordering_fields = ['orden', 'nombre', 'modalidad__nombre']
    ordering = ['modalidad__nombre', 'orden']

    def get_permissions(self):
        if self.action in {'create', 'update', 'partial_update', 'destroy'}:
            return [CRUDModelPermission()]
        return super().get_permissions()
