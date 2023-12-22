# Django
from django.urls import path
# admin
from apps.admin.views import Main
app_name = 'admin'

urlpatterns = [
    path('main', Main.as_view(), name='main')
]