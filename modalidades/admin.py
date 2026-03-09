from django.contrib import admin

from .models import Etapa, Modalidad


@admin.register(Modalidad)
class ModalidadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activa', 'creada_en')
    list_filter = ('activa',)
    search_fields = ('nombre',)


@admin.register(Etapa)
class EtapaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'modalidad', 'orden', 'activo')
    list_filter = ('modalidad', 'activo')
    search_fields = ('nombre', 'modalidad__nombre')
    ordering = ('modalidad__nombre', 'orden')
