# Python
import io
import textwrap
# Django
from django.http import HttpResponse
# Reportlab and PyPDF2
from PyPDF2 import PdfWriter, PdfReader
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.timezone import localtime
from django.utils import timezone
import pytz

timezone.activate(pytz.timezone("America/Mexico_City"))

def get_receipt(place, px):
    output = PdfWriter()
    inputw = PdfReader(open('static/docs/pase_caja.pdf', 'rb'))
    buffer = io.BytesIO()
    pdf = Canvas(buffer)
    width, height = letter
    # username
    pdf.drawString(195, 624, textwrap.wrap(place.solicitud.nombre.upper(), 30)[0])
    pdf.drawString(107, 575, place.solicitud.folio)
    pdf.drawString(343, 575, place.nombre)
    pdf.drawString(475, 575, place.get_zona_display())
    if px is not None:
        pdf.drawString(142, 521, f'${intcomma(px.precio)}')
        pdf.drawString(330, 521, str(f'{px.folio} (1 Gafete Extra)'))
    else:
        pdf.drawString(142, 521, f'${intcomma(place.precio)}')
        pdf.drawString(375, 521, str(place.folio))
    pdf.setFont("Helvetica", 8)
    pdf.drawString(260, 464, timezone.localtime(timezone.now()).strftime("%d-%m-%Y %H:%M"))
    pdf.drawString(457, 464, timezone.localtime(timezone.now() + + timezone.timedelta(days=1)).strftime("%d-%m-%Y %H:%M"))
    pdf.save()
    watermark = PdfReader(buffer)
    page1 = inputw.pages[0]
    page1.merge_page(watermark.pages[0])
    output.add_page(page1)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=PASE_CAJA_{}.pdf'.format(place.folio)
    outputStream = response
    output.write(response)
    outputStream.close()
    return response