# Django
from django.http import HttpResponse
from django.db.models import Q, Sum, Count
import zipfile
import os
# places
from apps.places.models import Lugares, Pagos, ProductosExtras, Solicitudes
# openpyxl
from openpyxl import load_workbook

def get_docs():
    zf = zipfile.ZipFile(os.path.join('', 'SISCOMFERIA_DOCUMENTACION.zip'), 'w')
    counter = 1
    for sl in Solicitudes.objects.filter(solicitud_pagos__pagado=True):
        print(counter)
        if sl.identificacion:
            try:
                zf.write(sl.identificacion.path, f'{sl.folio}_{sl.nombre}/{os.path.basename(sl.identificacion.name)}')
            except Exception as e:
                pass
                print(e)
        
        if sl.acta_constitutiva:
            try:
                zf.write(sl.acta_constitutiva.path, f'{sl.folio}_{sl.nombre}/{os.path.basename(sl.acta_constitutiva.name)}')
            except Exception as e:
                pass
                print(e)
        
        if sl.comprobante_domicilio:
            try:
                zf.write(sl.comprobante_domicilio.path, f'{sl.folio}_{sl.nombre}/{os.path.basename(sl.comprobante_domicilio.name)}')
            except Exception as e:
                pass
                print(e)
        
        if sl.constancia_fiscal:
            try:
                zf.write(sl.constancia_fiscal.path, f'{sl.folio}_{sl.nombre}/{os.path.basename(sl.constancia_fiscal.name)}')
            except Exception as e:
                pass
                print(e)
        
        if sl.curp:
            try:
                zf.write(sl.curp.path, f'{sl.folio}_{sl.nombre}/{os.path.basename(sl.curp.name)}')
            except Exception as e:
                pass
                print(e)
        counter+=1
    zf.close()

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
    ws = wb.get_sheet_by_name('MONTOS')
    # n1
    ws['E4'] = Lugares.objects.filter(zona='n_1').count()
    ws['E8'] = Pagos.objects.filter(pagado=True).aggregate(total=Count('solicitud__solicitud_lugar', filter=Q(solicitud__solicitud_lugar__zona='n_1')))['total']
    ws['H4'] = Lugares.objects.filter(zona='n_1').aggregate(total=Sum('precio'))['total']
    ws['H8'] = Pagos.objects.filter(pagado=True).aggregate(total=Sum('solicitud__solicitud_lugar__precio', filter=Q(solicitud__solicitud_lugar__zona='n_1')))['total']
    # n3
    ws['O4'] = Lugares.objects.filter(zona='n_3').count()
    ws['O8'] = Pagos.objects.filter(pagado=True).aggregate(total=Count('solicitud__solicitud_lugar', filter=Q(solicitud__solicitud_lugar__zona='n_3')))['total']
    ws['R4'] = Lugares.objects.filter(zona='n_3').aggregate(total=Sum('precio'))['total']
    ws['R8'] = Pagos.objects.filter(pagado=True).aggregate(total=Sum('solicitud__solicitud_lugar__precio', filter=Q(solicitud__solicitud_lugar__zona='n_3')))['total']
    # z_a
    ws['E13'] = Lugares.objects.filter(zona='z_a').count()
    ws['E17'] = Pagos.objects.filter(pagado=True).aggregate(total=Count('solicitud__solicitud_lugar', filter=Q(solicitud__solicitud_lugar__zona='z_a')))['total']
    ws['H13'] = Lugares.objects.filter(zona='z_a').aggregate(total=Sum('precio'))['total']
    ws['H17'] = Pagos.objects.filter(pagado=True).aggregate(total=Sum('solicitud__solicitud_lugar__precio', filter=Q(solicitud__solicitud_lugar__zona='z_a')))['total']
    # z_b
    ws['O13'] = Lugares.objects.filter(zona='z_b').count()
    ws['O17'] = Pagos.objects.filter(pagado=True).aggregate(total=Count('solicitud__solicitud_lugar', filter=Q(solicitud__solicitud_lugar__zona='z_b')))['total']
    ws['R13'] = Lugares.objects.filter(zona='z_b').aggregate(total=Sum('precio'))['total']
    ws['R17'] = Pagos.objects.filter(pagado=True).aggregate(total=Sum('solicitud__solicitud_lugar__precio', filter=Q(solicitud__solicitud_lugar__zona='z_b')))['total']
    # z_c
    ws['E22'] = Lugares.objects.filter(zona='z_c').count()
    ws['E26'] = Pagos.objects.filter(pagado=True).aggregate(total=Count('solicitud__solicitud_lugar', filter=Q(solicitud__solicitud_lugar__zona='z_c')))['total']
    ws['H22'] = Lugares.objects.filter(zona='z_c').aggregate(total=Sum('precio'))['total']
    ws['H26'] = Pagos.objects.filter(pagado=True).aggregate(total=Sum('solicitud__solicitud_lugar__precio', filter=Q(solicitud__solicitud_lugar__zona='z_c')))['total']
    # z_d
    ws['O22'] = Lugares.objects.filter(zona='z_d').count()
    ws['O26'] = Pagos.objects.filter(pagado=True).aggregate(total=Count('solicitud__solicitud_lugar', filter=Q(solicitud__solicitud_lugar__zona='z_d')))['total']
    ws['R22'] = Lugares.objects.filter(zona='z_d').aggregate(total=Sum('precio'))['total']
    ws['R26'] = Pagos.objects.filter(pagado=True).aggregate(total=Sum('solicitud__solicitud_lugar__precio', filter=Q(solicitud__solicitud_lugar__zona='z_d')))['total']
    # terraza
    ws['E37'] = ProductosExtras.objects.filter(tipo='terraza').count()
    ws['E41'] = Pagos.objects.filter(pagado=True).aggregate(total=Count('solicitud__solicitud_lugar__extras', filter=Q(solicitud__solicitud_lugar__extras__tipo='terraza')))['total']
    ws['H37'] = ProductosExtras.objects.filter(tipo='terraza').aggregate(total=Sum('precio'))['total']
    ws['H41'] = Pagos.objects.filter(pagado=True).aggregate(total=Sum('solicitud__solicitud_lugar__extras__precio', filter=Q(solicitud__solicitud_lugar__extras__tipo='terraza')))['total']
    # terraza_grande
    ws['O37'] = ProductosExtras.objects.filter(tipo='terraza_grande').count()
    ws['O41'] = Pagos.objects.filter(pagado=True).aggregate(total=Count('solicitud__solicitud_lugar__extras', filter=Q(solicitud__solicitud_lugar__extras__tipo='terraza_grande')))['total']
    ws['R37'] = ProductosExtras.objects.filter(tipo='terraza_grande').aggregate(total=Sum('precio'))['total']
    ws['R41'] = Pagos.objects.filter(pagado=True).aggregate(total=Sum('solicitud__solicitud_lugar__extras__precio', filter=Q(solicitud__solicitud_lugar__extras__tipo='terraza_grande')))['total']
    # licencias_alcohol
    ws['E46'] = ProductosExtras.objects.filter(tipo='licencia_alcohol').count()
    ws['E50'] = Pagos.objects.filter(pagado=True).aggregate(total=Count('solicitud__solicitud_lugar__extras', filter=Q(solicitud__solicitud_lugar__extras__tipo='licencia_alcohol')))['total']
    ws['H46'] = ProductosExtras.objects.filter(tipo='licencia_alcohol').aggregate(total=Sum('precio'))['total']
    ws['H50'] = Pagos.objects.filter(pagado=True).aggregate(total=Sum('solicitud__solicitud_lugar__extras__precio', filter=Q(solicitud__solicitud_lugar__extras__tipo='licencia_alcohol')))['total']

    ws['Q29'] = Lugares.objects.all().aggregate(total=Sum('precio'))['total']
    ws['Q32'] = Pagos.objects.filter(pagado=True).aggregate(total=Sum('solicitud__solicitud_lugar__precio'))['total']

    ws['Q53'] = ProductosExtras.objects.all().aggregate(total=Sum('precio'))['total']
    ws['Q56'] = Pagos.objects.filter(pagado=True).aggregate(total=Sum('solicitud__solicitud_lugar__extras__precio'))['total']

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    wb.save(response)
    response['Content-Disposition'] = 'attachment; filename=REPORTE_SISCOMFERIA.xlsx'
    return response