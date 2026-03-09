from django.contrib import admin

from .models import AuditoriaLog


@admin.register(AuditoriaLog)
class AuditoriaLogAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'usuario', 'accion', 'modelo_afectado', 'objeto_id')
    list_filter = ('accion', 'modelo_afectado', 'fecha')
    search_fields = ('usuario__username', 'accion', 'modelo_afectado', 'objeto_id')
    readonly_fields = (
        'usuario',
        'accion',
        'modelo_afectado',
        'objeto_id',
        'estado_anterior',
        'estado_nuevo',
        'fecha',
        'detalles',
    )

