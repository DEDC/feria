# Django
import datetime
import json
import logging
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
from apps.places.models import Lugares, HistorialTapy
from apps.tpay.tools import solicitar_linea_captura, generarToken, validar_linea_captura, status_linea_captura, \
    consulta_linea_captura, escribir_log

all_dates = get_dates_from_range(settings.START_DATES, settings.END_DATES)
all_hours = get_times_from_range(settings.START_HOURS, settings.END_HOURS, settings.PERIODS_TIME)

# Obtén el logger (en este caso se usa el logger raíz)
logger = logging.getLogger(__name__)


class JsProxyView(APIView):
    """
    APIView que actúa como proxy para cargar un archivo JS desde otra URL,
    enviando un header 'Origin' con un subdominio personalizado.
    """

    def get(self, request, **kwargs):
        # URL del archivo JavaScript a cargar

        tipo = "orden"  # Reemplaza con la URL real

        if self.kwargs["pk"] == 2:
            tipo = "object"

        # Define el header Origin con el subdominio que deseas enviar
        headers = {
            "Origin": "https://comercializacionferia.tabasco.gob.mx"  # Modifica según necesites
        }

        try:
            js_url = f"{settings.TPAY_RUTA}api/v1/component/js/{tipo}?clientid={settings.TPAY_APIKEY}"
            # Realiza la petición GET con el header personalizado
            response = requests.get(js_url, headers=headers)

            # Verifica que la respuesta haya sido exitosa
            if response.status_code == 200:
                # Retorna el contenido del JS con el MIME type adecuado
                return HttpResponse(response.content, content_type="text/javascript")
            else:
                return Response(
                    {"error": "No se pudo cargar el archivo JS"},
                    status=response.status_code
                )
        except requests.RequestException as e:
            return Response(
                {"error": f"Error al realizar la solicitud: {str(e)}"},
                status=500
            )


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


class TpayStatusLineaCapturaView(APIView):
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
                data = json.dumps({
                    "orderId": "2025-{}".format(lugar.tpay_folio),
                    "sistemaId": settings.TPAY_SISTEMA,
                    "proyecto": settings.TPAY_PROJECT,
                    "monto": lugar.data_tpay["importe"]
                }, separators=(",", ":")
                )
                status = status_linea_captura(token, data)
                lugar.tpay_status = status
                lugar.save()

        except requests.RequestException as e:
            return Response({"error": f"Error al obtener el PDF: {str(e)}"}, status=400)
        return Response(data=response)


class TpayConsultaLineaCapturaView(APIView):
    def get(self, request, *args, **kwargs):
        # URL desde donde se obtiene el PDF
        lugar: Lugares = Lugares.objects.filter(uuid=self.kwargs["pk"]).first()
        response = None
        if not lugar:
            return Response({"error": "No se proporcionó la información requerida"}, status=400)

        try:
            if not lugar.tpay_status:
                # Obtener el PDF usando requests
                user_data = json.dumps({
                    "user": lugar.solicitud.nombre,
                    "email": lugar.solicitud.usuario.email
                }, separators=(",", ":")
                )
                token, error = generarToken(user_data)

                if not error:
                    folio = f"/?folioSeguimiento={lugar.data_tpay['folioSeguimiento']}&idTramite={lugar.tramite_id}&folioControlEstado={lugar.data_tpay['folioControlEstado']}"
                    status = consulta_linea_captura(token, folio)
                    if "resultado" in status:
                        lugar.tpay_status = status
                        lugar.recibo_url = status["data"]['urlReciboPago']["_text"]
                        lugar.save()
            response = {"url_recibo": lugar.tpay_status["data"]['urlReciboPago']["_text"]}

        except requests.RequestException as e:
            return Response({"error": f"Error al obtener el PDF: {str(e)}"}, status=400)
        return Response(data=response)


