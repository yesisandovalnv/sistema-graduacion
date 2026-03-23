import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from usuarios.models import CustomUser

users = CustomUser.objects.all()
print(f'Total users: {users.count()}\n')
for u in users:
    print(f'  {u.username:25} role={str(u.role):15} is_staff={u.is_staff}')
