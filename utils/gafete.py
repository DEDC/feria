# Python
import io
import textwrap
# Django
from django.http import HttpResponse
from django.utils.timezone import localtime
from django.utils import formats
# Reportlab and PyPDF2
from PyPDF2 import PdfWriter, PdfReader
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from reportlab.lib.colors import HexColor
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
# 
from reportlab.lib.units import mm, cm
from reportlab.lib.pagesizes import letter

def get_gafete(place):
    output = PdfWriter()
    inputw = PdfReader(open('static/docs/gafete.pdf', 'rb'))
    buffer = io.BytesIO()
    pdf = Canvas(buffer)
    width, height = letter
    # username
    pdf.setFont("Helvetica", 8)
    pdf.drawString(107, 162, place.get_zona_display())
    pdf.drawString(163, 162, place.nombre)
    pdf.drawString(82, 147, textwrap.wrap(place.solicitud.nombre.upper(), 24)[0])
    # QR
    qr_text = str(place.uuid)
    qr_code = qr.QrCodeWidget(qr_text)
    bounds = qr_code.getBounds()
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    d = Drawing(100, 100, transform=[130./width, 0, 0, 130./height, 0, 0])
    d.add(qr_code)
    renderPDF.draw(d, pdf, 71, 20)
    # Creación del pdf final
    pdf.save()
    watermark = PdfReader(buffer)
    page1 = inputw.pages[0]
    page1.merge_page(watermark.pages[0])
    output.add_page(page1)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=GAFETE_{}.pdf'.format(place.folio)
    outputStream = response
    output.write(response)
    outputStream.close()
    return response