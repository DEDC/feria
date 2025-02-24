import base64
import json
import logging
from datetime import datetime
from django.core.mail import send_mail, EmailMultiAlternatives
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from feria import settings
import os
from datetime import datetime


keyAES = settings.kEYAES
ivAES = settings.IVAES
tramites = {
    "A": "6171", "B": "6172", "C": "6173", "D": "6174", "N1": "6175",
    "N2": "6176", "N3": "6177", "N4": "6178", "N5": "6179"
}


def escribir_log(mensaje, archivo_log="logs/feria.log"):
    """
    Escribe una línea en un archivo de log. Si no existe, lo crea.

    :param mensaje: Texto a escribir en el log.
    :param archivo_log: Nombre o ruta del archivo de log (por defecto "app.log").
    """
    try:
        # Obtener la fecha y hora actual
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Crear la carpeta si el archivo está dentro de una ruta que no existe
        os.makedirs(os.path.dirname(f"{settings.BASE_DIR}/{archivo_log}"), exist_ok=True)

        # Abrir el archivo en modo append ('a') para agregar líneas sin sobrescribir
        with open(archivo_log, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} - {mensaje}\n")

    except Exception as e:
        print(f"Error al escribir en el log: {e}")


def encriptarData(data):
    try:
        datos = str(data).encode('utf-8')
        # parametros
        mode = AES.MODE_CBC
        # encriptacion
        encryptor = AES.new(keyAES.encode("utf-8"), mode, ivAES.encode("utf-8"))
        dataEncriptada = encryptor.encrypt(pad(datos, AES.block_size, "pkcs7"))
        dataEncriptadaBase64 = base64.b64encode(dataEncriptada).decode("utf-8")
        return dataEncriptadaBase64
    except Exception as error:
        logging.warning("------------------ERROR encriptarData----------------")
        logging.warning(f"Fecha: {datetime.now()}")
        logging.error(error)
        logging.warning("----------------------------------")
        return error


def desencriptado(data):
    try:
        mode = AES.MODE_CBC
        encryptor = AES.new(keyAES.encode("utf-8"), mode, ivAES.encode("utf-8"))
        # desencriptacion
        conversorbytes = base64.b64decode(data)
        desencriptar = unpad(encryptor.decrypt(conversorbytes), AES.block_size, "pkcs7").decode()
        return desencriptar
    except Exception as error:
        logging.warning("------------------ERROR desencriptado----------------")
        logging.warning(f"Fecha: {datetime.now()}")
        logging.error(f"error desencriptado: {error}")
        logging.warning("----------------------------------")
        return error


def generarToken(usuario):
    try:
        dataUser = encriptarData(usuario)

        jsonData = json.dumps({"data": dataUser}, separators=(",", ":"))

        header = {
            "Content-Type": "application/json",
            "Access-Control-Allow-Methods": "GET, POST",
            "X-API-KEY": settings.TPAY_APIKEY,
            "X-SESSION-KEY": settings.TPAY_SESSION_ABORDAJE,
            "X-CHANNEL-SERVICE": settings.TPAY_CHANNEL_SERVICE
        }

        param = {"query": False}

        response = requests.post(
            "{}api/v1/gateway/client/loginMov".format(settings.TPAY_RUTA), params=param, headers=header,
            data=jsonData
        )
        respJson = json.loads(response.text)
        tokenDesencriptado = desencriptado(respJson["data"])

        # Ejemplo de uso
        escribir_log("JSON de Token.")
        escribir_log(tokenDesencriptado)
        token = json.loads(tokenDesencriptado)
        return token["session"]["token_user"], False
    except Exception as e:
        logging.warning("------------------ERROR desencriptado----------------")
        logging.warning(f"Fecha: {datetime.now()}")
        logging.error(f"error desencriptado: {e}")
        logging.warning("----------------------------------")
        return "504 Tiempo de espera agotado", True


def sendEmail(correo, html, subject):
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [correo]

    # Crear el correo con versión en texto plano y HTML
    message = EmailMultiAlternatives(subject, "Tu solicitud ha sido aprobada.", from_email, to_email)
    message.attach_alternative(html, "text/html")  # Agrega el contenido HTML

    # Enviar correo
    message.send()


