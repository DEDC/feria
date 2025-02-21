# Django
import datetime
import json

from django.utils import formats
from django.http import HttpResponse
from django.views import View
# DjangoRestFramework
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.conf import settings
from rest_framework.views import APIView
import requests
# dates
from apps.dates.tools import get_dates_from_range, get_times_from_range
from apps.dates.models import CitasAgendadas
from apps.places.models import Lugares
from apps.tpay.tools import solicitar_linea_captura, generarToken

all_dates = get_dates_from_range(settings.START_DATES, settings.END_DATES)
all_hours = get_times_from_range(settings.START_HOURS, settings.END_HOURS, settings.PERIODS_TIME)


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
@permission_classes([IsAuthenticated])
def get_available_dates(request):
    scheduled = CitasAgendadas.objects.filter(fecha__year=2025).values('fecha', 'hora')
    exclude_dates = []
    for sch in scheduled:
        if sch['fecha'].strftime('%Y-%m-%d') in all_dates:
            hours_completed = 0
            for hr in all_hours:
                modules_scheduled = scheduled.filter(fecha=sch['fecha'], hora=hr).count()
                if modules_scheduled >= settings.ATTENTION_MODULES:
                    hours_completed += 1
            if hours_completed == len(all_hours):
                exclude_dates.append(sch['fecha'].strftime('%Y-%m-%d'))
    fdates = [{'short_format': d.strftime('%Y-%m-%d'), 'text_format': formats.date_format(d, "j \d\e F \d\e Y")} for d
              in all_dates if d.strftime('%Y-%m-%d') not in exclude_dates]
    return Response(fdates)


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
@permission_classes([IsAuthenticated])
def get_available_times(request, date):
    exclude_hours = []
    for hr in all_hours:
        modules_scheduled = CitasAgendadas.objects.filter(fecha=date, hora=hr).count()
        if modules_scheduled >= settings.ATTENTION_MODULES:
            exclude_hours.append(hr)
    fhours = [{'short_format': t} for t in all_hours if t not in exclude_hours]
    return Response(fhours)


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
@permission_classes([IsAuthenticated])
def get_curp_service(request, curp):
    response = []
    headersAuth = {
        'Authorization': f'Bearer {settings.TOKEN_CURP}',
    }

    data = {
        'curp': curp
    }
    print(headersAuth)
    resp = requests.post(f"{settings.URL_CURP}consulta-curp", json=data, headers=headersAuth, verify=False,
                         stream=False)
    if resp.status_code == 200:
        response = resp.json()
    return Response(response)


class PDFLineaCapturaView(View):
    def get(self, request, *args, **kwargs):
        # URL desde donde se obtiene el PDF
        pdf_url = Lugares.objects.filter(uuid=self.kwargs["pk"]).first()

        if not pdf_url:
            return Response({"error": "No se proporcionó la URL del PDF"}, status=400)

        try:
            # Obtener el PDF usando requests
            r = requests.get(pdf_url.data_tpay["urlFormatoPago"])
            r.raise_for_status()  # Levanta una excepción para códigos de error HTTP
        except Exception as e:
            return Response({"error": f"Error al obtener el PDF: {str(e)}"}, status=400)

        # Retornar el contenido del PDF con el Content-Type adecuado
        response = HttpResponse(r.content, content_type='application/pdf')
        # 'inline' permite mostrarlo en el navegador (ideal para un iframe)
        response['Content-Disposition'] = 'inline; filename="document.pdf"'
        return response


