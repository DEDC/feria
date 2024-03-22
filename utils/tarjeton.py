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

def get_tarjeton(tarjeton):
    output = PdfWriter()
    inputw = PdfReader(open('static/docs/tarjeton.pdf', 'rb'))
    buffer = io.BytesIO()
    pdf = Canvas(buffer)
    pdf.setPageSize(landscape(TABLOID))
    width, height = landscape(TABLOID)
    # ubication
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(160, 460, tarjeton.get_acceso_display())
    pdf.drawString(610, 460, tarjeton.get_no_estacionamiento_display())
    pdf.drawString(783, 460, tarjeton.get_ubicacion_display())
    # names
    pdf.setFont("Helvetica-Bold", 35)
    pdf.drawString(78, 355, textwrap.wrap(tarjeton.nombre.upper(), 28)[0])
    # lables
    pdf.setFont("Helvetica", 17)
    pdf.drawString(78, 390, 'Nombre o Razón Social')
    # car
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(124, 302, textwrap.wrap(tarjeton.tipo.upper(), 13)[0])
    pdf.drawString(352, 302, textwrap.wrap(tarjeton.marca.upper(), 13)[0])
    pdf.drawString(568, 302, textwrap.wrap(tarjeton.color.upper(), 13)[0])
    pdf.drawString(787, 302, textwrap.wrap(tarjeton.placa.upper(), 13)[0])
    # QR
    qr_text = str(tarjeton.folio)
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
    response['Content-Disposition'] = 'attachment; filename=TARJETON-{}.pdf'.format(tarjeton.folio)
    outputStream = response
    output.write(response)
    outputStream.close()
    return response