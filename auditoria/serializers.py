from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import AuditoriaLog

User = get_user_model()


class SimpleUserSerializer(serializers.ModelSerializer):
    """Serializer simple para usuario en contexto de auditoría."""
    nombre_completo = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'nombre_completo']


class AuditoriaLogSerializer(serializers.ModelSerializer):
    """Serializer detallado para logs de auditoría."""
    usuario = SimpleUserSerializer(read_only=True, allow_null=True)
    usuario_id = serializers.IntegerField(source='usuario.id', read_only=True, allow_null=True)
    usuario_nombre = serializers.CharField(
        source='usuario.get_full_name', read_only=True, allow_null=True
    )
    
    class Meta:
        model = AuditoriaLog
        fields = [
            'id', 'usuario', 'usuario_id', 'usuario_nombre', 'accion',
            'modelo_afectado', 'objeto_id', 'estado_anterior', 'estado_nuevo',
            'detalles', 'fecha'
        ]
        read_only_fields = fields
