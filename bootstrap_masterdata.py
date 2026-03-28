#!/usr/bin/env python
"""
Bootstrap mejorado: Crea todas las MasterData necesaria
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '/app')
django.setup()

from django.contrib.auth import get_user_model
from modalidades.models import Modalidad, Etapa
from documentos.models import TipoDocumento

User = get_user_model()

print("\n🔧 Bootstrap: Creando MasterData...\n")

# 1. Admin user
admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@admin.com',
        'is_staff': True,
        'is_superuser': True
    }
)
if created:
    admin_user.set_password('password')
    admin_user.save()
    print("✓ Admin user creado")
else:
    print("✓ Admin user ya existe")

# 2. Modalidad Tesis
modalidad_tesis, created = Modalidad.objects.get_or_create(
    nombre='Tesis',
    defaults={
        'descripcion': 'Modalidad de Tesis de Grado',
        'activa': True
    }
)
if created:
    print("✓ Modalidad 'Tesis' creada")
else:
    print("✓ Modalidad 'Tesis' ya existe")

# 3. Étapas para Tesis
etapas_tesis = [
    {'orden': 1, 'nombre': 'Propuesta/Perfil'},
    {'orden': 2, 'nombre': 'Etapa Privada'},
    {'orden': 3, 'nombre': 'Defensa Pública'},
    {'orden': 4, 'nombre': 'Correcciones'},
]

for etapa_data in etapas_tesis:
    etapa, created = Etapa.objects.get_or_create(
        modalidad=modalidad_tesis,
        orden=etapa_data['orden'],
        defaults={
            'nombre': etapa_data['nombre'],
            'activo': True
        }
    )
    if created:
            print(f"  ✓ Etapa {etapa_data['orden']}: {etapa_data['nombre']} creada")
        else:
            print(f"  ✓ Etapa {etapa_data['orden']}: {etapa_data['nombre']} ya existe")

# 4. Tipos de Documentos
primera_etapa = Etapa.objects.filter(modalidad=modalidad_tesis, orden=1).first()
if primera_etapa:
    tipos_docs = [
        {'nombre': 'Propuesta de Tesis', 'obligatorio': True, 'orden': 1},
        {'nombre': 'CV del Autor', 'obligatorio': True, 'orden': 2},
        {'nombre': 'Carta de Aceptación de Tutor', 'obligatorio': True, 'orden': 3},
    ]
    
    for doc_data in tipos_docs:
        tipo_doc, created = TipoDocumento.objects.get_or_create(
            nombre=doc_data['nombre'],
            defaults={
                'etapa': primera_etapa,
                'descripcion': doc_data['nombre'],
                'obligatorio': doc_data['obligatorio'],
                'orden': doc_data.get('orden', 1),
                'activo': True
            }
        )
        if created:
            print(f"  ✓ Tipo Doc: {doc_data['nombre']} creado")
        else:
            print(f"  ✓ Tipo Doc: {doc_data['nombre']} ya existe")

print("\n✅ Bootstrap completado\n")

# Verificación
from postulantes.models import Postulante
print(f"📊 Estado de BD:")
print(f"   • Usuarios: {User.objects.count()}")
print(f"   • Modalidades: {Modalidad.objects.count()}")
print(f"   • Etapas: {Etapa.objects.count()}")
print(f"   • Tipos Documentos: {TipoDocumento.objects.count()}")
print(f"   • Postulantes: {Postulante.objects.count()}\n")
