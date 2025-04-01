# Python
import io
# Django
from django.http import HttpResponse
from django.core.exceptions import ValidationError
# Reportlab and PyPDF2
from PyPDF2 import PdfWriter, PdfReader
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from reportlab.pdfgen.canvas import Canvas
# Python
import io
from textwrap import wrap
# Django
from django.http import HttpResponse

def get_gafete(place):
    output = PdfWriter()
    if place.zona == 'amb':
        url = 'static/docs/gafete_ambulante.pdf'
    else:
        raise ValidationError('No se generó gafete para esa Zona. Intente de nuevo más tarde.', code = 'invalid_gafete')
    
    inputw = PdfReader(open(url, 'rb'))
    buffer = io.BytesIO()
    pdf = Canvas(buffer)
    pdf.setFont("Helvetica-Bold", 33)
    text = place.solicitud.nombre.upper()
    for i, s in enumerate(wrap(text, 23)):
        y_step  = 35 * i
        y_start = 480 - y_step
        pdf.drawCentredString(305, y_start, s)
        pdf.drawCentredString
    # QR
    qr_text = str(place.folio)
    qr_code = qr.QrCodeWidget(qr_text)
    bounds = qr_code.getBounds()
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    d = Drawing(100, 100, transform=[160./width, 0, 0, 160./height, 0, 0])
    d.add(qr_code)
    renderPDF.draw(d, pdf, 229, 120)
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