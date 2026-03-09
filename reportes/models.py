from django.conf import settings
from django.db import models


class ReporteGenerado(models.Model):
    TIPO_CHOICES = (
        ('postulaciones', 'Postulaciones'),
        ('documentos', 'Documentos'),
        ('estadistico', 'Estadistico'),
    )
    FORMATO_CHOICES = (
        ('pdf', 'PDF'),
        ('xlsx', 'Excel'),
        ('csv', 'CSV'),
    )

    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    formato = models.CharField(max_length=10, choices=FORMATO_CHOICES)
    generado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reportes_generados',
    )
    filtros = models.JSONField(default=dict, blank=True)
    archivo = models.FileField(upload_to='reportes/')
    total_registros = models.PositiveIntegerField(default=0)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado_en']

    def __str__(self):
        return f"{self.get_tipo_display()} ({self.formato.upper()}) - {self.creado_en:%Y-%m-%d %H:%M}"
