"""
Health check view for monitoring systems.
Provides simple endpoint to verify Django is running.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def health_check(request):
    """
    Simple health check endpoint that returns 200 if Django is running.
    
    Used by Docker healthcheck and monitoring systems.
    """
    return JsonResponse({
        "status": "healthy",
        "message": "Backend is running"
    }, status=200)
