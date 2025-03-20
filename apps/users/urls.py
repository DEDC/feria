# Django
from django.urls import path
from django.views.generic import TemplateView
# users
from apps.users.views import LoginUser, LogoutUser, CreateUser, CustomPasswordResetView, CustomPasswordResetConfirmView, CustomPasswordResetDoneView

app_name = 'users'

urlpatterns = [
    path('', LoginUser.as_view(), name='login'),
    path('logout', LogoutUser.as_view(), name='logout'),
    path('registro', CreateUser.as_view(), name='create_user'),
    path('aviso_privacidad', TemplateView.as_view(template_name='usuarios/privacidad.html'), name='aviso_privacidad'),
    # passwordreset
    path('password_reset', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset_confirm/<uidb64>/<token>', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_done', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
]