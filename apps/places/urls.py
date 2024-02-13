# Django
from django.urls import path
# places
from apps.places.views import Main, CreateRequest, Request, CreateShop, Dates

app_name = 'places'

urlpatterns = [
    path('main', Main.as_view(), name='main'),
    path('solicitud/crear', CreateRequest.as_view(), name='create_request'),
    path('solicitud/<uuid:uuid>', Request.as_view(), name='detail_request'),
    path('solicitud/<uuid:uuid>/comercio/crear', CreateShop.as_view(), name='create_shop'),
    # path('solicitud/<uuid:uuid>/cita/crear', Dates.as_view(), name='create_date'),
]