# Django
from django.urls import path
# users
from apps.users.views import LoginUser, LogoutUser, CreateUser

app_name = 'users'

urlpatterns = [
    path('', LoginUser.as_view(), name='login'),
    path('logout', LogoutUser.as_view(), name='logout'),
    path('registro', CreateUser.as_view(), name='create_user')
]