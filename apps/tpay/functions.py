import json
from decimal import Decimal

from apps.admin.views import place_concept_alcohol
from apps.places.models import Lugares, HistorialTapy, ProductosExtras
from apps.tpay.tools import consulta_linea_captura, generarToken, status_linea_captura, validar_linea_captura, \
    escribir_log
from feria import settings


def get_validar_pago(id, historico=False):
    lugar: Lugares = Lugares.objects.filter(pk=id).first()
    data_tpay = lugar.data_tpay
    if historico:
        hist = HistorialTapy.objects.filter(pk=historico).first()
        data_tpay = hist.data_tpay

    user_data = json.dumps({
        "user": lugar.solicitud.nombre,
        "email": lugar.solicitud.usuario.email
    }, separators=(",", ":")
    )
    token, error = generarToken(user_data)

    if not error:
        folio = f"/?folioSeguimiento={data_tpay['folioSeguimiento']}&idTramite={lugar.tramite_id}&folioControlEstado={data_tpay['folioControlEstado']}"
        status = consulta_linea_captura(token, folio)
        print(status)
        return status


def validar_pago(folio, importe):
    data = json.dumps({
        "orderId": "2025-{}".format(folio),
        "sistemaId": 21,
        "proyecto": settings.TPAY_PROJECT,
        "monto": importe
    }, separators=(",", ":")
    )
    status = status_linea_captura("", data)
    print(status)


def status_validar_pago(id, historico=False):
    lugar: Lugares = Lugares.objects.filter(pk=id).first()
    data_tpay = lugar.data_tpay
    tpay_folio = lugar.tpay_folio
    if historico:
        hist = HistorialTapy.objects.filter(pk=historico).first()
        data_tpay = hist.data_tpay
        tpay_folio = hist.tpay_folio

    data = json.dumps({
        "orderId": "2025-{}".format(tpay_folio),
        "sistemaId": 21,
        "proyecto": settings.TPAY_PROJECT,
        "monto": int(lugar.precio)
    }, separators=(",", ":")
    )
    status = status_linea_captura("", data)
    print(status)
    if status["codigoEstatus"] == 0:
        # Obtener el PDF usando requests
        user_data = json.dumps({
            "user": lugar.solicitud.nombre,
            "email": lugar.solicitud.usuario.email
        }, separators=(",", ":")
        )
        token, error = generarToken(user_data)

        if not error:
            if not error:
                data = json.dumps({
                    "AuthS701": status["data"]["pnum_autorizacion"],
                    "referenceKey": status["data"]["pordenp_ref"],
                    "AccessUser": 'BBV',  # data["data"]["resultadoTrans"]["pcve_instrumento_pago"],
                    "EstablishNum": "7681",
                    "BranchSource": "7681",
                }, separators=(",", ":")
                )

                validacion = validar_linea_captura(token, data)
                print(validacion)
                if "res" in validacion:
                    lugar.tpay_service = True
                    # lugar.tpay_status = get_validar_pago(lugar.id)

    lugar.data_tpay = data_tpay
    lugar.tpay_val = status
    lugar.tpay_pagado = True
    lugar.tpay_web = True
    lugar.tpay_service = True
    lugar.tpay_socket = True
    lugar.tpay_folio = tpay_folio
    lugar.save()
    return status


def updateFolioHistorial():
    historial = HistorialTapy.objects.all()
    for hist in historial:
        hist.tpay_folio = hist.data_tpay["lineaCaptura"].split("|")[0]
        hist.save()


def aplicar_licencia(folio):
    lugar: Lugares = Lugares.objects.filter(folio=folio).first()
    if lugar:
        ProductosExtras.objects.create(
            lugar=lugar, tipo='licencia_alcohol', m2=lugar.m2, to_places=lugar.folio,
            precio_tpay=lugar.precio, tramite_id=lugar.tramite_id
        )
        lugar.precio = Decimal(place_concept_alcohol[lugar.tramite_id.__str__()][1])
        lugar.tramite_id = place_concept_alcohol[lugar.tramite_id.__str__()][0]
        lugar.tpay_alcohol = True
        lugar.save()


def process_validated_pay():
    lugares = Lugares.objects.filter(caja_pago=False, tpay_pagado=False, transfer_pago=False).exclude(usuario_id=1711)
    escribir_log(f"Total: {lugares.count()}", "logs/process_validated.log")
    process = 0
    process_b = 0
    print(f"Total: {lugares.count()}")
    for l in lugares:
        if l.data_tpay:
            data = json.dumps({
                "orderId": "2025-{}".format(l.tpay_folio),
                "sistemaId": 21,
                "proyecto": settings.TPAY_PROJECT,
                "monto": int(l.precio)
            }, separators=(",", ":")
            )
            status = status_linea_captura("", data)
            escribir_log(f"{status}", "logs/process_validated.log")
            print(status)
            if status["respuesta"] == True:
                if status["codigoEstatus"] != 0:
                    # Obtener el PDF usando requests
                    # HistorialTapy.objects.filter(lugar=l).delete()
                    # l.delete()
                    print(status)
                    process += 1
        else:
            # l.delete()
            print("Eliminado sin tpay")
            process_b += 1

    print(f"Elminados con tpay: {process}")
    print(f"Elminados: {process_b}")
