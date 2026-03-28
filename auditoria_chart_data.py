#!/usr/bin/env python
"""Auditoría: Ver exactamente qué retorna el backend para charts"""
import urllib.request
import json

print("🔍 AUDITORÍA: Ver datos reales del backend")
print("=" * 70)
print()

# Login
try:
    data = json.dumps({"username": "admin", "password": "password"}).encode()
    req = urllib.request.Request(
        'http://localhost/api/auth/login/',
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    response = urllib.request.urlopen(req, timeout=5)
    login_result = json.loads(response.read())
    token = login_result['access']
    print("✅ Login exitoso")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

print()

# Chart data
print("📊 GET /api/reportes/dashboard-chart-data/?meses=6")
try:
    req = urllib.request.Request(
        'http://localhost/api/reportes/dashboard-chart-data/?meses=6',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        },
        method='GET'
    )
    response = urllib.request.urlopen(req, timeout=5)
    chart_data = json.loads(response.read())
    
    print("\n📈 BAR CHART DATA:")
    print(json.dumps(chart_data.get('barChartData', [])[:3], indent=2))
    
    print("\n📉 LINE CHART DATA:")
    print(json.dumps(chart_data.get('lineChartData', [])[:3], indent=2))
    
    print("\n🥧 PIE CHART DATA:")
    print(json.dumps(chart_data.get('pieChartData', []), indent=2))
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
