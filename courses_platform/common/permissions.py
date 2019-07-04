from courses.models import ContentBase, Item, Module
from rest_framework.permissions import SAFE_METHODS, BasePermission


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


class IsStudentOrTeacherReadOnlyOrAdminOrSU(IsOwnerOrSuperuser):
    """Permission to use read_only methods for students and write access to owners and superusers."""

    def has_permission(self, request, view):
        obj = view.get_object()
        is_student = False
        is_teacher = False
        if issubclass(obj.__class__, ContentBase):
            is_student = obj.item.module.course.students.filter(pk=request.user.pk).exists()
            is_teacher = obj.item.module.course.teachers.filter(pk=request.user.pk).exists()
        elif isinstance(obj, Module):
            is_student = obj.course.students.filter(pk=request.user.pk).exists()
            is_teacher = obj.course.teachers.filter(pk=request.user.pk).exists()
        elif isinstance(obj, Item):
            is_student = obj.module.course.students.filter(pk=request.user.pk).exists()
            is_teacher = obj.module.course.teachers.filter(pk=request.user.pk).exists()

        if request.method in SAFE_METHODS:
            return is_student or is_teacher or request.user.is_staff
        else:
            return super().has_permission(request, view)
