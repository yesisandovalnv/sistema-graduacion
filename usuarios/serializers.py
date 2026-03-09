from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer para CustomUser completo (lectura)."""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'is_active', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined']


class CustomUserDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para CustomUser con permisos."""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'is_active', 'is_staff', 'is_superuser',
            'date_joined', 'permissions'
        ]
        read_only_fields = ['id', 'date_joined', 'permissions']
    
    def get_permissions(self, obj):
        """Retorna lista de permisos del usuario."""
        if obj.is_superuser:
            return ['admin']
        return list(obj.user_permissions.values_list('codename', flat=True))


class LoginSerializer(TokenObtainPairSerializer):
    """Serializer para login con información del usuario mejorada."""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['username'] = user.username
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        
        # Información del usuario en respuesta
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'role_display': user.get_role_display(),
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        }
        
        return data
