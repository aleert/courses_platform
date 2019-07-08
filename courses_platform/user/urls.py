from django.urls import path

from . import views


app_name = 'user'

urlpatterns = [
    path('verify-registration/', views.verify_registration,
         name='verify_registration'),
]
