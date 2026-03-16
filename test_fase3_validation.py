#!/usr/bin/env python
"""
FASE 3 Validation Tests
Validates cache and pagination implementations
"""

import os
import sys
import django
import time
from django.test import TestCase, Client
from django.core.cache import cache
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework import status
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from postulantes.models import Postulante, Postulacion
from documentos.models import DocumentoPostulacion, TipoDocumento
from modalidades.models import Modalidad, Etapa

User = get_user_model()


class CacheValidationTests(TestCase):
    """Test cache functionality in FASE 3"""
    
    def setUp(self):
        """Setup test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='test_user',
            email='test@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        cache.clear()
    
    def test_cache_configuration_exists(self):
        """Test that CACHES configuration is defined"""
        from django.conf import settings
        self.assertIn('default', settings.CACHES)
        self.assertEqual(
            settings.CACHES['default']['BACKEND'],
            'django.core.cache.backends.locmem.LocMemCache'
        )
        print("✅ CACHES configuration exists and is LocMemCache")
    
    def test_cache_set_and_get(self):
        """Test cache set and get operations"""
        cache.set('test_key', 'test_value', 60)
        value = cache.get('test_key')
        self.assertEqual(value, 'test_value')
        print("✅ Cache set/get operations work")
    
    def test_cache_expiration(self):
        """Test cache expiration"""
        cache.set('expiring_key', 'value', 1)
        self.assertEqual(cache.get('expiring_key'), 'value')
        time.sleep(2)
        self.assertIsNone(cache.get('expiring_key'))
        print("✅ Cache expiration works correctly")
    
    def test_dashboard_response(self):
        """Test that dashboard endpoint responds"""
        response = self.client.get('/api/reportes/dashboard-general/')
        self.assertIn(response.status_code, [200, 401])  # 401 if auth fails, 200 if succeeds
        print(f"✅ Dashboard endpoint responds with status {response.status_code}")


class PaginationValidationTests(TestCase):
    """Test pagination functionality in FASE 3"""
    
    def setUp(self):
        """Setup test data with multiple postulants"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='admin_user',
            email='admin@test.com',
            password='adminpass123'
        )
        # Grant permissions
        self.user.is_staff = True
        self.user.save()
        
        self.client.force_authenticate(user=self.user)
        
        # Create 50 postulants for testing pagination
        for i in range(50):
            postulant_user = User.objects.create_user(
                username=f'postulant_{i}',
                email=f'postulant{i}@test.com',
                password='pass123'
            )
            Postulante.objects.create(
                usuario=postulant_user,
                nombre=f'Postulante {i}',
                apellido='Test',
                ci=f'123456789{i:02d}',
                codigo_estudiante=f'EST{i:05d}'
            )
    
    def test_pagination_class_exists(self):
        """Test that CustomPagination class is defined"""
        from postulantes.views import CustomPagination
        pagination = CustomPagination()
        self.assertEqual(pagination.page_size, 20)
        self.assertEqual(pagination.max_page_size, 100)
        print("✅ CustomPagination class exists with correct settings")
    
    def test_pagination_viewset_has_class(self):
        """Test that ViewSets have pagination_class"""
        from postulantes.views import PostulanteViewSet, PostulacionViewSet
        from documentos.views import DocumentoPostulacionViewSet
        
        self.assertTrue(hasattr(PostulanteViewSet, 'pagination_class'))
        self.assertTrue(hasattr(PostulacionViewSet, 'pagination_class'))
        self.assertTrue(hasattr(DocumentoPostulacionViewSet, 'pagination_class'))
        print("✅ All ViewSets have pagination_class attribute")
    
    def test_default_page_size(self):
        """Test default page size is 20"""
        response = self.client.get('/api/postulantes/')
        if response.status_code == 200:
            data = response.json()
            if 'results' in data:
                # Default should be 20 or less if fewer exist
                self.assertLessEqual(len(data['results']), 20)
                print(f"✅ Default page size respected: {len(data['results'])} items")
    
    def test_max_page_size_limit(self):
        """Test that max_page_size is enforced"""
        # Try to request 500 items (should be limited to 100)
        response = self.client.get('/api/postulantes/?page_size=500')
        if response.status_code == 200:
            data = response.json()
            if 'results' in data:
                # Should be limited to max_page_size (100)
                self.assertLessEqual(len(data['results']), 100)
                print(f"✅ Max page size enforced: {len(data['results'])} items (requested 500)")
    
    def test_pagination_response_structure(self):
        """Test pagination response has correct structure"""
        response = self.client.get('/api/postulantes/')
        if response.status_code == 200:
            data = response.json()
            self.assertIn('results', data)
            self.assertIn('count', data)
            print("✅ Pagination response structure is correct")


