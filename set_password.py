#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from usuarios.models import CustomUser

try:
    user = CustomUser.objects.get(username='admin')
    user.set_password('admin123')
    user.save()
    print('✅ Contraseña establecida correctamente!')
    print('Usuario: admin')
    print('Contraseña: admin123')
except CustomUser.DoesNotExist:
    print('❌ Usuario admin no existe')
except Exception as e:
    print(f'❌ Error: {e}')
