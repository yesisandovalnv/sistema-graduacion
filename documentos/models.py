from django.conf import settings
from django.db import models


class TipoDocumento(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    etapa = models.ForeignKey(
        'modalidades.Etapa',
        on_delete=models.PROTECT,
        related_name='tipos_documento',
        null=True,
        blank=True,
    )
    descripcion = models.TextField(blank=True)
    obligatorio = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class DocumentoPostulacion(models.Model):
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    )

    postulacion = models.ForeignKey('postulantes.Postulacion', on_delete=models.CASCADE, related_name='documentos')
    tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.PROTECT, related_name='documentos_cargados')
    archivo = models.FileField(upload_to='documentos/postulaciones/')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    comentario_revision = models.TextField(blank=True)
    revisado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documentos_revisados',
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)
    fecha_revision = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-fecha_subida']
        unique_together = ('postulacion', 'tipo_documento')
        permissions = (
            ('puede_aprobar_documentos', 'Puede aprobar documentos'),
        )

    def __str__(self):
        return f"{self.postulacion} - {self.tipo_documento.nombre}"
