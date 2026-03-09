from rest_framework.permissions import BasePermission


def _is_authenticated(user) -> bool:
    return bool(user and user.is_authenticated)


def _has_any_perm(user, perm_codenames: list[str]) -> bool:
    return _is_authenticated(user) and any(user.has_perm(codename) for codename in perm_codenames)


def can_view_all_postulantes(user) -> bool:
    return _has_any_perm(
        user,
        [
            'postulantes.view_postulante',
            'postulantes.change_postulante',
            'postulantes.delete_postulante',
        ],
    )


def can_view_all_postulaciones(user) -> bool:
    return _has_any_perm(
        user,
        [
            'postulantes.view_postulacion',
            'postulantes.change_postulacion',
            'postulantes.delete_postulacion',
        ],
    )


def can_view_all_documentos(user) -> bool:
    return _has_any_perm(
        user,
        [
            'documentos.view_documentopostulacion',
            'documentos.change_documentopostulacion',
            'documentos.delete_documentopostulacion',
        ],
    )


class CRUDModelPermission(BasePermission):
    """Dynamic model permission by HTTP method (view/add/change/delete)."""

    def has_permission(self, request, view):
        user = request.user
        if not _is_authenticated(user):
            return False

        if request.method in {'POST', 'PUT', 'PATCH', 'DELETE'}:
            model = getattr(getattr(view, 'queryset', None), 'model', None)
            if not model:
                return False
            app_label = model._meta.app_label
            model_name = model._meta.model_name
            action_by_method = {
                'POST': 'add',
                'PUT': 'change',
                'PATCH': 'change',
                'DELETE': 'delete',
            }
            action = action_by_method[request.method]
            return user.has_perm(f'{app_label}.{action}_{model_name}')

        model = getattr(getattr(view, 'queryset', None), 'model', None)
        if not model:
            return False
        return user.has_perm(f'{model._meta.app_label}.view_{model._meta.model_name}')


class DocumentoRolePermission(BasePermission):
    """Authorization by Django permissions + ownership."""

    def has_permission(self, request, view):
        return _is_authenticated(request.user)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if can_view_all_documentos(user):
            return True
        return obj.postulacion.postulante.usuario_id == user.id


class PostulanteRolePermission(BasePermission):
    """Authorization by Django permissions + ownership."""

    def has_permission(self, request, view):
        return _is_authenticated(request.user)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if can_view_all_postulantes(user):
            return True
        return obj.usuario_id == user.id


class PostulacionRolePermission(BasePermission):
    """Authorization by Django permissions + ownership."""

    def has_permission(self, request, view):
        return _is_authenticated(request.user)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if can_view_all_postulaciones(user):
            return True
        return obj.postulante.usuario_id == user.id


class PuedeAprobarDocumentosPermission(BasePermission):
    message = 'No tienes permiso para aprobar documentos.'

    def has_permission(self, request, view):
        user = request.user
        return _is_authenticated(user) and user.has_perm('documentos.puede_aprobar_documentos')


class PuedeAvanzarEtapaPermission(BasePermission):
    message = 'No tienes permiso para avanzar etapas.'

    def has_permission(self, request, view):
        user = request.user
        return _is_authenticated(user) and user.has_perm('postulantes.puede_avanzar_etapa')


class PuedeVerAuditoriaPermission(BasePermission):
    message = 'No tienes permiso para ver auditoria.'

    def has_permission(self, request, view):
        user = request.user
        return _is_authenticated(user) and user.has_perm('auditoria.puede_ver_auditoria')


class PuedeVerDashboardInstitucionalPermission(BasePermission):
    message = 'No tienes permiso para ver el dashboard institucional.'

    def has_permission(self, request, view):
        user = request.user
        return _is_authenticated(user) and user.has_perm('reportes.view_reportegenerado')