class TpayLineaCapturaView(APIView):
    def get(self, request, *args, **kwargs):
        # URL desde donde se obtiene el PDF
        lugar: Lugares = Lugares.objects.filter(uuid=self.kwargs["pk"]).first()
        response = None
        if not lugar:
            return Response({"error": "No se proporcionó la información requerida"}, status=400)

        try:
            if lugar.data_tpay:
                user_data = json.dumps({
                    "user": lugar.solicitud.nombre,
                    "email": lugar.solicitud.usuario.email
                }, separators=(",", ":")
                )
                token, error = generarToken(user_data)

                if not error:
                    folio = f"/?folioSeguimiento={lugar.data_tpay['folioSeguimiento']}&idTramite={lugar.tramite_id}&folioControlEstado={lugar.data_tpay['folioControlEstado']}"
                    status = consulta_linea_captura(token, folio)
                    if "resultado" in status:
                        if status["resultado"]:
                            if status["data"]["codigoEstatus"]["_text"] == "00":
                                lugar.recibo_url = status["data"]["urlReciboPago"]["_text"]
                                lugar.tpay_status = status
                                lugar.tpay_pagado = True
                                lugar.tpay_service = True
                                lugar.save()
                                return Response(data={"pagado": True})
                            elif status["data"]["codigoEstatus"]["_text"] == "01":
                                return Response(data={"proceso": True})

                HistorialTapy.objects.create(
                    lugar=lugar, data_tpay=lugar.data_tpay, tpay_folio=lugar.tpay_folio
                )

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
    def put(self, request, *args, **kwargs):
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

            if not lugar.tpay_service:

                # Obtener el PDF usando requests
                user_data = json.dumps({
                    "user": lugar.solicitud.nombre,
                    "email": lugar.solicitud.usuario.email
                }, separators=(",", ":")
                )
                token, error = generarToken(user_data)

                if not error:

                    data = json.dumps({
                        "AuthS701": data["data"]["transaccion"],
                        "referenceKey": data["data"]["resultadoTrans"]["pordenp_ref"],
                        "AccessUser": 'BBV',#data["data"]["resultadoTrans"]["pcve_instrumento_pago"],
                        "EstablishNum": "7681",
                        "BranchSource": "7681",
                    }, separators=(",", ":")
                    )

                    validacion = validar_linea_captura(token, data)

                    logger.debug("{}".format(validacion))
                    if "res" in validacion:
                        lugar.tpay_service = True
                        if not lugar.tpay_val:
                            lugar.tpay_val = validacion
                        lugar.save()
                    else:
                        lugar.tpay_val = validacion
                        lugar.save()

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
        logger.error("{}".format(data))
        response = {
            "data": {
                "resultado": 0,  # (0: éxito, 1: error)
                "message": "Ok",  # (notificación exitosa o Descripción del error)
            }
        }
        try:
            # URL desde donde se obtiene el PDF
            lugar: Lugares = Lugares.objects.filter(tpay_folio=data["data"]["pordenp_ref"]).first()
            if lugar:
                lugar.tpay_pagado = True
                lugar.tpay_web = True
                lugar.tpay_val = data
                lugar.save()

                if not lugar.tpay_service:
                    # Obtener el PDF usando requests
                    user_data = json.dumps({
                        "user": lugar.solicitud.nombre,
                        "email": lugar.solicitud.usuario.email
                    }, separators=(",", ":")
                    )
                    token, error = generarToken(user_data)

                    if not error:

                        data = json.dumps({
                            "data": {
                                "AuthS701": data["data"]["transaccion"],
                                "referenceKey": data["data"]["resultadoTrans"]["pordenp_ref"],
                                "AccessUser": data["data"]["resultadoTrans"]["pcve_instrumento_pago"],
                                "EstablishNum": "7681",
                                "BranchSource": "7681",
                            }
                        }, separators=(",", ":"))

                        validacion = validar_linea_captura(token, data)

                        logger.info("{}".format(validacion))
                        if validacion:
                            # lugar.tpay_service = True
                            # lugar.tpay_val = validacion
                            lugar.save()
                        else:
                            lugar.tpay_val = validacion
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
        except Exception as e:
            escribir_log("Error WebHookTapyApiView.")
            escribir_log(f"{e}")
        return Response(data=response)
