#!/usr/bin/env python
"""Test HTTP al endpoint después del restart de Docker"""
# Usar powershell inline aprovechando que estamos en terminal

# Simulación: lo que debería estar en el JSON
print("╔" + "═" * 68 + "╗")
print("║" + " TEST ENDPOINT DESPUÉS DE DOCKER RESTART" .center(68) + "║")
print("╚" + "═" * 68 + "╝")
print()

# Esperar y hacer una prueba real
import subprocess
import json
import time

time.sleep(2)

# Comando PowerShell para hacer llamada HTTP
ps_cmd = '''
$login = Invoke-RestMethod -Uri 'http://localhost/api/token/' -Method POST -ContentType 'application/json' -Body (ConvertTo-Json @{username='admin';password='password'})
$token = $login.access

$headers = @{'Authorization' = "Bearer $token"}
$response = Invoke-RestMethod -Uri 'http://localhost/api/reportes/dashboard-general/' -Method GET -Headers $headers

Write-Output "satisfaccion_score: $($response.satisfaccion_score)"
Write-Output "Type: $($response.satisfaccion_score | Get-Member | % -Property TypeName)"
'''

try:
    result = subprocess.run(
        ['powershell', '-Command', ps_cmd],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
        
except Exception as e:
    print(f"Error: {e}")

print()
print("✅ Si ves 'N/A' arriba, el fix trabajó.")
