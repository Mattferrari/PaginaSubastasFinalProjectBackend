from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrAdmin(BasePermission):
    """
    Permite editar/eliminar una subasta solo si el usuario es el propietario o el administrador. Cualquiera puede consultar (GET)
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user or request.user.is_staff
    

class IsAuthorOrAdmin(BasePermission):
    """
    Permite editar/eliminar un comentario solo si el usuario es el autor o el administrador. Cualquiera puede consultar (GET)
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.autor == request.user or request.user.is_staff