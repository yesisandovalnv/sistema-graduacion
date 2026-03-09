#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from usuarios.models import CustomUser

try:
    # Obtener el usuario actual admin
    user = CustomUser.objects.get(username='admin')
    
    # Cambiar username a admin@admin.com
    user.username = 'admin@admin.com'
    user.email = 'admin@admin.com'
    
    # Establecer nueva contraseña
    user.set_password('password')
    user.save()
    
    print('✅ Credenciales actualizadas!')
    print(f'Usuario: {user.username}')
    print('Contraseña: password')
except CustomUser.DoesNotExist:
    print('❌ Usuario admin no existe')
except Exception as e:
    print(f'❌ Error: {e}')
