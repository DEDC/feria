import json

from apps.places.models import Lugares, HistorialTapy
from apps.tpay.tools import consulta_linea_captura, generarToken


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