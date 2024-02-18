# Django
from django.urls import path
# admin
from apps.admin.views import Main, Request, SetPlace, UpdateRequest, set_place_temp, unset_place_temp, set_place
app_name = 'admin'

urlpatterns = [
    path('main', Main.as_view(), name='main'),
    path('solicitud/<uuid:uuid>', Request.as_view(), name='request'),
    path('solicitud/<uuid:uuid>/editar', UpdateRequest.as_view(), name='update_request'),
    path('solicitud/<uuid:uuid>/lugares', SetPlace.as_view(), name='set_place'),
    path('solicitud/<uuid:uuid>/lugar/temp', set_place_temp),
    path('solicitud/<uuid:uuid>/lugar/unset/temp', unset_place_temp),
    path('solicitud/<uuid:uuid>/lugar/set', set_place)
]