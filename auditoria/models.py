from django.conf import settings
from django.db import models


class AuditoriaLog(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='auditoria_logs',
    )
    accion = models.CharField(max_length=100)
    modelo_afectado = models.CharField(max_length=100)
    objeto_id = models.CharField(max_length=64)
    estado_anterior = models.JSONField(null=True, blank=True)
    estado_nuevo = models.JSONField(null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    detalles = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-fecha']
        permissions = (
            ('puede_ver_auditoria', 'Puede ver auditoria'),
        )

    def __str__(self):
        return f"{self.fecha:%Y-%m-%d %H:%M} - {self.accion} - {self.modelo_afectado}#{self.objeto_id}"
