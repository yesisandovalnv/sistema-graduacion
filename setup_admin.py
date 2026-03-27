from usuarios.models import CustomUser

# Asegurar que admin existe con la contraseña correcta
admin, created = CustomUser.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@sistema.com',
        'first_name': 'Admin',
        'last_name': 'Sistema',
        'is_staff': True,
        'is_superuser': True,
        'is_active': True,
        'role': 'admin'
    }
)

# Establecer contraseña
admin.set_password('password')
admin.save()

# Eliminar todos los otros usuarios
deleted_count, _ = CustomUser.objects.exclude(username='admin').delete()

print(f"✅ Admin creado/actualizado")
print(f"✅ {deleted_count} usuarios eliminados")
print(f"✅ Total de usuarios ahora: {CustomUser.objects.count()}")
