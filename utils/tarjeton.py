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
from reportlab.lib.pagesizes import landscape, TABLOID

def get_tarjeton(tarjeton):
    output = PdfWriter()
    place = tarjeton.lugar
    if place.zona == 'z_a' or place.zona == 'n_1' or place.zona == 'n_2' or place.zona == 's_t':
        url = 'static/docs/tarjeton_zona_a.pdf'
    elif place.zona == 'z_b':
        url = 'static/docs/tarjeton_zona_b.pdf'
    elif place.zona == 'z_c' or place.zona == 'teatro':
        url = 'static/docs/tarjeton_zona_c.pdf'
    elif place.zona == 'z_d':
        url = 'static/docs/tarjeton_zona_d.pdf'
    elif place.zona == 'n_3':
        url = 'static/docs/tarjeton_zona_e.pdf'
    else:
        return HttpResponse('No se generó Tarjetón para esa Zona. Intente de nuevo más tarde.')
    inputw = PdfReader(open(url, 'rb'))
    buffer = io.BytesIO()
    pdf = Canvas(buffer)
    pdf.setPageSize(landscape(TABLOID))
    width, height = landscape(TABLOID)
    # inserts
    # x horizontal  y vertical
    pdf.setFont("Helvetica-Bold", 26)
    pdf.drawString(490, 289, place.nombre.upper())
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(185, 234, textwrap.wrap(tarjeton.nombre.upper(), 60)[0])
    pdf.drawString(159, 203, textwrap.wrap(tarjeton.nombre_comercial.upper(), 65)[0])
    pdf.drawString(83, 168, textwrap.wrap(tarjeton.marca.upper(), 12)[0])
    pdf.drawString(210, 168, textwrap.wrap(tarjeton.tipo.upper(), 12)[0])
    pdf.drawString(385, 168, textwrap.wrap(tarjeton.color.upper(), 12)[0])
    pdf.drawString(517, 168, textwrap.wrap(tarjeton.placa.upper(), 10)[0])
    # QR
    qr_text = str(tarjeton.folio)
    qr_code = qr.QrCodeWidget(qr_text)
    bounds = qr_code.getBounds()
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    d = Drawing(100, 100, transform=[115./width, 0, 0, 115./height, 0, 0])
    d.add(qr_code)
    renderPDF.draw(d, pdf, 486, 10)
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