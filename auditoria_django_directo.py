#!/usr/bin/env python
"""Auditoría: Llamar directamente la función Django sin ir por HTTP"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from reportes.services import dashboard_general
from datetime import datetime, timedelta
from django.utils import timezone

print('═' * 70)
print('🔍 AUDITORÍA DIRECTA: dashboard_general() sin pasar por HTTP')
print('═' * 70)
print()

# Llamar función directly
result = dashboard_general()

# Verificar satisfaccion_score
satisfaccion = result.get('satisfaccion_score')
print(f'satisfaccion_score VALUE: {repr(satisfaccion)}')
print(f'satisfaccion_score TYPE: {type(satisfaccion).__name__}')
print(f'¿Es string "N/A"? {satisfaccion == "N/A"}')
print(f'¿Es número 0.0? {satisfaccion == 0.0}')
print(f'¿Es número 0? {satisfaccion == 0}')
print()

# Mostrar cómo se vería en JSON
import json
print('📄 Cómo se serializa a JSON:')
json_str = json.dumps({'satisfaccion_score': satisfaccion})
print(f'JSON: {json_str}')
print()

# Reverificar que el código tiene "N/A"
print('═' * 70)
print('✅ Si ves "N/A" arriba, el backend está correcto.')
print('❌ Si ves 0 o 0.0, significa que el archivo reportes/services.py tiene cache.')
print('═' * 70)
