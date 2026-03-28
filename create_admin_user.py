from django.contrib.auth import get_user_model

User = get_user_model()

# Crear usuario admin si no existe
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@admin.com',
        password='password'
    )
    print("✅ Usuario admin creado")
else:
    print("ℹ️  Usuario admin ya existe")
