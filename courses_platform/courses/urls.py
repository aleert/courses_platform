from django.urls import path
from django.views.generic import RedirectView
from rest_framework.reverse import reverse_lazy

from . import views

app_name = 'courses'

urlpatterns = [
    path('', RedirectView.as_view(url=reverse_lazy('courses:course_list'), permanent=True)),
    path('items/<int:pk>/', views.ItemDetailView.as_view(), name='item_detail'),
    path('modules/<int:pk>/', views.ModuleDetailView.as_view(), name='module_detail'),
    path('modules/<int:pk>/items/', views.ModuleItemsView.as_view(), name='module_items'),
    path('subjects/', views.SubjectListView.as_view(), name='subject_list'),
    path('subjects/<slug:pk>/', views.SubjectDetailView.as_view(), name='subject_detail'),
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('courses/<int:pk>/modules/', views.CourseModulesView.as_view(), name='course_modules'),
    path('courses/<int:pk>/add_teacher/', views.add_teacher, name='course_add_teacher'),
    path('users/<int:pk>/courses/', views.UserCourseListView.as_view(), name='user_courses'),
    path('contents/<str:content_type>/<int:pk>/', views.ContentDetailView.as_view(), name='content_detail'),
]
