#!/usr/bin/env python
"""Test de integración real frontend-backend"""

import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '.')

try:
    django.setup()
    
    from django.contrib.auth import get_user_model
    from rest_framework.test import APIRequestFactory
    from rest_framework_simplejwt.tokens import RefreshToken
    from reportes.views import DashboardGeneralView
    from postulantes.views import PostulanteViewSet
    
    User = get_user_model()
    
    print("="*70)
    print("TEST DE INTEGRACIÓN: Frontend-Backend")
    print("="*70)
    
    # 1. Crear usuario
    print("\n[1] USUARIO & AUTENTICACIÓN")
    print("-"*70)
    user, created = User.objects.get_or_create(
        username='test_diagnostic',
        defaults={'email': 'test@test.com'}
    )
    user.set_password('test123')
    user.save()
    print(f"✓ Usuario: {user.username}")
    
    # 2. JWT Token
    print("\n[2] GENERANDO JWT TOKEN")
    print("-"*70)
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    print(f"✓ Token generado: {access_token[:50]}...")
    
    factory = APIRequestFactory()
    
    # 3. TEST Dashboard General
    print("\n[3] TEST ENDPOINT: /api/reportes/dashboard-general/")
    print("-"*70)
    request_auth = factory.get(
        '/api/reportes/dashboard-general/',
        HTTP_AUTHORIZATION=f'Bearer {access_token}'
    )
    request_auth.user = user
    view = DashboardGeneralView.as_view()
    response = view(request_auth)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.data
        print(f"✓ Response es dict: {isinstance(data, dict)}")
        print(f"✓ Keys presentes: {list(data.keys())}")
        
        # Validar campos esperados por frontend
        required_fields = ['total_postulantes', 'documentos_pendientes', 'total_titulados']
        missing = [k for k in required_fields if k not in data]
        
        if missing:
            print(f"✗ FALTAN CAMPOS: {missing}")
        else:
            print(f"✓ Todos los campos requeridos presentes")
            print(f"  - total_postulantes: {data['total_postulantes']}")
            print(f"  - documentos_pendientes: {data['documentos_pendientes']}")
            print(f"  - total_titulados: {data['total_titulados']}")
    else:
        print(f"✗ ERROR: {response.data}")
    
    # 4. TEST Postulantes List
    print("\n[4] TEST ENDPOINT: /api/postulantes/")
    print("-"*70)
    request_auth = factory.get('/api/postulantes/', HTTP_AUTHORIZATION=f'Bearer {access_token}')
    request_auth.user = user
    view = PostulanteViewSet.as_view({'get': 'list'})
    response = view(request_auth)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.data
        print(f"✓ Response es dict o list: {isinstance(data, (dict, list))}")
        
        if isinstance(data, dict) and 'results' in data:
            results = data['results']
            print(f"✓ Formato paginado detectado")
            print(f"✓ Total items: {len(results)}")
            if results:
                print(f"✓ Campos en primer item: {list(results[0].keys())}")
                # Validar campos esperados por frontend
                expected_fields = ['nombre', 'apellido', 'ci', 'codigo_estudiante']
                missing = [k for k in expected_fields if k not in results[0]]
                if missing:
                    print(f"✗ FALTAN CAMPOS en response: {missing}")
                else:
                    print(f"✓ Todos los campos presentes para DataTable")
        elif isinstance(data, list):
            print(f"✓ Response es lista simple")
            print(f"✓ Total items: {len(data)}")
    else:
        print(f"✗ ERROR: {response.data}")
    
    print("\n" + "="*70)
    print("FIN TEST DE INTEGRACIÓN")
    print("="*70)
    
except Exception as e:
    print(f"\n✗ ERROR CRÍTICO: {str(e)}")
    import traceback
    traceback.print_exc()
