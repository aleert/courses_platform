from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrSuperuserOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        obj = view.get_object()
        return bool(
            request.method in SAFE_METHODS
            or request.user
            and (request.user.is_staff or getattr(obj, 'owner', None) == request.user)
        )


class IsAdminUserOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        return bool(request.method in SAFE_METHODS or request.user and request.user.is_staff)


class IsOwnerOrSuperuser(BasePermission):

    def has_permission(self, request, view):
        obj = view.get_object()
        return bool(
            request.user
            and (request.user.is_staff or getattr(obj, 'owner', None) == request.user)
        )
