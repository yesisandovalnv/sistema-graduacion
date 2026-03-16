#!/usr/bin/env python
import os
import sys
import django
import traceback
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Now test the view
try:
    print("=" * 80)
    print("TESTING: DashboardGeneralView.get()")
    print("=" * 80)
    
    from django.test import RequestFactory
    from django.contrib.auth import get_user_model
    from rest_framework_simplejwt.tokens import RefreshToken
    from reportes.views import DashboardGeneralView
    
    # Create a test user
    User = get_user_model()
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@test.com', 'is_active': True}
    )
    
    # Create JWT token
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    # Create request
    factory = RequestFactory()
    request = factory.get('/api/reportes/dashboard-general/')
    request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
    request.user = user
    
    # Call the view
    view = DashboardGeneralView.as_view()
    response = view(request)
    
    print("✅ VIEW RESPONSE:")
    print(f"Status code: {response.status_code}")
    print(f"Data type: {type(response.data)}")
    
    if hasattr(response, 'data'):
        print(f"Response data keys: {response.data.keys() if isinstance(response.data, dict) else 'N/A'}")
    
    # Try to serialize
    if response.status_code == 200:
        print("\n✅ SERIALIZATION TEST:")
        json_str = json.dumps(response.data)
        print(f"✅ JSON serialization successful - {len(json_str)} bytes")
    else:
        print(f"\n❌ ERROR: Status {response.status_code}")
        print(f"Response: {response.data}")
    
except Exception as e:
    print("❌ ERROR FOUND:")
    print("=" * 80)
    print(traceback.format_exc())
    print("=" * 80)
    sys.exit(1)
