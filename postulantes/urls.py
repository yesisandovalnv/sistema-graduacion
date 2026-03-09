from rest_framework.routers import DefaultRouter

from .views import ComentarioInternoViewSet, EtapaViewSet, NotificacionViewSet, PostulacionViewSet, PostulanteViewSet

router = DefaultRouter()
router.register(r'postulantes', PostulanteViewSet, basename='postulante')
router.register(r'postulaciones', PostulacionViewSet, basename='postulacion')
router.register(r'etapas', EtapaViewSet, basename='etapa')
router.register(r'notificaciones', NotificacionViewSet, basename='notificacion')
router.register(r'comentarios-internos', ComentarioInternoViewSet, basename='comentario-interno')

urlpatterns = router.urls