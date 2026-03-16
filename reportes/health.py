# Health Check Service for FASE 4
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class HealthCheckService:
    """Sistema de health check para monitoreo del estado"""
    
    @staticmethod
    def check_database():
        """Verifica conexión a PostgreSQL"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return {
                'status': 'healthy',
                'database': 'PostgreSQL',
                'message': 'Conexión exitosa'
            }
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'database': 'PostgreSQL',
                'message': f'Error: {str(e)}'
            }
    
    @staticmethod
    def check_cache():
        """Verifica conexión a Cache (Redis o LocMemCache)"""
        try:
            # Intenta set y get en caché
            test_key = 'health_check_test'
            test_value = 'ok'
            cache.set(test_key, test_value, 10)
            result = cache.get(test_key)
            
            if result == test_value:
                cache_backend = settings.CACHES['default']['BACKEND'].split('.')[-1]
                return {
                    'status': 'healthy',
                    'cache': cache_backend,
                    'location': settings.CACHES['default'].get('LOCATION', 'Redis'),
                    'message': 'Caché funcional'
                }
            else:
                raise Exception("Cache value mismatch")
        except Exception as e:
            logger.error(f"Cache health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'cache': 'Unknown',
                'message': f'Error: {str(e)}'
            }
    
    @staticmethod
    def check_overall_health():
        """Verificación general de salud del sistema"""
        db_health = HealthCheckService.check_database()
        cache_health = HealthCheckService.check_cache()
        
        # Sistema es healthy si DB está OK (cache es deseable pero no crítico)
        overall_status = 'healthy' if db_health['status'] == 'healthy' else 'unhealthy'
        
        return {
            'status': overall_status,
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'components': {
                'database': db_health,
                'cache': cache_health,
            },
            'version': '1.0',
            'service': 'Sistema de Graduación'
        }
