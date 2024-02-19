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

def get_date_constancy(request_, date):
    fecha = formats.date_format(localtime(date.fecha_reg), "j \d\e F \d\e Y \- h:m A")
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=CITA_ESPACIOS_FERIA.pdf'
    output = PdfWriter()
    inputw = PdfReader(open('static/docs/CITA_ESPACIOS_FERIA.pdf', 'rb'))
    # num_pages = inputw.getNumPages()
    buffer = io.BytesIO()
    pdf = Canvas(buffer)
    width, height = letter
    styles = getSampleStyleSheet() 
    def coord(x, y, height, unit=1): 
        x, y = x * unit, height - y * unit 
        return x, y 
    p = ParagraphStyle('user_name')
    p.alignment = TA_CENTER
    p.fontSize = 11
    p.leading = 20
    # fecha reg
    pdf.drawString(237, 620, fecha)
    # username
    pdf.drawString(247, 410, textwrap.wrap(request_.usuario.get_full_name(), 40)[0])
    # curp/rfc
    pdf.drawString(247, 380, request_.curp_txt or request_.rfc_txt)
    # Fecha y Hora
    pdf.drawString(247, 353, '{} a las {} hrs.'.format(date.fecha.strftime('%d/%m/%Y'), date.hora.strftime('%H:%M')))
    # Folio
    pdf.drawString(247, 273, date.folio)
    #pdf.setFillColor(HexColor('#878787'))
    #pdf.drawString(707, 46, branch.folio)
    # QR de la empresa
    qr_text = str(date.uuid)
    qr_code = qr.QrCodeWidget(qr_text)
    bounds = qr_code.getBounds()
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    # d = Drawing(100, 100, transform=[100./width, 0, 0, 100./height, 0, 0])
    # d.add(qr_code)
    # renderPDF.draw(d, pdf, 343, 30)
    # Creación del pdf final
    pdf.save()
    watermark = PdfReader(buffer)
    page1 = inputw.pages[0]
    page1.merge_page(watermark.pages[0])
    output.add_page(page1)
    outputStream = response
    output.write(response)
    outputStream.close()
    return response