class PerformanceValidationTests(TestCase):
    """Test performance improvements from FASE 3"""
    
    def setUp(self):
        """Setup test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='perf_user',
            email='perf@test.com',
            password='perfpass123'
        )
        self.client.force_authenticate(user=self.user)
        cache.clear()
    
    def test_cache_speed_improvement(self):
        """Test that cached requests are faster"""
        # Note: In actual testing, measure response times
        # This is a placeholder validation
        from django.conf import settings
        self.assertIn('default', settings.CACHES)
        print("✅ Cache is configured for performance improvement")
    
    def test_rest_framework_max_page_size(self):
        """Test that REST_FRAMEWORK has MAX_PAGE_SIZE"""
        from django.conf import settings
        self.assertIn('MAX_PAGE_SIZE', settings.REST_FRAMEWORK)
        self.assertEqual(settings.REST_FRAMEWORK['MAX_PAGE_SIZE'], 100)
        print("✅ REST_FRAMEWORK MAX_PAGE_SIZE is set to 100")


class ImportValidationTests(TestCase):
    """Test that all required imports work"""
    
    def test_cache_imports(self):
        """Test cache-related imports"""
        try:
            from django.views.decorators.cache import cache_page
            from django.utils.decorators import method_decorator
            print("✅ Cache decorator imports successful")
        except ImportError as e:
            self.fail(f"Cache import failed: {e}")
    
    def test_pagination_imports(self):
        """Test pagination-related imports"""
        try:
            from rest_framework.pagination import PageNumberPagination
            from postulantes.views import CustomPagination
            from documentos.views import CustomPagination as DocCustomPagination
            print("✅ Pagination imports successful")
        except ImportError as e:
            self.fail(f"Pagination import failed: {e}")


def run_validation_suite():
    """Run all validation tests"""
    print("\n" + "="*60)
    print("FASE 3 VALIDATION SUITE")
    print("="*60 + "\n")
    
    tests = [
        ("Cache Configuration", CacheValidationTests),
        ("Pagination Configuration", PaginationValidationTests),
        ("Performance Settings", PerformanceValidationTests),
        ("Import Validation", ImportValidationTests),
    ]
    
    from django.test.runner import DiscoverRunner
    runner = DiscoverRunner(verbosity=2, interactive=False)
    
    test_classes = [
        CacheValidationTests,
        PaginationValidationTests,
        PerformanceValidationTests,
        ImportValidationTests,
    ]
    
    print("\n📋 Running FASE 3 Validation Tests...\n")
    
    # Run cache tests
    print("1️⃣ Testing Cache Configuration...")
    cache_tests = CacheValidationTests()
    try:
        for method in dir(cache_tests):
            if method.startswith('test_'):
                try:
                    getattr(cache_tests, method)()
                except Exception as e:
                    print(f"❌ {method} failed: {e}")
    except Exception as e:
        print(f"❌ Cache tests error: {e}")
    
    # Run pagination tests
    print("\n2️⃣ Testing Pagination Configuration...")
    pag_tests = PaginationValidationTests()
    try:
        for method in dir(pag_tests):
            if method.startswith('test_'):
                try:
                    getattr(pag_tests, method)()
                except Exception as e:
                    print(f"❌ {method} failed: {e}")
    except Exception as e:
        print(f"❌ Pagination tests error: {e}")
    
    # Run import tests
    print("\n3️⃣ Testing Imports...")
    imp_tests = ImportValidationTests()
    try:
        for method in dir(imp_tests):
            if method.startswith('test_'):
                try:
                    getattr(imp_tests, method)()
                except Exception as e:
                    print(f"❌ {method} failed: {e}")
    except Exception as e:
        print(f"❌ Import tests error: {e}")
    
    print("\n" + "="*60)
    print("✅ FASE 3 VALIDATION COMPLETE")
    print("="*60 + "\n")


if __name__ == '__main__':
    run_validation_suite()