class TpayLineaCapturaView(APIView):
    def get(self, request, *args, **kwargs):
        # URL desde donde se obtiene el PDF
        lugar: Lugares = Lugares.objects.filter(uuid=self.kwargs["pk"]).first()
        response = None
        if not lugar:
            return Response({"error": "No se proporcionó la información requerida"}, status=400)

        try:
            # Obtener el PDF usando requests
            user_data = json.dumps({
                "user": lugar.solicitud.nombre,
                "email": lugar.solicitud.usuario.email
            }, separators=(",", ":")
            )
            token, error = generarToken(user_data)

            if not error:
                lineapago = solicitar_linea_captura(
                    token, "{}-{}".format(lugar.solicitud.folio, datetime.datetime.now().strftime("%H%M%S")),
                    lugar.tramite_id,
                    lugar.solicitud.nombre, lugar.solicitud.curp_txt, lugar.solicitud.calle,
                    lugar.solicitud.colonia, lugar.solicitud.codigo_postal, lugar.solicitud.estado,
                    lugar.solicitud.municipio
                )
                lugar.tpay_folio = lineapago["data"]["lineaCaptura"]["_text"].split('|')[0]
                lugar.data_tpay = {
                    "fechaVencimiento": lineapago["data"]["fechaVencimiento"]["_text"],
                    "folioControlEstado": lineapago["data"]["folioControlEstado"]["_text"],
                    "urlFormatoPago": lineapago["data"]["urlFormatoPago"]["_text"],
                    "lineaCaptura": lineapago["data"]["lineaCaptura"]["_text"],
                    "folioSeguimiento": lineapago["data"]["folioSeguimiento"]["_text"],
                    "importe": lineapago["data"]["importe"]["_text"],
                }
                solicitud = lugar.solicitud
                solicitud.data_tpay = lugar.data_tpay
                solicitud.save()
                lugar.save()
            response = {
                "query": False,
                "dataOrden": {
                    "lineaCaptura": lugar.data_tpay["lineaCaptura"].split("|")[0],
                    "deviceUuid": lugar.uuid,  # UUID por solicitudCaptura por id usuario
                    "userId": 3,
                    "sistemaId": int(settings.TPAY_PROJECT_ID),
                    "platform": settings.TPAY_PROJECT,
                    "newCharge": {
                        "amount": lugar.data_tpay["importe"],
                        "orderId": "2025-{}".format(lugar.data_tpay["lineaCaptura"].split("|")[0])
                    }
                },
                "key": settings.TPAY_APIKEY,
                "key_session_boardin": settings.TPAY_SESSION_ABORDAJE,
                "key_session_passport": settings.TPAY_SESSION_ACCESS,
                "key_channel_service": "scriptComponent",
                "socketId": settings.TPAY_SOCKET,
                "nombre": lugar.solicitud.nombre,
                "apellidoP": ".",
                "apellidoM": ".",
                "email": lugar.usuario.email,
                "nomCSis": settings.TPAY_SISTEMA
            }
        except requests.RequestException as e:
            return Response({"error": f"Error al obtener el PDF: {str(e)}"}, status=400)
        return Response(data=response)

    @renderer_classes((JSONRenderer,))
    @permission_classes([IsAuthenticated])
    def post(self, request, *args, **kwargs):
        data = request.data
        lugar = Lugares.objects.filter(tpay_folio=self.kwargs["pk"]).first()
        response = {
            "data": {
                "resultado": 0,  # (0: éxito, 1: error)
                "message": "Ok",  # (notificación exitosa o Descripción del error)
            }
        }
        if not lugar:
            lugar.tpay_pagado = True
            lugar.save()
        return Response(data=response)


class TpayValidadoView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        lugar = Lugares.objects.filter(tpay_folio=self.kwargs["pk"]).first()
        response = {
            "data": {
                "resultado": 0,  # (0: éxito, 1: error)
                "message": "Ok",  # (notificación exitosa o Descripción del error)
            }
        }
        if lugar:
            lugar.tpay_pagado = True
            lugar.tpay_socket = True
            lugar.save()

            data = {
                "data": {
                    "AuthS701": "180403",
                    "referenceKey": "20231399258334681271",
                    "AccessUser": "BBV",
                    "EstablishNum": "7681",
                    "BranchSource": "7681",
                }
            }

            # validacion = solicitar_linea_captura(token, data)
        else:
            response = {
                "data": {
                    "resultado": 1,  # (0: éxito, 1: error)
                    "message": "No se encontro un folio para el lugar",
                    # (notificación exitosa o Descripción del error)
                }
            }
        return Response(data=response)


class WebHookTapyApiView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data
        print(data)
        response = {
            "data": {
                "resultado": 0,  # (0: éxito, 1: error)
                "message": "Ok",  # (notificación exitosa o Descripción del error)
            }
        }
        # URL desde donde se obtiene el PDF
        lugar: Lugares = Lugares.objects.filter(tpay_folio=data.get("preferencia_operacion")).first()
        if lugar:
            lugar.tpay_pagado = True
            lugar.tpay_web = True
            lugar.save()
            response = {
                "data": {
                    "resultado": 0,  # (0: éxito, 1: error)
                    "message": "Informacion registrada satisfactoriamente",
                    # (notificación exitosa o Descripción del error)
                }
            }
        else:
            response = {
                "data": {
                    "resultado": 1,  # (0: éxito, 1: error)
                    "message": "No existe registro del folio de seguimiento para el pago",
                    # (notificación exitosa o Descripción del error)
                }
            }
        return Response(data=response)
