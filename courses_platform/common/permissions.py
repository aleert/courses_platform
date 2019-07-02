from rest_framework.permissions import BasePermission, SAFE_METHODS

from courses.models import Module, Item, ContentBase


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


class IsStudentOrOwnerOrSuperuser(BasePermission):

    def has_permission(self, request, view):
        obj = view.get_object()
        return bool(
            (
                request.user
                and (request.user.is_staff or getattr(obj, 'owner', None) == request.user)
            )
            or obj.students.filter(pk=request.user.pk).exists()
        )


class IsStudentReadOnlyOrAdminOrSU(IsOwnerOrSuperuser):
    """Permission to use read_only methods for students and write acess to owners and superusers."""

    def has_permission(self, request, view):
        obj = view.get_object()
        student_exists = False
        if issubclass(obj.__class__, ContentBase):
            student_exists = obj.item.module.course.students.filter(pk=request.user.pk).exists()
        elif isinstance(obj, Module):
            student_exists = obj.course.students.filter(pk=request.user.pk).exists()
        elif isinstance(obj, Item):
            student_exists = obj.module.course.students.filter(pk=request.user.pk).exists()

        if request.method in SAFE_METHODS:
            return student_exists
        else:
            return super().has_permission(request, view)


        return False