def solicitar_linea_captura(token, folio, tramite_id, nombre, curp, calle, colonia, cp, estado, municipio):
    try:
        folio = f"/?folioSeguimiento={folio}&idTramite={tramite_id}&nombre={nombre}&curp={curp}&calle={calle}&colonia={colonia}&cp={cp}&estado={estado}&municipio={municipio}"
        # folio = f"/?folioSeguimiento={folio}&idTramite={tramites[zona]}"
        # folio = f"/?folioSeguimiento={folio}&token={token}&nombre={nombre}&paterno={paterno}&materno={materno}&curp={curp}&calle={calle}&colonia={colonia}&cp={cp}&estado={estado}&municipio={municipio}"
        folioEncriptado = encriptarData(folio)
        header = {
            "Content-Type": "application/json",
            "Access-Control-Allow-Methods": "GET, POST",
            "X-API-KEY": settings.TPAY_APIKEY,
            "X-SESSION-KEY": settings.TPAY_SESSION_ACCESS,
            "X-SISTEMA-KEY": settings.TPAY_SISTEMA,
            "X-CHANNEL-SERVICE": settings.TPAY_CAPTURA,
            "Authorization": f"Bearer {token}"
        }
        parms = {"query": folioEncriptado}

        response = requests.get(
            f"{settings.TPAY_RUTA}api/v1/gateway/servExtApi1/externo/getLineaCaptura?query={folioEncriptado}",
            headers=header
        )
        respLinea = desencriptado(response.text)

        # Ejemplo de uso
        escribir_log("JSON de Linea Captura.")
        escribir_log(respLinea)
        data = json.loads(respLinea)
        return data
    except Exception as e:
        logging.warning("------------------ERROR desencriptado----------------")
        logging.warning(f"Fecha: {datetime.now()}")
        logging.error(f"error desencriptado: {e}")
        logging.warning("----------------------------------")
        return e


def validar_linea_captura(token, data):
    try:
        folioEncriptado = encriptarData(data)
        header = {
            "Content-Type": "application/json",
            "Access-Control-Allow-Methods": "GET, POST",
            "X-API-KEY": settings.TPAY_APIKEY,
            "X-SESSION-KEY": settings.TPAY_SESSION_ACCESS,
            "X-SISTEMA-KEY": settings.TPAY_SISTEMA,
            "X-CHANNEL-SERVICE": settings.TPAY_CHANNEL_INFO,
            "Authorization": f"Bearer {token}"
        }

        data_val = {"data": folioEncriptado}

        param = {"query": False}

        response = requests.post(
            f"{settings.TPAY_RUTA}api/v1/gateway/servInfApi1/pagos/bancoOnline",
            headers=header, params=param, json=data_val
        )
        respLinea = desencriptado(response.text)

        # Ejemplo de uso
        escribir_log("JSON de Validar Captura.")
        escribir_log(respLinea)
        data = json.loads(respLinea)
        return data
    except Exception as e:
        logging.warning("------------------ERROR desencriptado----------------")
        logging.warning(f"Fecha: {datetime.now()}")
        logging.error(f"error desencriptado: {e}")
        logging.warning("----------------------------------")
        return e


def status_linea_captura(token, data):
    try:
        folioEncriptado = encriptarData(data)
        header = {
            "Content-Type": "application/json",
            "Access-Control-Allow-Methods": "GET, POST",
            "X-API-KEY": settings.TPAY_APIKEY,
            "X-SESSION-KEY": settings.TPAY_SESSION_ABORDAJE,
            "X-SISTEMA-KEY": settings.TPAY_SISTEMA,
            "X-CHANNEL-SERVICE": settings.TPAY_CHANNEL_GESTOR,
            "Authorization": f"Bearer {token}"
        }

        data_val = {"data": folioEncriptado}

        param = {"query": False}

        response = requests.post(
            f"{settings.TPAY_RUTA}api/v1/gateway/gestorApi1/transactions/statusN",
            headers=header, params=param, json=data_val
        )
        respLinea = desencriptado(response.text)

        # Ejemplo de uso
        escribir_log("JSON de Status Captura.")
        escribir_log(respLinea)
        data = json.loads(respLinea)
        return data
    except Exception as e:
        logging.warning("------------------ERROR desencriptado----------------")
        logging.warning(f"Fecha: {datetime.now()}")
        logging.error(f"error desencriptado: {e}")
        logging.warning("----------------------------------")
        return e


def consulta_linea_captura(token, folio):
    try:
        folioEncriptado = encriptarData(folio)
        header = {
            "Content-Type": "application/json",
            "Access-Control-Allow-Methods": "GET, POST",
            "X-API-KEY": settings.TPAY_APIKEY,
            "X-SESSION-KEY": settings.TPAY_SESSION_ACCESS,
            "X-SISTEMA-KEY": settings.TPAY_SISTEMA,
            "X-CHANNEL-SERVICE": settings.TPAY_CAPTURA,
            "Authorization": f"Bearer {token}"
        }

        param = {"query": folioEncriptado}

        response = requests.get(
            f"{settings.TPAY_RUTA}api/v1/gateway/servExtApi1/externo/consultar-pago?query={folioEncriptado}",
            headers=header
        )
        respLinea = desencriptado(response.text)

        # Ejemplo de uso
        escribir_log("JSON de Consulta Captura.")
        escribir_log(respLinea)
        data = json.loads(respLinea)
        return data
    except Exception as e:
        logging.warning("------------------ERROR desencriptado----------------")
        logging.warning(f"Fecha: {datetime.now()}")
        logging.error(f"error desencriptado: {e}")
        logging.warning("----------------------------------")
        return e
