import base64
import json
import logging
from datetime import datetime
from django.core.mail import send_mail, EmailMultiAlternatives
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from feria import settings

keyAES = settings.kEYAES
ivAES = settings.IVAES


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
            data=jsonData, verify=False, stream=False
        )
        respJson = json.loads(response.text)
        tokenDesencriptado = desencriptado(respJson["data"])
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


def solicitar_linea_captura(token, folio, nombre, curp, calle, colonia, cp, estado, municipio):
    try:
        folio = f"/?folioSeguimiento={folio}&token={token}&nombre={nombre}&curp={curp}&calle={calle}&colonia={colonia}&cp={cp}&estado={estado}&municipio={municipio}"
        # folio = f"/?folioSeguimiento={folio}&token={token}&nombre={nombre}&paterno={paterno}&materno={materno}&curp={curp}&calle={calle}&colonia={colonia}&cp={cp}&estado={estado}&municipio={municipio}"
        folioEncriptado = encriptarData(folio)
        header = {
            "Content-Type": "application/json",
            "Access-Control-Allow-Methods": "GET, POST",
            "X-API-KEY": settings.TPAY_APIKEY,
            "X-SESSION-KEY": settings.TPAY_SESSION_ACCESS,
            "X-SISTEMA-KEY": settings.TPAY_SISTEMA,
            "Authorization": f"Bearer {token}"
        }
        response = requests.get(f"{settings.TPAY_RUTA}?query={folioEncriptado}", headers=header)
        respLinea = desencriptado(response.text)
        data = json.loads(respLinea)
        return data
    except Exception as e:
        logging.warning("------------------ERROR desencriptado----------------")
        logging.warning(f"Fecha: {datetime.now()}")
        logging.error(f"error desencriptado: {e}")
        logging.warning("----------------------------------")
        return e
