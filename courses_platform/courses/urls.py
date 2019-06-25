from django.urls import path, re_path, include

from . import views

app_name = 'courses'

urlpatterns = [
    path('modules/<int:module_pk>/items/', views.ModuleItemsView.as_view(), name='module_items'),
    path('modules/<int:pk>/', views.ModuleView.as_view(), name='module_detail'),
    path('items/<int:pk>/', views.ItemDetailView.as_view(), name='item_detail'),
]
