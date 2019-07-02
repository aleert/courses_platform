from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404,
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from common.permissions import (
    IsOwnerOrSuperuserOrReadOnly, IsAdminUserOrReadOnly, IsOwnerOrSuperuser,
    IsStudentOrTeacherReadOnlyOrAdminOrSU
)
from . import models
from . import serializers


class CourseDetailView(RetrieveUpdateDestroyAPIView):
    """View and update course."""

    permission_classes = [IsOwnerOrSuperuserOrReadOnly]
    serializer_class = serializers.CourseSerializer
    queryset = models.Course.objects.all()

    def filter_queryset(self, queryset):
        user = self.request.user
        if user.is_staff:
            qs = queryset
        elif user.is_authenticated:
            qs = queryset.filter(Q(visible=True) | Q(owner=user.pk)).all()
        else:
            qs = queryset.filter(visible=True).all()
        return qs


class CourseListView(ListCreateAPIView):
    """View all courses and create new ones if authenticated user."""

    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = serializers.CourseWithoutModulesSerializer
    queryset = models.Course.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner_id=self.request.user.pk)

    def filter_queryset(self, queryset):
        user = self.request.user
        if user.is_staff:
            qs = queryset
        elif user.is_authenticated:
            qs = queryset.filter(Q(visible=True) | Q(owner=user.pk)).all()
        else:
            qs = queryset.filter(visible=True).all()
        return qs


class UserCourseListView(CourseListView):
    """Courses that belong to specific user."""

    def filter_queryset(self, queryset):
        User = get_user_model()
        try:
            user_pk = self.kwargs.get('pk')
            user = get_object_or_404(User, pk=user_pk)
        except User.DoesNotExist:
            raise NotFound(detail='No such user')
        qs = queryset.filter(owner=user)
        return qs


class CourseModulesView(ListCreateAPIView):
    """View all modules in course and create new ones."""

    permission_classes = [IsOwnerOrSuperuser]
    serializer_class = serializers.ModuleWithoutItemsSerializer

    def get_queryset(self):
        course = models.Course.objects.get(pk=self.kwargs['pk'])
        return course.modules.all()

    def perform_create(self, serializer):
        serializer.save(course_id=self.kwargs.get('pk'))


class ModuleDetailView(RetrieveUpdateDestroyAPIView):
    """View and update module."""

    # Doesn't have put support as it's ambigous what to do with module items
    # and hard to do multiple nested objects creation (items and contents within items)
    http_method_names = ['get', 'patch', 'delete', 'head', 'options', 'trace']
    permission_classes = [IsStudentOrTeacherReadOnlyOrAdminOrSU]
    serializer_class = serializers.ModuleSerializer
    queryset = models.Module.objects.all()


class ModuleItemsView(ListCreateAPIView):
    """View all items in module and create a new ones."""

    permission_classes = [IsOwnerOrSuperuser]
    serializer_class = serializers.ItemSerializer

    def get_queryset(self):
        qs = models.Module.objects.get(pk=self.kwargs['pk']).all_items()
        return qs

    def list(self, request, *args, **kwargs):
        qs = models.Module.objects.get(pk=self.kwargs['pk']).all_items()

        ctx = self.get_serializer_context()
        serializer = serializers.ItemSerializer(qs, many=True, context=ctx)
        return Response(serializer.data)

    def get_object(self):
        # This is an object to run permission checks from permission_classes against
        # So we display items but run checks on module those items belong to
        return get_object_or_404(models.Module, pk=self.kwargs['pk'])

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        # this is used in item serializer to set item module properly
        ctx['module_id'] = self.kwargs['pk']
        return ctx


class ItemDetailView(RetrieveUpdateDestroyAPIView):
    """View single item and update it if owner."""

    permission_classes = [IsOwnerOrSuperuser]
    serializer_class = serializers.ItemSerializer
    queryset = models.Item.objects.all()

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['item_pk'] = self.kwargs.get('pk')
        return ctx


class SubjectDetailView(RetrieveUpdateDestroyAPIView):
    """View subject and create new one if superuser."""

    permission_classes = [IsAdminUserOrReadOnly]
    serializer_class = serializers.SubjectSerializer
    queryset = models.Subject.objects.all()


class SubjectListView(ListCreateAPIView):
    """View sibject and create new one if superuser."""

    permission_classes = [IsAdminUserOrReadOnly]
    serializer_class = serializers.SubjectWithoutCoursesSerializer
    queryset = models.Subject.objects.all()


class ContentDetailView(RetrieveUpdateDestroyAPIView):
    # TODO when content deleted return response is 404 which is probably due to get_object()
    permission_classes = [IsStudentOrTeacherReadOnlyOrAdminOrSU]
    serializer_class = serializers.ContentSerializer
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        content_type = self.kwargs.get('content_type')
        serializer = serializers.get_content_serializer_class(content_type)
        klass = serializer.Meta.model
        return klass.objects.all()


@api_view(http_method_names=['POST'])
@permission_classes([IsOwnerOrSuperuser])
def add_teacher(request, pk):
    User = get_user_model()
    user = get_object_or_404(User, pk=request.data['user_pk'])
    course = get_object_or_404(models.Course, pk=pk)
    course.teachers.add(user)
    return Response(status=HTTP_200_OK, data={'detail': 'Teacher added successfully'})


@api_view(http_method_names=['POST'])
@permission_classes([IsAuthenticated])
def enroll(request, pk):
    course = get_object_or_404(models.Course, pk=pk)
    if course.is_enroll_open:
        course.students.add(request.user)
        return JsonResponse(status=status.HTTP_200_OK, data={'detail': f'Successfully registered to {course.title}'})
    return JsonResponse(
        status=status.HTTP_400_BAD_REQUEST,
        data={'error': f'Course {course.title} not open for enroll.'}
    )
