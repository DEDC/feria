#!/usr/bin/env python3
import os
import zipfile
from datetime import datetime
from django.conf import settings
from apps.places.models import Solicitudes


def generate_files_zip():
    """
    Genera un archivo ZIP con los documentos de las solicitudes validadas.
    """
    # Carpeta pública donde se pondrá el ZIP
    public_folder = "/var/www/public_files_feria2025"
    os.makedirs(public_folder, exist_ok=True)

    # Nombre del ZIP con fecha
    zip_name = f"REPORTE_ARCHIVOS_FERIA_2025_{datetime.now().strftime('%Y%m%d')}.zip"
    zip_path = os.path.join(public_folder, zip_name)

    print(f"Generando ZIP en: {zip_path}")

    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for solicitud in Solicitudes.objects.all():
            if solicitud.estatus == 'validated' or solicitud.estatus == 'validated-direct':
                for doc in [solicitud.identificacion, solicitud.curp, solicitud.comprobante_domicilio, solicitud.acta_constitutiva]:
                    if doc and os.path.exists(doc.path):
                        arcname = os.path.join(f'{str(solicitud.folio)}_{solicitud.nombre}', os.path.basename(doc.name))
                        zf.write(doc.path, arcname=arcname)

    print(f"ZIP listo. Descargar en:")
    print(f"http://comercializacionferia.tabasco.gob.mx/zip_descargar/{zip_name}")