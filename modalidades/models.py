from django.db import models


class Modalidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)
    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Etapa(models.Model):
    nombre = models.CharField(max_length=100)
    orden = models.PositiveIntegerField()
    modalidad = models.ForeignKey(Modalidad, on_delete=models.CASCADE, related_name='etapas')
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['modalidad__nombre', 'orden']
        constraints = [
            models.UniqueConstraint(fields=['modalidad', 'orden'], name='unique_orden_por_modalidad'),
        ]

    def __str__(self):
        return f"{self.modalidad.nombre} - {self.orden}. {self.nombre}"
