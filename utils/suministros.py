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
from reportlab.lib.pagesizes import letter, landscape, TABLOID

def get_suministros(place):
    output = PdfWriter()
    inputw = PdfReader(open('static/docs/suministros.pdf', 'rb'))
    buffer = io.BytesIO()
    pdf = Canvas(buffer)
    pdf.setPageSize(landscape(TABLOID))
    width, height = landscape(TABLOID)
    # ubication
    pdf.setFont("Helvetica-Bold", 33)
    pdf.drawString(568, 510, place.get_zona_display())
    pdf.drawString(880, 510, place.nombre)
    # names
    pdf.setFont("Helvetica-Bold", 35)
    name = ''
    if hasattr(place.solicitud, 'comercio'):
        name = place.solicitud.comercio.nombre.upper()
    else:
        name = place.solicitud.nombre.upper()
    pdf.drawString(90, 410, textwrap.wrap(place.solicitud.nombre.upper(), 28)[0])
    pdf.drawString(90, 350, textwrap.wrap(name, 28)[0])
    # lables
    pdf.setFont("Helvetica", 17)
    pdf.drawString(90, 445, 'Nombre o Razón Social')
    pdf.drawString(90, 385, 'Nombre Comercial')
    # QR
    qr_text = str(place.folio)
    qr_code = qr.QrCodeWidget(qr_text)
    bounds = qr_code.getBounds()
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    d = Drawing(100, 100, transform=[180./width, 0, 0, 180./height, 0, 0])
    d.add(qr_code)
    renderPDF.draw(d, pdf, 813, 19)
    # Creación del pdf final
    pdf.save()
    watermark = PdfReader(buffer)
    page1 = inputw.pages[0]
    page1.merge_page(watermark.pages[0])
    output.add_page(page1)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=SUMINISTROS_{}.pdf'.format(place.folio)
    outputStream = response
    output.write(response)
    outputStream.close()
    return response