# Django
from django.http import HttpResponse
# places
from apps.places.models import Lugares
# openpyxl
from openpyxl import load_workbook
from openpyxl.drawing.image import Image

def get_report():
    wb = load_workbook('static/docs/layout_feria.xlsx')
    ws = wb.get_sheet_by_name('LOCALES')
    places = Lugares.objects.all().order_by('solicitud__folio', 'zona')
    counter = 4
    for p in places:
        ws.cell(row=counter, column=1).value = p.folio
        ws.cell(row=counter, column=2).value = p.nombre
        ws.cell(row=counter, column=3).value = p.get_zona_display()
        ws.cell(row=counter, column=4).value = p.precio
        ws.cell(row=counter, column=5).value = p.m2
        ws.cell(row=counter, column=6).value = p.solicitud.nombre
        ws.cell(row=counter, column=7).value = p.solicitud.folio
        ws.cell(row=counter, column=8).value = p.solicitud.get_estatus_display()
        ws.cell(row=counter, column=9).value = p.solicitud.nombre if hasattr(p.solicitud, 'comercio') else 'Sin Comercio'
        ws.cell(row=counter, column=10).value = p.solicitud.usuario.email
        ws.cell(row=counter, column=11).value = p.solicitud.usuario.get_full_name()
        payment = p.solicitud.solicitud_pagos.first()
        if payment:
            ws.cell(row=counter, column=12).value = 'Pagado' if payment.pagado else 'No pagado'
            ws.cell(row=counter, column=13).value = payment.get_tipo_display()
            ws.cell(row=counter, column=14).value = payment.validador or 'No definido'
        counter_column = 15
        for px in p.extras.all():
            ws.cell(row=counter, column=counter_column).value = px.get_tipo_display()
            counter_column += 1
            ws.cell(row=counter, column=counter_column).value = px.precio
            counter_column += 1
            ws.cell(row=counter, column=counter_column).value = 'Aplica para {}'.format(px.to_places)
            counter_column += 1
        counter += 1
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    wb.save(response)
    response['Content-Disposition'] = 'attachment; filename=REPORTE_SISCOMFERIA.xlsx'
    return response