# Django
from django.urls import path
# admin
from apps.admin.views import (Main, Request, Shop, SetPlace, UpdateRequest, UpdateShop, DownloadDateDoc, 
                              ListRequests, UnlockRequest, set_place_temp, unset_place_temp, set_place)
app_name = 'admin'

urlpatterns = [
    path('main', Main.as_view(), name='main'),
    path('solicitudes', ListRequests.as_view(), name='list_requests'),
    path('solicitud/<uuid:uuid>', Request.as_view(), name='request'),
    path('solicitud/<uuid:uuid>/editar', UpdateRequest.as_view(), name='update_request'),
    path('comercio/<uuid:uuid>/editar', UpdateShop.as_view(), name='update_shop'),
    path('comercio/<uuid:uuid>', Shop.as_view(), name='shop'),
    path('solicitud/<uuid:uuid>/lugares', SetPlace.as_view(), name='set_place'),
    path('solicitud/<uuid:uuid>/cita/<uuid:uuid_date>/descargar', DownloadDateDoc.as_view(), name='download_date'),
    path('solicitud/<uuid:uuid>/validacion/desbloquear', UnlockRequest.as_view(), name='unlock_validation'),
    path('solicitud/<uuid:uuid>/lugar/temp', set_place_temp),
    path('solicitud/<uuid:uuid>/lugar/unset/temp', unset_place_temp),
    path('solicitud/<uuid:uuid>/lugar/set', set_place)
]