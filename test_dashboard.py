#!/usr/bin/env python
import os
import sys
import django
import traceback

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Now test the endpoint
try:
    print("=" * 60)
    print("TESTING: dashboard_general()")
    print("=" * 60)
    
    from reportes.services import dashboard_general
    result = dashboard_general()
    
    print("✅ SUCCESS - No errors in dashboard_general()")
    print(f"Result keys: {result.keys()}")
    
except Exception as e:
    print("❌ ERROR FOUND:")
    print("=" * 60)
    print(traceback.format_exc())
    print("=" * 60)
    sys.exit(1)
