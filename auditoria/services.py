from typing import Any
import logging

from .models import AuditoriaLog

logger = logging.getLogger(__name__)


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

    log = AuditoriaLog.objects.create(
        usuario=usuario if user_is_authenticated else None,
        accion=accion,
        modelo_afectado=modelo_afectado,
        objeto_id=str(objeto_id),
        estado_anterior=estado_anterior,
        estado_nuevo=estado_nuevo,
        detalles=detalles_payload or None,
    )
    logger.info(f"Auditoría registrada: {accion} en {modelo_afectado}#{objeto_id}")
    return log


# FASE 4: Métodos específicos para acciones críticas
def registrar_creacion_postulante(usuario, postulante, detalles=None):
    """Registra creación de un nuevo postulante"""
    return registrar_auditoria(
        usuario=usuario,
        accion='CREAR_POSTULANTE',
        modelo_afectado='Postulante',
        objeto_id=postulante.id,
        estado_anterior=None,
        estado_nuevo={
            'nombre': postulante.nombre,
            'apellido': postulante.apellido,
            'ci': postulante.ci,
            'codigo_estudiante': postulante.codigo_estudiante,
        },
        detalles={
            'usuario_id': postulante.usuario_id,
            **(detalles or {})
        }
    )


def registrar_modificacion_documento(usuario, documento, campos_anteriores, campos_nuevos):
    """Registra modificación de un documento de postulación"""
    return registrar_auditoria(
        usuario=usuario,
        accion='MODIFICAR_DOCUMENTO',
        modelo_afectado='DocumentoPostulacion',
        objeto_id=documento.id,
        estado_anterior=campos_anteriores,
        estado_nuevo=campos_nuevos,
        detalles={
            'postulacion_id': documento.postulacion_id,
            'tipo_documento_id': documento.tipo_documento_id,
            'estado': documento.estado,
        }
    )


def registrar_aprobacion_documento(usuario, documento):
    """Registra aprobación de un documento"""
    return registrar_auditoria(
        usuario=usuario,
        accion='APROBAR_DOCUMENTO',
        modelo_afectado='DocumentoPostulacion',
        objeto_id=documento.id,
        estado_anterior={'estado': 'pendiente'},
        estado_nuevo={'estado': 'aprobado'},
        detalles={
            'postulacion_id': documento.postulacion_id,
            'tipo_documento': documento.tipo_documento.nombre if documento.tipo_documento else None,
            'revisado_por_id': usuario.id,
        }
    )


def registrar_rechazo_documento(usuario, documento, razon=None):
    """Registra rechazo de un documento"""
    return registrar_auditoria(
        usuario=usuario,
        accion='RECHAZAR_DOCUMENTO',
        modelo_afectado='DocumentoPostulacion',
        objeto_id=documento.id,
        estado_anterior={'estado': 'pendiente'},
        estado_nuevo={'estado': 'rechazado'},
        detalles={
            'postulacion_id': documento.postulacion_id,
            'tipo_documento': documento.tipo_documento.nombre if documento.tipo_documento else None,
            'razon': razon,
        }
    )


def registrar_eliminacion(usuario, modelo_nombre, objeto_id, detalles=None):
    """Registra eliminación de un registro (soft delete o eliminación real)"""
    return registrar_auditoria(
        usuario=usuario,
        accion='ELIMINAR',
        modelo_afectado=modelo_nombre,
        objeto_id=objeto_id,
        estado_anterior={'estado': 'activo'},
        estado_nuevo={'estado': 'eliminado'},
        detalles=detalles or {}
    )


def registrar_cambio_estado_postulacion(usuario, postulacion, estado_anterior, estado_nuevo):
    """Registra cambio de estado de una postulación"""
    return registrar_auditoria(
        usuario=usuario,
        accion='CAMBIAR_ESTADO_POSTULACION',
        modelo_afectado='Postulacion',
        objeto_id=postulacion.id,
        estado_anterior={'estado': estado_anterior},
        estado_nuevo={'estado': estado_nuevo},
        detalles={
            'postulante_id': postulacion.postulante_id,
            'modalidad_id': postulacion.modalidad_id,
        }
    )

