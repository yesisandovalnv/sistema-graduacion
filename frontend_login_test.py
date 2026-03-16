"""
Quick tests to verify login is working
Run with: pytest frontend_login_test.py -v
Or manually execute the steps
"""

import requests
import json
import time

BASE_URL = 'http://localhost:8000'
API_BASE = f'{BASE_URL}/api'

def test_backend_is_running():
    """Verify backend is running"""
    print('\n🔍 Test 1: Backend Running')
    try:
        response = requests.get(f'{BASE_URL}/api/docs/', timeout=5)
        assert response.status_code in [200, 404], 'Backend not responding'
        print('   ✅ Backend is running on http://localhost:8000')
        return True
    except requests.exceptions.ConnectionError:
        print('   ❌ Backend not running. Start with: python manage.py runserver')
        return False

def test_login_endpoint_exists():
    """Verify login endpoint exists"""
    print('\n🔍 Test 2: Login Endpoint')
    try:
        response = requests.post(
            f'{API_BASE}/auth/login/',
            json={'username': 'nonexistent', 'password': 'wrong'},
            timeout=5
        )
        # 401 is expected for wrong credentials
        assert response.status_code == 401, f'Unexpected status: {response.status_code}'
        print('   ✅ Login endpoint is responding')
        print(f'   Response: {response.json()}')
        return True
    except requests.exceptions.ConnectionError:
        print('   ❌ Cannot connect to /api/auth/login/')
        return False
    except Exception as e:
        print(f'   ❌ Error: {str(e)}')
        return False

def test_cors_headers():
    """Verify CORS headers"""
    print('\n🔍 Test 3: CORS Headers')
    try:
        response = requests.post(
            f'{API_BASE}/auth/login/',
            json={'username': 'test', 'password': 'test'},
            timeout=5,
            headers={'Origin': 'http://localhost:5173'}
        )
        
        cors_header = response.headers.get('Access-Control-Allow-Origin')
        if cors_header:
            print(f'   ✅ CORS Header present: {cors_header}')
            return True
        else:
            print('   ⚠️  CORS Header NOT present')
            print('   Consider adding X-Frame-Options to Django settings')
            return False
    except Exception as e:
        print(f'   ❌ Error: {str(e)}')
        return False

def test_login_with_correct_credentials():
    """Try login with admin credentials"""
    print('\n🔍 Test 4: Login with admin credentials')
    try:
        response = requests.post(
            f'{API_BASE}/auth/login/',
            json={'username': 'admin', 'password': 'password'},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            assert 'access' in data, 'No access token in response'
            assert 'refresh' in data, 'No refresh token in response'
            assert 'user' in data, 'No user info in response'
            
            user = data['user']
            print(f'   ✅ Login successful!')
            print(f'   User: {user["username"]} ({user["email"]})')
            print(f'   Role: {user["role_display"]}')
            print(f'   Access Token (first 50 chars): {data["access"][:50]}...')
            return True
        elif response.status_code == 401:
            print(f'   ❌ Login failed: Wrong credentials')
            print(f'   Response: {response.json()}')
            print(f'   Solution: Run: python setup_test_users.py')
            return False
        else:
            print(f'   ❌ Unexpected status: {response.status_code}')
            print(f'   Response: {response.text}')
            return False
    except requests.exceptions.ConnectionError:
        print('   ❌ Cannot connect to backend')
        return False
    except Exception as e:
        print(f'   ❌ Error: {str(e)}')
        return False

def test_token_refresh():
    """Test token refresh endpoint"""
    print('\n🔍 Test 5: Token Refresh')
    
    # First, get a token
    try:
        login_response = requests.post(
            f'{API_BASE}/auth/login/',
            json={'username': 'admin', 'password': 'password'},
            timeout=5
        )
        
        if login_response.status_code != 200:
            print('   ⏭️  Skipping (login failed)')
            return False
        
        refresh_token = login_response.json()['refresh']
        
        # Now try to refresh
        refresh_response = requests.post(
            f'{API_BASE}/auth/refresh/',
            json={'refresh': refresh_token},
            timeout=5
        )
        
        if refresh_response.status_code == 200:
            data = refresh_response.json()
            assert 'access' in data, 'No access token in refresh response'
            print(f'   ✅ Token refresh successful!')
            print(f'   New Access Token (first 50 chars): {data["access"][:50]}...')
            return True
        else:
            print(f'   ❌ Token refresh failed: {refresh_response.status_code}')
            print(f'   Response: {refresh_response.text}')
            return False
    except Exception as e:
        print(f'   ❌ Error: {str(e)}')
        return False

def test_protected_endpoint():
    """Test accessing a protected endpoint"""
    print('\n🔍 Test 6: Protected Endpoint')
    
    try:
        # Get token first
        login_response = requests.post(
            f'{API_BASE}/auth/login/',
            json={'username': 'admin', 'password': 'password'},
            timeout=5
        )
        
        if login_response.status_code != 200:
            print('   ⏭️  Skipping (login failed)')
            return False
        
        access_token = login_response.json()['access']
        
        # Try to access a protected endpoint
        headers = {'Authorization': f'Bearer {access_token}'}
        protected_response = requests.get(
            f'{API_BASE}/postulantes/',
            headers=headers,
            timeout=5
        )
        
        if protected_response.status_code == 200:
            data = protected_response.json()
            print(f'   ✅ Protected endpoint accessible!')
            print(f'   Response: {data}')
            return True
        else:
            print(f'   ❌ Protected endpoint returned: {protected_response.status_code}')
            return False
    except Exception as e:
        print(f'   ❌ Error: {str(e)}')
        return False

def run_all_tests():
    """Run all tests"""
    print('╔════════════════════════════════════════════════╗')
    print('║   Login Functionality Test Suite               ║')
    print('╚════════════════════════════════════════════════╝')
    
    tests = [
        test_backend_is_running,
        test_login_endpoint_exists,
        test_cors_headers,
        test_login_with_correct_credentials,
        test_token_refresh,
        test_protected_endpoint,
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f'   ❌ Test failed with error: {str(e)}')
            results.append(False)
    
    # Summary
    print('\n' + '=' * 50)
    print('📊 SUMMARY')
    print('=' * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f'Passed: {passed}/{total}')
    
    if passed == total:
        print('\n✅ All tests passed! Login is working correctly.')
        print('\n🚀 Next steps:')
        print('   1. Open http://localhost:5173/')
        print('   2. Login with admin/password')
        print('   3. Verify you are redirected to /dashboard')
    else:
        print(f'\n⚠️  {total - passed} test(s) failed.')
        print('   Review the errors above and fix them.')
    
    return passed == total

if __name__ == '__main__':
    print('⏱️  Testing login functionality...\n')
    
    success = run_all_tests()
    
    print('\n' + '=' * 50)
    print('For manual testing, see: QUICK_START_LOGIN.md')
    print('For debugging help, see: LOGIN_DEBUGGING.md')
    print('=' * 50 + '\n')

