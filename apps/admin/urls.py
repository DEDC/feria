# Django
from django.urls import path
# admin
from apps.admin.views import (Main, Request, Shop, SetPlace, UpdateRequest, UpdateShop, DownloadDateDoc,
                              ListRequests, ListUsers, UnlockRequest, UpdateUser, UserDates, ListDates,
                              DownloadContract, DownloadGafete, DownloadSuministros, DownloadReport,
                              DownloadRequestsReport, ListParking, DownloadStandsReport,
                              DownloadTarjeton, UpdateParking, DownloadReceipt, ListStands, DownloadResponsibility, QRReader,
                              set_place_temp, unset_place_temp, set_place,
                              add_alcohol, add_terraza, add_big_terraza, add_gafete, delete_item, delete_place, add_descuento,
                              aplicar_pago_caja, aplicar_pago_transfer, apply_cash_payment_gafete, RegistroManualUbicacion, AddTarjetonByLocal)
app_name = 'admin'

urlpatterns = [
    path('lector_qr', QRReader.as_view(), name='qr_reader'),
    path('main', Main.as_view(), name='main'),
    path('solicitudes', ListRequests.as_view(), name='list_requests'),
    path('usuarios', ListUsers.as_view(), name='list_users'),
    path('citas', ListDates.as_view(), name='list_dates'),
    path('tarjetones', ListParking.as_view(), name='list_parking'),
    path('locales', ListStands.as_view(), name='list_stands'),
    path('solicitud/<uuid:uuid>', Request.as_view(), name='request'),
    path('solicitud/<uuid:uuid>/lugar', RegistroManualUbicacion.as_view(), name='ubicacion-manual'),
    path('solicitud/<uuid:uuid>/editar', UpdateRequest.as_view(), name='update_request'),
    path('comercio/<uuid:uuid>/editar', UpdateShop.as_view(), name='update_shop'),
    path('usuario/<int:pk>/editar', UpdateUser.as_view(), name='update_user'),
    path('tarjeton/<int:pk>/editar', UpdateParking.as_view(), name='update_parking'),
    path('usuario/<int:pk>/citas/', UserDates.as_view(), name='assing_user_date'),
    path('comercio/<uuid:uuid>', Shop.as_view(), name='shop'),
    path('solicitud/<uuid:uuid>/espacios', SetPlace.as_view(), name='set_place'),
    path('solicitud/<uuid:uuid>/cita/<uuid:uuid_date>/descargar', DownloadDateDoc.as_view(), name='download_date'),
    path('solicitud/<uuid:uuid>/validacion/desbloquear', UnlockRequest.as_view(), name='unlock_validation'),
    path('solicitud/<uuid:uuid>/tarjeton/agregar', AddTarjetonByLocal.as_view(), name='add_tes'),
    # assign places
    path('solicitud/<uuid:uuid>/<str:zone>/lugar/temp', set_place_temp),
    path('solicitud/<uuid:uuid>/lugar/unset/temp', unset_place_temp),
    path('solicitud/<uuid:uuid>/lugar/set', set_place),
    # products
    path('solicitud/<uuid:uuid>/lugar/<uuid:uuid_place>/pago', aplicar_pago_caja),
    path('solicitud/<uuid:uuid>/lugar/<uuid:uuid_place>/transfer', aplicar_pago_transfer),
    path('solicitud/<uuid:uuid>/lugar/<uuid:uuid_place>/gafete/<uuid_px>/pago', apply_cash_payment_gafete),
    path('solicitud/<uuid:uuid>/lugar/<uuid:uuid_place>/alcohol/agregar', add_alcohol),
    path('solicitud/<uuid:uuid>/lugar/<uuid:uuid_place>/terraza/agregar', add_terraza),
    path('solicitud/<uuid:uuid>/lugar/<uuid:uuid_place>/descuento/agregar', add_descuento),
    path('solicitud/<uuid:uuid>/lugar/<uuid:uuid_place>/terraza_grande/agregar', add_big_terraza),
    path('solicitud/<uuid:uuid>/lugar/<uuid:uuid_place>/gafete/agregar', add_gafete),
    path('solicitud/<uuid:uuid>/item/<uuid:uuid_pdt>/eliminar', delete_item),
    path('solicitud/<uuid:uuid>/lugar/<uuid:uuid_place>/eliminar', delete_place),
    # downloads
    path('solicitud/<uuid:uuid>/contrato/descargar', DownloadContract.as_view(), name='download_contract'),
    path('solicitud/<uuid:uuid>/carta_responsiva/descargar', DownloadResponsibility.as_view(), name='download_responsibility'),
    path('solicitud/<uuid:uuid>/lugar/<uuid:uuid_place>/gafete/descargar', DownloadGafete.as_view(), name='download_gafete'),
    path('solicitud/<uuid:uuid>/lugar/<uuid:uuid_place>/suministros/descargar', DownloadSuministros.as_view(), name='download_suministros'),
    path('tarjeton/<uuid:uuid>/descargar', DownloadTarjeton.as_view(), name='download_tarjeton'),
    path('reportes/descargar', DownloadReport.as_view(), name='download_report'),
    path('solicitudes/reporte/descargar', DownloadRequestsReport.as_view(), name='download_requests_report'),
    path('locales/reporte/descargar', DownloadStandsReport.as_view(), name='download_stands_report'),
    path('solicitud/<uuid:uuid>/lugar/<uuid:uuid_place>/pase_caja/descargar', DownloadReceipt.as_view(), name='download_receipt')
]