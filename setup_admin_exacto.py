#!/usr/bin/env python
import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from usuarios.models import CustomUser

# Credenciales exactas solicitadas
USERNAME = 'admin'
PASSWORD = 'password'
EMAIL = 'admin@admin.com'

print("🔍 Verificando usuario administrador...")

# Verificar si existe
try:
    admin_user = CustomUser.objects.get(username=USERNAME)
    print(f"✅ Usuario '{USERNAME}' EXISTE")
    print(f"   Email actual: {admin_user.email}")
    print(f"   Es superusuario: {admin_user.is_superuser}")
    print(f"   Está activo: {admin_user.is_active}")
    
    # Actualizar credenciales si es necesario
    if admin_user.email != EMAIL:
        print(f"\n⚠️  Actualizando email: {admin_user.email} → {EMAIL}")
        admin_user.email = EMAIL
    
    admin_user.set_password(PASSWORD)
    admin_user.is_active = True
    admin_user.is_superuser = True
    admin_user.is_staff = True
    admin_user.save()
    print(f"✅ Contraseña actualizada a: {PASSWORD}")
    print(f"✅ Usuario listo para usar\n")
    
except CustomUser.DoesNotExist:
    print(f"❌ Usuario '{USERNAME}' NO EXISTE - Creando...\n")
    
    admin_user = CustomUser.objects.create_superuser(
        username=USERNAME,
        email=EMAIL,
        password=PASSWORD
    )
    admin_user.is_active = True
    admin_user.save()
    
    print(f"✅ Usuario creado exitosamente")
    print(f"   Username: {USERNAME}")
    print(f"   Email: {EMAIL}")
    print(f"   Contraseña: {PASSWORD}")
    print(f"   Rol: Superusuario")
    print(f"   Está activo: {admin_user.is_active}\n")

# Mostrar todos los usuarios disponibles
print("📋 Usuarios en el sistema:")
for user in CustomUser.objects.all().order_by('username'):
    role = getattr(user, 'role', 'N/A')
    print(f"   • {user.username:20} | Email: {user.email:25} | Role: {str(role):15} | Activo: {user.is_active}")

print(f"\n✨ Total de usuarios: {CustomUser.objects.count()}")
print(f"🎯 Puedes iniciar sesión con: admin / password")
