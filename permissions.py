from rest_framework import permissions


class IsAdminRole(permissions.BasePermission):
    """
    Permiso personalizado para permitir el acceso solo a usuarios con el rol 'admin'.
    """
    message = "Solo los administradores pueden realizar esta acción."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and getattr(request.user, 'role', None) == 'admin'


class DocumentoRolePermission(permissions.BasePermission):
    # ... (contenido existente de DocumentoRolePermission)
    pass


class CRUDModelPermission(permissions.BasePermission):
    # ... (contenido existente de CRUDModelPermission)
    pass


class PuedeAprobarDocumentosPermission(permissions.BasePermission):
    # ... (contenido existente de PuedeAprobarDocumentosPermission)
    pass


class PuedeAvanzarEtapaPermission(permissions.BasePermission):
    # ... (contenido existente de PuedeAvanzarEtapaPermission)
    pass