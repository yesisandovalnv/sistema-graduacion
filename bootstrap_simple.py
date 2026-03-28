#!/usr/bin/env python
"""Bootstrap mejorado: Crea todas las MasterData necesaria"""
import os, sys, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '/app')
django.setup()

from django.contrib.auth import get_user_model
from modalidades.models import Modalidad, Etapa
from documentos.models import TipoDocumento
from postulantes.models import Postulante

User = get_user_model()

print("\n🔧 Bootstrap: Creando MasterData...\n")

# 1. Admin
admin, _ = User.objects.get_or_create(
    username='admin',
    defaults={'email': 'admin@admin.com', 'is_staff': True, 'is_superuser': True}
)
admin.set_password('password')
admin.save()
print("✓ Admin user")

# 2. Modalidad
mod, created = Modalidad.objects.get_or_create(
    nombre='Tesis',
    defaults={'descripcion': 'Modalidad de Tesis de Grado', 'activa': True}
)
print("✓ Modalidad 'Tesis'" + (" creada" if created else " (existente)"))

# 3. Etapas
for orden, nombre in [(1, 'Propuesta'), (2, 'Privada'), (3, 'Pública'), (4, 'Correcciones')]:
    etapa, created = Etapa.objects.get_or_create(
        modalidad=mod,
        orden=orden,
        defaults={'nombre': nombre, 'activo': True}
    )
    print(f"  ✓ Etapa {orden}: {nombre}" + (" creada" if created else " (existente)"))

# 4. Tipos de Documentos
primera = Etapa.objects.filter(modalidad=mod, orden=1).first()
for nombre in ['Propuesta de Tesis', 'CV del Autor', 'Carta de Tutor']:
    doc, created = TipoDocumento.objects.get_or_create(
        nombre=nombre,
        defaults={'etapa': primera, 'descripcion': nombre, 'obligatorio': True, 'activo': True}
    )
    print(f"  ✓ Doc: {nombre}" + (" creado" if created else " (existente)"))

print(f"\n📊 BD Stats:")
print(f"   Usuarios: {User.objects.count()}")
print(f"   Modalidades: {Modalidad.objects.count()}")
print(f"   Etapas: {Etapa.objects.count()}")
print(f"   Tipos Doc: {TipoDocumento.objects.count()}")
print(f"   Postulantes: {Postulante.objects.count()}")
print(f"\n✅ Bootstrap completado\n")
