# Python
import io
# Django
from django.http import HttpResponse
from django.http import Http404
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
    qr_coords = 0, 0
    name_coords = 0, 0
    if place.zona == 'amb':
        url = 'static/docs/gafete_ambulante.pdf'
        qr_coords = 229, 120
        name_coords = 480, 305
        font_size = 33
        line_height = 35
    elif place.zona == 'z_a' or place.zona == 'n_1' or place.zona == 'n_2' or place.zona == 's_t':
        url = 'static/docs/gafete_zona_a.pdf'
        qr_coords = 395, 113
        name_coords = 230, 230
        font_size = 20
        line_height = 21
    elif place.zona == 'z_b':
        url = 'static/docs/gafete_zona_b.pdf'
        qr_coords = 395, 113
        name_coords = 230, 230
        font_size = 20
        line_height = 21
    elif place.zona == 'z_c' or place.zona == 'teatro':
        url = 'static/docs/gafete_zona_c.pdf'
        qr_coords = 395, 113
        name_coords = 230, 230
        font_size = 20
        line_height = 21
    elif place.zona == 'z_d':
        url = 'static/docs/gafete_zona_d.pdf'
        qr_coords = 395, 113
        name_coords = 230, 230
        font_size = 20
        line_height = 21
    elif place.zona == 'n_3':
        url = 'static/docs/gafete_zona_e.pdf'
        qr_coords = 395, 113
        name_coords = 230, 230
        font_size = 20
        line_height = 21
    else:
        raise Http404('No se generó gafete para esa Zona. Intente de nuevo más tarde.')
    
    inputw = PdfReader(open(url, 'rb'))
    buffer = io.BytesIO()
    pdf = Canvas(buffer)
    pdf.setFont("Helvetica-Bold", font_size)
    text = place.solicitud.nombre.upper()
    for i, s in enumerate(wrap(text, 23)):
        y_step  = line_height * i
        y_start = name_coords[0] - y_step
        pdf.drawCentredString(name_coords[1], y_start, s)
        pdf.drawCentredString
    # QR
    qr_text = str(place.folio)
    qr_code = qr.QrCodeWidget(qr_text)
    bounds = qr_code.getBounds()
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    d = Drawing(100, 100, transform=[160./width, 0, 0, 160./height, 0, 0])
    d.add(qr_code)
    renderPDF.draw(d, pdf, qr_coords[0], qr_coords[1])
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