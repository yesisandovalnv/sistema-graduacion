from rest_framework import serializers
from .models import Etapa, Modalidad


class EtapaSerializer(serializers.ModelSerializer):
    """Serializer para etapas."""
    modalidad_nombre = serializers.CharField(source='modalidad.nombre', read_only=True)
    
    class Meta:
        model = Etapa
        fields = ['id', 'nombre', 'orden', 'modalidad', 'modalidad_nombre', 'activo']
        read_only_fields = ['id']


class ModalidadListSerializer(serializers.ModelSerializer):
    """Serializer para listado de modalidades."""
    total_etapas = serializers.SerializerMethodField()
    
    class Meta:
        model = Modalidad
        fields = ['id', 'nombre', 'descripcion', 'activa', 'total_etapas', 'creada_en']
        read_only_fields = ['id', 'creada_en']
    
    def get_total_etapas(self, obj):
        """Retorna el número de etapas en la modalidad."""
        return obj.etapas.filter(activo=True).count()


class ModalidadDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para modalidades con etapas."""
    etapas = EtapaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Modalidad
        fields = ['id', 'nombre', 'descripcion', 'activa', 'etapas', 'creada_en', 'actualizada_en']
        read_only_fields = ['id', 'creada_en', 'actualizada_en']


class ModalidadSerializer(serializers.ModelSerializer):
    """Serializer general para modalidades."""
    class Meta:
        model = Modalidad
        fields = '__all__'
        read_only_fields = ['id', 'creada_en', 'actualizada_en']
