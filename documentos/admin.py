from django.contrib import admin

from .models import DocumentoPostulacion, TipoDocumento


@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'etapa', 'obligatorio', 'activo')
    list_filter = ('etapa__modalidad', 'etapa', 'obligatorio', 'activo')
    search_fields = ('nombre', 'etapa__nombre', 'etapa__modalidad__nombre')


@admin.register(DocumentoPostulacion)
class DocumentoPostulacionAdmin(admin.ModelAdmin):
    list_display = ('postulacion', 'tipo_documento', 'estado', 'revisado_por', 'fecha_subida')
    list_filter = ('estado', 'tipo_documento')
    search_fields = ('postulacion__postulante__usuario__username',)
