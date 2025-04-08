# Django
from django.urls import path
# places
from apps.places.views import Main, CreateRequest, Request, CreateShop, ObservationsRequest, ObservationsShop, DownloadDateDoc, DownloadContractUser, DownloadGafeteUser, DownloadResponsibilityUser

app_name = 'places'

urlpatterns = [
    path('main', Main.as_view(), name='main'),
    path('solicitud/crear', CreateRequest.as_view(), name='create_request'),
    path('solicitud/<uuid:uuid>', Request.as_view(), name='detail_request'),
    path('solicitud/<uuid:uuid>/observaciones', ObservationsRequest.as_view(), name='observations_request'),
    path('comercio/<uuid:uuid>/observaciones', ObservationsShop.as_view(), name='observations_shop'),
    path('solicitud/<uuid:uuid>/comercio/crear', CreateShop.as_view(), name='create_shop'),
    path('solicitud/<uuid:uuid>/cita/<uuid:uuid_date>/descargar', DownloadDateDoc.as_view(), name='download_date'),
    path('solicitud/<uuid:uuid>/contrato/descargar', DownloadContractUser.as_view(), name='download_contract_user'),
    path('solicitud/<uuid:uuid>/carta_responsiva/descargar', DownloadResponsibilityUser.as_view(), name='download_responsibility_user'),
    path('solicitud/<uuid:uuid>/lugar/<uuid:uuid_place>/gafete/descargar', DownloadGafeteUser.as_view(), name='download_gafete_user'),
]