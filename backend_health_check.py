#!/usr/bin/env python
"""
Django Backend Health Check
Verifies that the backend is working correctly
"""

import os
import sys
import json
import django
import requests

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from usuarios.models import CustomUser

def check_database():
    """Check database connection"""
    print('\n🔍 Verificando Base de Datos...')
    try:
        count = CustomUser.objects.count()
        print(f'   ✅ Conexión exitosa')
        print(f'   📊 Total usuarios: {count}')
        return True
    except Exception as e:
        print(f'   ❌ Error: {str(e)}')
        return False

def check_jwt_config():
    """Check JWT configuration"""
    print('\n🔍 Verificando JWT Configuration...')
    try:
        rest_settings = settings.REST_FRAMEWORK
        print(f'   ✅ REST Framework configurado')
        print(f'   🔑 Auth class: {rest_settings.get("DEFAULT_AUTHENTICATION_CLASSES", [None])[0]}')
        
        jwt_settings = settings.SIMPLE_JWT
        print(f'   ⏱️  Access token lifetime: {jwt_settings.get("ACCESS_TOKEN_LIFETIME")}')
        print(f'   ⏱️  Refresh token lifetime: {jwt_settings.get("REFRESH_TOKEN_LIFETIME")}')
        return True
    except Exception as e:
        print(f'   ❌ Error: {str(e)}')
        return False

def check_cors():
    """Check CORS configuration"""
    print('\n🔍 Verificando CORS...')
    try:
        origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
        if origins:
            print(f'   ✅ CORS configurado')
            for origin in origins:
                print(f'      - {origin}')
        else:
            print(f'   ⚠️  CORS_ALLOWED_ORIGINS vacío')
        return True
    except Exception as e:
        print(f'   ❌ Error: {str(e)}')
        return False

def check_endpoints():
    """Check if endpoints are responding"""
    print('\n🔍 Verificando Endpoints...')
    
    endpoints = [
        ('POST', 'http://localhost:8000/api/auth/login/', {'username': 'admin', 'password': 'wrong'}),
        ('GET', 'http://localhost:8000/api/postulantes/', None),
    ]
    
    for method, url, data in endpoints:
        try:
            if method == 'POST':
                response = requests.post(url, json=data, timeout=5)
            else:
                response = requests.get(url, timeout=5)
            
            status = '✅' if response.status_code < 500 else '❌'
            print(f'   {status} {method} {url.split("/api/")[1]}: {response.status_code}')
        except requests.exceptions.ConnectionError:
            print(f'   ❌ {method} {url.split("/api/")[1]}: Cannot connect (backend not running)')
        except Exception as e:
            print(f'   ❌ {method} {url.split("/api/")[1]}: {str(e)}')

def check_installed_apps():
    """Check if required apps are installed"""
    print('\n🔍 Verificando Aplicaciones Instaladas...')
    
    required_apps = [
        'rest_framework',
        'rest_framework_simplejwt',
        'corsheaders',
    ]
    
    installed = settings.INSTALLED_APPS
    for app in required_apps:
        if app in installed:
            print(f'   ✅ {app}')
        else:
            print(f'   ❌ {app} (FALTA)')

def main():
    print('╔════════════════════════════════════════════════╗')
    print('║   Django Backend - Health Check               ║')
    print('╚════════════════════════════════════════════════╝')
    
    checks = [
        ('Database', check_database),
        ('INSTALLED_APPS', check_installed_apps),
        ('JWT', check_jwt_config),
        ('CORS', check_cors),
        ('Endpoints', check_endpoints),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f'❌ Error en {name}: {str(e)}')
            results[name] = False
    
    # Summary
    print('\n' + '=' * 50)
    print('📋 RESUMEN')
    print('=' * 50)
    
    all_passed = all(results.values())
    
    for name, result in results.items():
        status = '✅' if result else '❌'
        print(f'{status} {name}')
    
    print('\n' + '=' * 50)
    
    if all_passed:
        print('✅ Todo está funcionando correctamente!')
    else:
        print('⚠️  Revisar los errores marcados con ❌')
    
    sys.exit(0 if all_passed else 1)

if __name__ == '__main__':
    main()
