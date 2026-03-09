from typing import Any

from .models import AuditoriaLog


def registrar_auditoria(
    *,
    usuario=None,
    accion: str,
    modelo_afectado: str,
    objeto_id: Any,
    estado_anterior=None,
    estado_nuevo=None,
    detalles=None,
) -> AuditoriaLog:
    user_is_authenticated = getattr(usuario, 'is_authenticated', False)
    detalles_payload = dict(detalles or {})
    if user_is_authenticated:
        detalles_payload.setdefault('actor_role', getattr(usuario, 'role', None))

    return AuditoriaLog.objects.create(
        usuario=usuario if user_is_authenticated else None,
        accion=accion,
        modelo_afectado=modelo_afectado,
        objeto_id=str(objeto_id),
        estado_anterior=estado_anterior,
        estado_nuevo=estado_nuevo,
        detalles=detalles_payload or None,
    )

