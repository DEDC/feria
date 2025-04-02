import json
from decimal import Decimal

from django.db.models import Q

from apps.admin.views import place_concept_alcohol
from apps.places.models import Lugares, HistorialTapy, ProductosExtras, Solicitudes, Pagos
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
        print(folio)
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
    lugares = Lugares.objects.filter(
        caja_pago=False, tpay_pagado=False, transfer_pago=False
    ).exclude(usuario_id=1711).exclude(solicitud_id=1177).exclude(solicitud_id=49).exclude(solicitud_id=1236).exclude(solicitud_id=1239).exclude(zona='amb').exclude(tramite_id=0)
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
            # print(status)
            if status["respuesta"] == False:
                # if status["codigoEstatus"] != 0:
                    # Obtener el PDF usando requests
                HistorialTapy.objects.filter(lugar=l).delete()
                ProductosExtras.objects.filter(lugar=l).delete()
                l.delete()
                print(status)
                process += 1
        else:
            print("Eliminado sin tpay")
            HistorialTapy.objects.filter(lugar=l).delete()
            ProductosExtras.objects.filter(lugar=l).delete()
            l.delete()
            process_b += 1

    print(f"Elminados con tpay: {process}")
    print(f"Elminados: {process_b}")


def aplicar_pago_solicitud(sol: Solicitudes):
    places = sol.solicitud_lugar.filter(estatus='assign')

    validados = places.filter(
        Q(transfer_pago=True) |
        Q(tpay_pagado=True) |
        Q(caja_pago=True)
    ).count()
    total_tpay = places.count()

    if places.count() > 0 and validados == total_tpay:
        if sol.estatus == 'validated' or sol.estatus == 'validated-direct':
            if not Pagos.objects.filter(solicitud=sol):
                Pagos.objects.get_or_create(
                    solicitud=sol, usuario=sol.usuario, tipo='caja', pagado=True,
                    validador=sol.usuario.get_full_name()
                )


def pagos_solicitudes():
    solicitudes = Solicitudes.objects.all()
    print(f"Total: {solicitudes.count()}")
    for x, sol in enumerate(solicitudes):
        print(f"No: {x}")
        places = sol.solicitud_lugar.filter(estatus='assign')
        validados = places.filter(
            Q(transfer_pago=True) |
            Q(tpay_pagado=True) |
            Q(caja_pago=True)
        ).count()
        total_tpay = places.count()

        if places.count() > 0 and validados == total_tpay:
            if sol.estatus == 'validated' or sol.estatus == 'validated-direct':
                if not Pagos.objects.filter(solicitud=sol):
                    Pagos.objects.get_or_create(
                        solicitud=sol, usuario=sol.usuario, tipo='caja', pagado=True,
                        validador=sol.usuario.get_full_name()
                    )
