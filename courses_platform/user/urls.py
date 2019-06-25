from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

from . import views


app_name = 'user'

urlpatterns = [
    path('', RedirectView.as_view(
        url=reverse_lazy('user:edit')
    )
         ),
    path('login/', auth_views.LoginView.as_view(),
         name='login'),
    path('logout/', auth_views.LogoutView.as_view(),
         name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(
        success_url=reverse_lazy('user:password_change_done')
    ),
         name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(),
         name='password_change_done'),
    # password reset
    path('password_reset/', auth_views.PasswordResetView.as_view(
        success_url=reverse_lazy('user:password_reset_done')),
         name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        success_url=reverse_lazy('user:password_reset_complete')),
         name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
    # registration
    path('register/', views.register,
         name='register'),
    # update profile
    path('edit/', views.edit,
         name='edit')
]
