from django.contrib import admin

from .models import ReporteGenerado


@admin.register(ReporteGenerado)
class ReporteGeneradoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'formato', 'generado_por', 'total_registros', 'creado_en')
    list_filter = ('tipo', 'formato', 'creado_en')
    search_fields = ('generado_por__username',)
