#!/usr/bin/env python
"""Auditoría: Verificar exactamente qué retorna el endpoint"""
import requests
import json

# Obtener token
login_response = requests.post('http://localhost/api/token/', json={
    'username': 'admin',
    'password': 'password'
})

if login_response.status_code != 200:
    print('❌ LOGIN FALLIDO')
    print(login_response.text)
    exit(1)

token = login_response.json()['access']
print('✅ Token obtenido')
print()

# Llamar endpoint
response = requests.get('http://localhost/api/reportes/dashboard-general/', headers={
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
})

print('📊 ENDPOINT /api/reportes/dashboard-general/')
print('═' * 70)
print(f'Status Code: {response.status_code}')
print()

data = response.json()

# Mostrar campo satisfaccion_score
satisfaccion = data.get('satisfaccion_score')
print(f'satisfaccion_score VALUE: {repr(satisfaccion)}')
print(f'satisfaccion_score TYPE: {type(satisfaccion).__name__}')
print(f'¿Es string N/A? {satisfaccion == "N/A"}')
print(f'¿Es número 0.0? {satisfaccion == 0.0}')
print(f'¿Es número 0? {satisfaccion == 0}')
print()

# Mostrar JSON completo
print('JSON COMPLETO:')
print(json.dumps(data, indent=2, default=str))
