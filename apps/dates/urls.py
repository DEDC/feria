from django.urls import path
from apps.dates.views import get_available_dates, get_available_times, get_curp_service, PDFLineaCapturaView, \
    TpayLineaCapturaView, TpayValidadoView, WebHookTapyApiView
# admin
from apps.admin.views import render_place

urlpatterns = [
    path('get-available-dates', get_available_dates),
    path('get-available-times/<str:date>', get_available_times),
    path('get-curp-service/<str:curp>', get_curp_service),
    path('places/<str:key>/data', render_place),
    path('places/pdfcpatura/<str:pk>', PDFLineaCapturaView.as_view(), name='pdfcpatura'),
    path('places/tpay/<str:pk>', TpayLineaCapturaView.as_view(), name='tpay-captura'),
    path('places/tpayval/<str:pk>', TpayValidadoView.as_view(), name='tpay-valid'),
    path('webhook/tpay', WebHookTapyApiView.as_view(), name='tpay-webhook'),
]