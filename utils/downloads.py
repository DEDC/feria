# settings
from django.conf import settings
from django.db.models import Q
import zipfile
import os
import xlsxwriter
import io
from apps.services.models import CEGAPS, CEGAPSPolizas, ContratosEspecializados
from apps.records.models import Tiendas, Sucursales
from apps.movements.models import MovimientosMercancias

def especializados_structure():
    zf = zipfile.ZipFile(os.path.join(settings.FILE_STRUCTURE_ROOT, 'SERVICIOS_ESPECIALIZADOS.zip'), 'w')
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'strings_to_urls': False})
    gral_format = {'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': '#D9D9D9'}
    title_format = workbook.add_format(gral_format | {'font_size': 12, 'font_color': 'white', 'bg_color': '#235B4E', 'bold': True})
    cell_format = workbook.add_format(gral_format | {'font_size': 10})
    
    worksheet = workbook.add_worksheet('Servicios Especializados')
    worksheet.set_column('A1:AA1', 23)
    worksheet.set_row(0, 30)
    worksheet.write('A1', 'Sucursal', title_format)
    worksheet.write('B1', 'Unidad Operativa', title_format)
    worksheet.write('C1', 'Nombre, denominación o razón social', title_format)
    worksheet.write('D1', 'RFC', title_format)
    worksheet.write('E1', 'RP', title_format)
    worksheet.write('F1', 'Folio del Contrato', title_format)
    worksheet.write('G1', 'Fecha de inicio del Contrato', title_format)
    worksheet.write('H1', 'Fecha de conclusión del Contrato', title_format)
    worksheet.write('I1', 'Motivo del Contrato', title_format)
    worksheet.write('J1', 'Número de trabajadores', title_format)
    worksheet.write('K1', '¿El personal asignado realizó los trabajos con elementos propios del prestador de servicios?', title_format)
    worksheet.write('L1', '¿El prestador de servicios de personal es responsable de la dirección, supervisión o capacitación del personal asignado?', title_format)
    worksheet.write('M1', 'Número de Partida', title_format)
    worksheet.write('N1', 'Folio SIPRESS', title_format)
    worksheet.write('O1', 'Actividad económica especializada manifestada en REPSE', title_format)
    worksheet.write('P1', 'Folio del registro del REPSE', title_format)
    worksheet.write('Q1', 'Estatus de registro del REPSE', title_format)
    worksheet.write('R1', 'Fecha del registro del REPSE', title_format)
    worksheet.write('S1', 'Folio ICSOE', title_format)
    worksheet.write('T1', 'Folio del Contrato reportado en ICSOE', title_format)
    worksheet.write('U1', 'Fecha de presentación ICSOE', title_format)
    worksheet.write('V1', 'Archivo Contrato', title_format)
    worksheet.write('W1', 'Archivo Evidencia trimestral', title_format)
    worksheet.write('X1', 'Archivo Cuotas Obrero Patronal', title_format)
    worksheet.write('Y1', 'Archivo Opinión de cumplimiento', title_format)
    worksheet.write('Z1', 'Archivo Registro REPSE', title_format)
    worksheet.write('AA1', 'Archivo Listado de personal', title_format)
    
    contratos = ContratosEspecializados.objects.all()
    
    counter = 0
    for c in contratos:
        counter += 1
        print(counter)
        worksheet.write(counter, 0, c.unidad.sucursal.nombre, cell_format)
        worksheet.write(counter, 1, c.unidad.nombre, cell_format)
        worksheet.write(counter, 2, c.nombre, cell_format)
        worksheet.write(counter, 3, c.rfc.upper(), cell_format)
        worksheet.write(counter, 4, c.rp, cell_format)
        worksheet.write(counter, 5, c.folio_contrato.upper(), cell_format)
        worksheet.write(counter, 6, c.fecha_inicio.strftime('%d/%m/%Y'), cell_format)
        worksheet.write(counter, 7, c.fecha_fin.strftime('%d/%m/%Y'), cell_format)
        worksheet.write(counter, 8, c.motivo, cell_format)
        worksheet.write(counter, 9, c.num_trabajadores, cell_format)
        worksheet.write(counter, 10, 'Sí' if c.elementos_propios else 'No', cell_format)
        worksheet.write(counter, 11, 'Sí' if c.capacitacion else 'No', cell_format)
        worksheet.write(counter, 12, c.num_partida, cell_format)
        worksheet.write(counter, 13, c.folio_sipress, cell_format)
        worksheet.write(counter, 14, c.actividad_economica, cell_format)
        worksheet.write(counter, 15, c.folio_repse, cell_format)
        worksheet.write(counter, 16, c.estatus_repse, cell_format)
        worksheet.write(counter, 17, c.fecha_repse.strftime('%d/%m/%Y') if c.fecha_repse else '', cell_format)
        worksheet.write(counter, 18, c.folio_icsoe, cell_format)
        worksheet.write(counter, 19, c.folio_contrato_icsoe, cell_format)
        worksheet.write(counter, 20, c.fecha_icsoe.strftime('%d/%m/%Y') if c.fecha_icsoe else '', cell_format)
        
        route = os.path.join(c.unidad.sucursal.nombre.strip(), c.unidad.nombre.strip(), c.folio).upper()
        if c.contrato:
            try:
                zpath = os.path.join(route, os.path.basename(c.contrato.name))
                zf.write(c.contrato.path, zpath)
                worksheet.write_url(counter, 21, zpath, cell_format)
            except Exception as e:
                print(e)
        
        if c.evidencia_trimestral:
            try:
                zpath = os.path.join(route, os.path.basename(c.evidencia_trimestral.name))
                zf.write(c.evidencia_trimestral.path, zpath)
                worksheet.write_url(counter, 22, zpath, cell_format)
            except Exception as e:
                print(e)
        
        if c.cuotas_patronales:
            try:
                zpath = os.path.join(route, os.path.basename(c.cuotas_patronales.name))
                zf.write(c.cuotas_patronales.path, zpath)
                worksheet.write_url(counter, 23, zpath, cell_format)
            except Exception as e:
                print(e)
            
        if c.opinion_cumplimiento:
            try:
                zpath = os.path.join(route, os.path.basename(c.opinion_cumplimiento.name))
                zf.write(c.opinion_cumplimiento.path, zpath)
                worksheet.write_url(counter, 24, zpath, cell_format)
            except Exception as e:
                print(e)
        
        if c.registro_repse:
            try:
                zpath = os.path.join(route, os.path.basename(c.registro_repse.name))
                zf.write(c.registro_repse.path, zpath)
                worksheet.write_url(counter, 25, zpath, cell_format)
            except Exception as e:
                print(e)
        
        if c.listado_personal:
            try:
                zpath = os.path.join(route, os.path.basename(c.listado_personal.name))
                zf.write(c.listado_personal.path, zpath)
                worksheet.write_url(counter, 26, zpath, cell_format)
            except Exception as e:
                print(e)
    workbook.close()
    zf.writestr(f'SERVICIOS_ESPECIALIZADOS.xlsx', output.getvalue())
    zf.close()

def polizas_structure():
    zf = zipfile.ZipFile(os.path.join(settings.FILE_STRUCTURE_ROOT, 'CEGAPS_POLIZAS.zip'), 'w')
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'strings_to_urls': False})
    gral_format = {'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': '#D9D9D9'}
    title_format = workbook.add_format(gral_format | {'font_size': 12, 'font_color': 'white', 'bg_color': '#235B4E', 'bold': True})
    cell_format = workbook.add_format(gral_format | {'font_size': 10})
    cn = 0
    #cegapsf = []
    for suc in Sucursales.objects.all().order_by('nombre'):
        worksheet = workbook.add_worksheet(suc.nombre.strip())
        worksheet.set_column('A1:O1', 23)
        worksheet.set_row(0, 30)
        worksheet.write('A1', 'Sucursal', title_format)
        worksheet.write('B1', 'Clave de la Sucursal', title_format)
        worksheet.write('C1', 'Unidad Operativa', title_format)
        worksheet.write('D1', 'Clave de la Unidad Operativa', title_format)
        worksheet.write('E1', 'Folio CEGAP', title_format)
        worksheet.write('F1', 'Partida', title_format)
        worksheet.write('G1', 'Fecha', title_format)
        worksheet.write('H1', 'Tipo', title_format)
        worksheet.write('I1', 'Beneficiario', title_format)
        worksheet.write('J1', 'Concepto', title_format)
        worksheet.write('K1', 'Expediente', title_format)
        worksheet.write('L1', 'Archivo Pólizas', title_format)
        worksheet.write('M1', 'Archivo CEGAP', title_format)
        worksheet.write('N1', 'Archivo Contra Recibo', title_format)
        worksheet.write('O1', 'Archivo Constancia de Recepción', title_format)
        worksheet.write('P1', 'Archivo Comprobante Fiscal', title_format)
        worksheet.write('Q1', 'Archivo Verificación de Vigencia', title_format)
        worksheet.write('R1', 'Archivo Transferencia Electrónica', title_format)
        worksheet.write('S1', 'Archivo Comprobación', title_format)
        worksheet.write('T1', 'Requerimiento', title_format)
        lookup = ((Q(existe=False)&Q(periodo='p1')) | Q(periodo='p2'))
        cegaps = CEGAPSPolizas.objects.filter(lookup, unidad__sucursal=suc)
        
        #wb = load_workbook('search_polizas.xlsx')
        #ws2 = wb.active
        # for row in ws2.iter_rows(min_row=1):
        #     c = cegaps.filter(folio_cegap=str(row[1].value).strip())
        #     if c.exists():
        #         for f in c:
        #             cegapsf.append(f)
        
        counter = 1
        for c in cegaps:
            cn += 1
            print(cn)
            worksheet.write(counter, 0, suc.nombre, cell_format)
            worksheet.write(counter, 1, suc.clave, cell_format)
            worksheet.write(counter, 2, c.unidad.nombre, cell_format)
            worksheet.write(counter, 3, c.unidad.clave, cell_format)
            worksheet.write(counter, 4, c.folio_cegap, cell_format)
            worksheet.write(counter, 5, c.partida.clave, cell_format)
            worksheet.write(counter, 6, c.fecha, cell_format)
            worksheet.write(counter, 7, c.tipo, cell_format)
            worksheet.write(counter, 8, c.beneficiario, cell_format)
            worksheet.write(counter, 9, c.concepto, cell_format)
            worksheet.write(counter, 19, c.get_periodo_display(), cell_format)
            route = os.path.join(suc.nombre.strip(), c.unidad.nombre.strip(), c.partida.clave.strip(), c.folio_cegap.strip()).upper()
            if c.polizas.count() > 0:    
                for p in c.polizas.all():
                    worksheet.write(counter, 0, suc.nombre, cell_format)
                    worksheet.write(counter, 1, suc.clave, cell_format)
                    worksheet.write(counter, 2, c.unidad.nombre, cell_format)
                    worksheet.write(counter, 3, c.unidad.clave, cell_format)
                    worksheet.write(counter, 4, c.folio_cegap, cell_format)
                    worksheet.write(counter, 5, c.partida.clave, cell_format)
                    worksheet.write(counter, 6, c.fecha, cell_format)
                    worksheet.write(counter, 7, c.tipo, cell_format)
                    worksheet.write(counter, 8, c.beneficiario, cell_format)
                    worksheet.write(counter, 9, c.concepto, cell_format)
                    worksheet.write(counter, 19, c.get_periodo_display(), cell_format)
                    worksheet.write(counter, 10, p.folio, cell_format)
                    if p.poliza:
                        try:
                            zpath = os.path.join(route, p.folio, os.path.basename(p.poliza.name))
                            zf.write(p.poliza.path, zpath)
                            worksheet.write_url(counter, 11, zpath, cell_format)
                        except Exception as e:
                            print(e)
                        
                    if p.fcegap:
                        try:
                            zpath = os.path.join(route, p.folio, os.path.basename(p.fcegap.name))
                            zf.write(p.fcegap.path, zpath)
                            worksheet.write_url(counter, 12, zpath, cell_format)
                        except Exception as e:
                            print(e)
                    
                    if p.contrarecibo:
                        try:
                            zpath = os.path.join(route, p.folio, os.path.basename(p.contrarecibo.name))
                            zf.write(p.contrarecibo.path, zpath)
                            worksheet.write_url(counter, 13, zpath, cell_format)
                        except Exception as e:
                            print(e)
                    
                    if p.constancia_recepcion:
                        try:
                            zpath = os.path.join(route, p.folio, os.path.basename(p.constancia_recepcion.name))
                            zf.write(p.constancia_recepcion.path, zpath)
                            worksheet.write_url(counter, 14, zpath, cell_format)
                        except Exception as e:
                            print(e)
                    
                    if p.comprobante_fiscal:
                        try:
                            zpath = os.path.join(route, p.folio, os.path.basename(p.comprobante_fiscal.name))
                            zf.write(p.comprobante_fiscal.path, zpath)
                            worksheet.write_url(counter, 15, zpath, cell_format)
                        except Exception as e:
                            print(e)
                    
                    if p.verificacion_vigencia:
                        try:
                            zpath = os.path.join(route, p.folio, os.path.basename(p.verificacion_vigencia.name))
                            zf.write(p.verificacion_vigencia.path, zpath)
                            worksheet.write_url(counter, 16, zpath, cell_format)
                        except Exception as e:
                            print(e)
                    
                    if p.transferencia_electronica:
                        try:
                            zpath = os.path.join(route, p.folio, os.path.basename(p.transferencia_electronica.name))
                            zf.write(p.transferencia_electronica.path, zpath)
                            worksheet.write_url(counter, 17, zpath, cell_format)
                        except Exception as e:
                            print(e)

                    if p.comprobacion:
                        try:
                            zpath = os.path.join(route, p.folio, os.path.basename(p.comprobacion.name))
                            zf.write(p.comprobacion.path, zpath)
                            worksheet.write_url(counter, 18, zpath, cell_format)
                        except Exception as e:
                            print(e)
                    counter += 1
            else:
                counter += 1
    workbook.close()
    zf.writestr(f'CEGAPS_POLIZAS.xlsx', output.getvalue())
    zf.close()

def merca_structure():
    zf = zipfile.ZipFile(os.path.join(settings.FILE_STRUCTURE_ROOT, 'MERCANCIAS_FACTURAR.zip'), 'w')
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'strings_to_urls': False})
    gral_format = {'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': '#D9D9D9'}
    title_format = workbook.add_format(gral_format | {'font_size': 12, 'font_color': 'white', 'bg_color': '#235B4E', 'bold': True})
    cell_format = workbook.add_format(gral_format | {'font_size': 10})
    
    for suc in Sucursales.objects.all().order_by('nombre'):
        worksheet = workbook.add_worksheet(suc.nombre.strip())
        worksheet.set_column('A1:O1', 23)
        worksheet.set_row(0, 30)
        worksheet.write('A1', 'Sucursal', title_format)
        worksheet.write('B1', 'Clave de la Sucursal', title_format)
        worksheet.write('C1', 'Unidad Operativa', title_format)
        worksheet.write('D1', 'Clave de la Unidad Operativa', title_format)
        worksheet.write('E1', 'Almacén', title_format)
        worksheet.write('F1', 'Clave del Almácen', title_format)
        #
        worksheet.write('G1', 'Clave del Movimiento', title_format)
        worksheet.write('H1', 'Folio del Movimiento', title_format)
        worksheet.write('I1', 'Fecha del Movimiento', title_format)
        worksheet.write('J1', 'Canal', title_format)
        worksheet.write('K1', 'Número de Orden', title_format)
        # 
        worksheet.write('L1', 'Archivo Movimiento', title_format)
        worksheet.write('M1', 'Aplica para Vales', title_format)
        worksheet.write('N1', 'Archivo Vales', title_format)
        worksheet.write('O1', 'Archivo Devolución', title_format)
        
        movs = MovimientosMercancias.objects.filter(activo=True, unidad__sucursal=suc)

        counter = 1
        for m in movs:
            worksheet.write(counter, 0, suc.nombre, cell_format)
            worksheet.write_number(counter, 1, int(suc.clave), cell_format)
            worksheet.write(counter, 2, m.unidad.nombre, cell_format)
            worksheet.write_number(counter, 3, int(m.unidad.clave), cell_format)
            worksheet.write(counter, 4, m.almacen.nombre, cell_format)
            worksheet.write_number(counter, 5, int(m.almacen.clave), cell_format)
            worksheet.write_number(counter, 6, int(m.clave), cell_format)
            worksheet.write_number(counter, 7, int(m.folio_doc), cell_format)
            worksheet.write(counter, 8, m.fecha, cell_format)
            worksheet.write(counter, 9, m.canal, cell_format)
            worksheet.write_number(counter, 10, int(m.orden), cell_format)
            worksheet.write(counter, 12, 'No' if m.no_vales else 'Sí', cell_format)
            route = os.path.join(suc.nombre.strip(), m.unidad.nombre.strip(), m.almacen.nombre.strip(), f'MOV_{m.clave}').upper()
            if m.archivo:
                try:
                    name, extension = os.path.splitext(m.archivo.name)
                    zpath = os.path.join(route, f'TXT_{m.folio[:12]}_{m.folio_doc}{extension}')
                    # zf.write(m.archivo.path, zpath)
                    worksheet.write_url(counter, 11, zpath, cell_format)
                except Exception as e:
                    print(e)
            if not m.no_vales:
                if m.vales:    
                    try:
                        name, extension = os.path.splitext(m.vales.name)
                        zpath = os.path.join(route, f'VALE_{m.folio[:12]}_{m.folio_doc}{extension}')
                        # zf.write(m.vales.path, zpath)
                        worksheet.write_url(counter, 13, zpath, cell_format)
                    except Exception as e:
                        print(e)
                if m.archivo_dos:
                    try:
                        name, extension = os.path.splitext(m.archivo_dos.name)
                        zpath = os.path.join(route, f'DEVOLUCION_{m.folio[:12]}_{m.folio_doc}{extension}')
                        # zf.write(m.archivo_dos.path, zpath)
                        worksheet.write_url(counter, 14, zpath, cell_format)
                    except Exception as e:
                        print(e)
            counter += 1
    workbook.close()
    zf.writestr(f'MERCANCIAS_FACTURAR.xlsx', output.getvalue())
    zf.close()

def records_structure2():
    zf = zipfile.ZipFile(os.path.join(settings.FILE_STRUCTURE_ROOT, 'EXPEDIENTE_TIENDAS.zip'), 'w')
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'strings_to_urls': False})
    gral_format = {'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': '#D9D9D9'}
    title_format = workbook.add_format(gral_format | {'font_size': 12, 'font_color': 'white', 'bg_color': '#235B4E', 'bold': True})
    cell_format = workbook.add_format(gral_format | {'font_size': 10})
    
    for suc in Sucursales.objects.all().order_by('nombre'):
        print(suc.nombre)
        worksheet = workbook.add_worksheet(suc.nombre.strip())
        worksheet.write('A1', 'Sucursal', title_format)
        worksheet.write('B1', 'Clave de la Sucursal', title_format)
        worksheet.write('C1', 'Unidad Operativa', title_format)
        worksheet.write('D1', 'Clave de la Unidad Operativa', title_format)
        worksheet.write('E1', 'Almacén', title_format)
        worksheet.write('F1', 'Clave del Almácen', title_format)
        worksheet.write('G1', 'Clave de Tienda', title_format)
        
        stores = Tiendas.objects.filter(operacion=False, almacen__unidad__sucursal=suc).order_by('almacen')
        max_row = 0
        
        # -------------
        last_row = 7
        # counter = 1
        # for store in stores:
        #     worksheet.write(counter, 0, store.almacen.unidad.sucursal.nombre, cell_format)
        #     worksheet.write_number(counter, 1, int(store.almacen.unidad.sucursal.clave), cell_format)
        #     worksheet.write(counter, 2, store.almacen.unidad.nombre, cell_format)
        #     worksheet.write_number(counter, 3, int(store.almacen.unidad.clave), cell_format)
        #     worksheet.write(counter, 4, store.almacen.nombre, cell_format)
        #     worksheet.write_number(counter, 5, int(store.almacen.clave), cell_format)
        #     worksheet.write_number(counter, 6, int(store.clave) if store.clave else 0, cell_format)
        #     exp = store.exp.first()
            
        #     if exp is not None:
        #         counter_sap = last_row
        #         for tr in exp.solicitudes_apertura.all():
        #             worksheet.write(0, counter_sap, 'Solicitud de Apertura de Tienda Comunitaria', title_format)
        #             if tr.archivo:
        #                 name, extension = os.path.splitext(tr.archivo.name)
        #                 root = os.path.join(store.almacen.unidad.sucursal.nombre.strip(), store.almacen.unidad.nombre.strip(), store.almacen.nombre.strip(), store.clave.strip(), f'{name}{extension}').upper()
        #                 try:
        #                     zf.write(tr.archivo.path, root)
        #                     worksheet.write_url(counter, counter_sap, root, cell_format)
        #                 except Exception as e:
        #                     print(e)
        #             counter_sap += 1
        #         if counter_sap > max_row:
        #             max_row = counter_sap
        #     counter += 1
        # -------------
        # last_row = max_row
        # counter = 1
        # for store in stores:
        #     worksheet.write(counter, 0, store.almacen.unidad.sucursal.nombre, cell_format)
        #     worksheet.write_number(counter, 1, int(store.almacen.unidad.sucursal.clave), cell_format)
        #     worksheet.write(counter, 2, store.almacen.unidad.nombre, cell_format)
        #     worksheet.write_number(counter, 3, int(store.almacen.unidad.clave), cell_format)
        #     worksheet.write(counter, 4, store.almacen.nombre, cell_format)
        #     worksheet.write_number(counter, 5, int(store.almacen.clave), cell_format)
        #     worksheet.write_number(counter, 6, int(store.clave) if store.clave else 0, cell_format)
        #     exp = store.exp.first()
            
        #     if exp is not None:
        #         counter_eap = last_row
        #         for tr in exp.estudios_apertura.all():
        #             worksheet.write(0, counter_eap, 'Estudio Socioeconómico de Apertura', title_format)
        #             if tr.archivo:
        #                 name, extension = os.path.splitext(tr.archivo.name)
        #                 root = os.path.join(store.almacen.unidad.sucursal.nombre.strip(), store.almacen.unidad.nombre.strip(), store.almacen.nombre.strip(), store.clave.strip(), f'{name}{extension}').upper()
        #                 try:
        #                     zf.write(tr.archivo.path, root)
        #                     worksheet.write_url(counter, counter_eap, root, cell_format)
        #                 except Exception as e:
        #                     print(e)
        #             counter_eap += 1
        #         if counter_eap > max_row:
        #             max_row = counter_eap
        #     counter += 1
        # --------------
        # last_row = max_row
        # counter = 1
        # for store in stores:
        #     worksheet.write(counter, 0, store.almacen.unidad.sucursal.nombre, cell_format)
        #     worksheet.write_number(counter, 1, int(store.almacen.unidad.sucursal.clave), cell_format)
        #     worksheet.write(counter, 2, store.almacen.unidad.nombre, cell_format)
        #     worksheet.write_number(counter, 3, int(store.almacen.unidad.clave), cell_format)
        #     worksheet.write(counter, 4, store.almacen.nombre, cell_format)
        #     worksheet.write_number(counter, 5, int(store.almacen.clave), cell_format)
        #     worksheet.write_number(counter, 6, int(store.clave) if store.clave else 0, cell_format)
        #     exp = store.exp.first()
            
        #     if exp is not None:
        #         counter_aia = last_row
        #         for tr in exp.actas_informativas_apertura.all():
        #             worksheet.write(0, counter_aia, 'Acta de Asamblea Informativa de Apertura', title_format)
        #             if tr.archivo:
        #                 name, extension = os.path.splitext(tr.archivo.name)
        #                 root = os.path.join(store.almacen.unidad.sucursal.nombre.strip(), store.almacen.unidad.nombre.strip(), store.almacen.nombre.strip(), store.clave.strip(), f'{name}{extension}').upper()
        #                 try:
        #                     zf.write(tr.archivo.path, root)
        #                     worksheet.write_url(counter, counter_aia, root, cell_format)
        #                 except Exception as e:
        #                     print(e)
        #             counter_aia += 1
        #         if counter_aia > max_row:
        #             max_row = counter_aia
        #     counter += 1
        # # --------------
        # last_row = max_row
        # counter = 1
        # for store in stores:
        #     worksheet.write(counter, 0, store.almacen.unidad.sucursal.nombre, cell_format)
        #     worksheet.write_number(counter, 1, int(store.almacen.unidad.sucursal.clave), cell_format)
        #     worksheet.write(counter, 2, store.almacen.unidad.nombre, cell_format)
        #     worksheet.write_number(counter, 3, int(store.almacen.unidad.clave), cell_format)
        #     worksheet.write(counter, 4, store.almacen.nombre, cell_format)
        #     worksheet.write_number(counter, 5, int(store.almacen.clave), cell_format)
        #     worksheet.write_number(counter, 6, int(store.clave) if store.clave else 0, cell_format)
        #     exp = store.exp.first()
            
        #     if exp is not None:
        #         counter_aca = last_row
        #         for tr in exp.actas_constitutivas_apertura.all():
        #             worksheet.write(0, counter_aca, 'Acta de Asamblea Constitutiva de Apertura', title_format)
        #             if tr.archivo:
        #                 name, extension = os.path.splitext(tr.archivo.name)
        #                 root = os.path.join(store.almacen.unidad.sucursal.nombre.strip(), store.almacen.unidad.nombre.strip(), store.almacen.nombre.strip(), store.clave.strip(), f'{name}{extension}').upper()
        #                 try:
        #                     zf.write(tr.archivo.path, root)
        #                     worksheet.write_url(counter, counter_aca, root, cell_format)
        #                 except Exception as e:
        #                     print(e)
        #             counter_aca += 1
        #         if counter_aca > max_row:
        #             max_row = counter_aca
        #     counter += 1
        # --------------
        # last_row = max_row
        # counter = 1
        # for store in stores:
        #     worksheet.write(counter, 0, store.almacen.unidad.sucursal.nombre, cell_format)
        #     worksheet.write_number(counter, 1, int(store.almacen.unidad.sucursal.clave), cell_format)
        #     worksheet.write(counter, 2, store.almacen.unidad.nombre, cell_format)
        #     worksheet.write_number(counter, 3, int(store.almacen.unidad.clave), cell_format)
        #     worksheet.write(counter, 4, store.almacen.nombre, cell_format)
        #     worksheet.write_number(counter, 5, int(store.almacen.clave), cell_format)
        #     worksheet.write_number(counter, 6, int(store.clave) if store.clave else 0, cell_format)
        #     exp = store.exp.first()
            
        #     if exp is not None:
        #         counter_aap = last_row
        #         for tr in exp.autorizaciones_apertura.all():
        #             worksheet.write(0, counter_aap, 'Oficio de autorización de la Apertura de Tienda Comunitaria', title_format)
        #             if tr.archivo:
        #                 name, extension = os.path.splitext(tr.archivo.name)
        #                 root = os.path.join(store.almacen.unidad.sucursal.nombre.strip(), store.almacen.unidad.nombre.strip(), store.almacen.nombre.strip(), store.clave.strip(), f'{name}{extension}').upper()
        #                 try:
        #                     zf.write(tr.archivo.path, root)
        #                     worksheet.write_url(counter, counter_aap, root, cell_format)
        #                 except Exception as e:
        #                     print(e)
        #             counter_aap += 1
        #         if counter_aap > max_row:
        #             max_row = counter_aap
        #     counter += 1
        # --------------
        # last_row = max_row
        # counter = 1
        # for store in stores:
        #     worksheet.write(counter, 0, store.almacen.unidad.sucursal.nombre, cell_format)
        #     worksheet.write_number(counter, 1, int(store.almacen.unidad.sucursal.clave), cell_format)
        #     worksheet.write(counter, 2, store.almacen.unidad.nombre, cell_format)
        #     worksheet.write_number(counter, 3, int(store.almacen.unidad.clave), cell_format)
        #     worksheet.write(counter, 4, store.almacen.nombre, cell_format)
        #     worksheet.write_number(counter, 5, int(store.almacen.clave), cell_format)
        #     worksheet.write_number(counter, 6, int(store.clave) if store.clave else 0, cell_format)
        #     exp = store.exp.first()
            
        #     if exp is not None:
        #         counter_ace = last_row
        #         for tr in exp.actas.all():
        #             worksheet.write(0, counter_ace, 'Actas de Entrega de Capital de Trabajo', title_format)
        #             if tr.archivo:
        #                 name, extension = os.path.splitext(tr.archivo.name)
        #                 root = os.path.join(store.almacen.unidad.sucursal.nombre.strip(), store.almacen.unidad.nombre.strip(), store.almacen.nombre.strip(), store.clave.strip(), f'{name}{extension}').upper()
        #                 try:
        #                     zf.write(tr.archivo.path, root)
        #                     worksheet.write_url(counter, counter_ace, root, cell_format)
        #                 except Exception as e:
        #                     print(e)
        #             counter_ace += 1
        #         if counter_ace > max_row:
        #             max_row = counter_ace
        #     counter += 1
        # --------------
        # last_row = max_row
        # counter = 1
        # for store in stores:
        #     worksheet.write(counter, 0, store.almacen.unidad.sucursal.nombre, cell_format)
        #     worksheet.write_number(counter, 1, int(store.almacen.unidad.sucursal.clave), cell_format)
        #     worksheet.write(counter, 2, store.almacen.unidad.nombre, cell_format)
        #     worksheet.write_number(counter, 3, int(store.almacen.unidad.clave), cell_format)
        #     worksheet.write(counter, 4, store.almacen.nombre, cell_format)
        #     worksheet.write_number(counter, 5, int(store.almacen.clave), cell_format)
        #     worksheet.write_number(counter, 6, int(store.clave) if store.clave else 0, cell_format)
        #     exp = store.exp.first()
            
        #     if exp is not None:
        #         counter_tre = last_row
        #         for tr in exp.transferencias_enviadas.all():
        #             worksheet.write(0, counter_tre, 'Comprobante de la Transferencia Enviada a la Tienda Comunitaria por Concepto de Capital de Trabajo', title_format)
        #             if tr.archivo:
        #                 name, extension = os.path.splitext(tr.archivo.name)
        #                 root = os.path.join(store.almacen.unidad.sucursal.nombre.strip(), store.almacen.unidad.nombre.strip(), store.almacen.nombre.strip(), store.clave.strip(), f'{name}{extension}').upper()
        #                 try:
        #                     zf.write(tr.archivo.path, root)
        #                     worksheet.write_url(counter, counter_tre, root, cell_format)
        #                 except Exception as e:
        #                     print(e)
        #             counter_tre += 1
        #         if counter_tre > max_row:
        #             max_row = counter_tre
        #     counter += 1
        # --------------
        # last_row = max_row
        # counter = 1
        # for store in stores:
        #     worksheet.write(counter, 0, store.almacen.unidad.sucursal.nombre, cell_format)
        #     worksheet.write_number(counter, 1, int(store.almacen.unidad.sucursal.clave), cell_format)
        #     worksheet.write(counter, 2, store.almacen.unidad.nombre, cell_format)
        #     worksheet.write_number(counter, 3, int(store.almacen.unidad.clave), cell_format)
        #     worksheet.write(counter, 4, store.almacen.nombre, cell_format)
        #     worksheet.write_number(counter, 5, int(store.almacen.clave), cell_format)
        #     worksheet.write_number(counter, 6, int(store.clave) if store.clave else 0, cell_format)
        #     exp = store.exp.first()
            
        #     if exp is not None:
        #         counter_trf = last_row
        #         for tr in exp.transfers.all():
        #             worksheet.write(0, counter_trf, 'Comprobante de la Transferencia Recibida por la Tienda Comunitaria por Concepto de Capital de Trabajo', title_format)
        #             if tr.archivo:
        #                 name, extension = os.path.splitext(tr.archivo.name)
        #                 root = os.path.join(store.almacen.unidad.sucursal.nombre.strip(), store.almacen.unidad.nombre.strip(), store.almacen.nombre.strip(), store.clave.strip(), f'{name}{extension}').upper()
        #                 try:
        #                     zf.write(tr.archivo.path, root)
        #                     worksheet.write_url(counter, counter_trf, root, cell_format)
        #                 except Exception as e:
        #                     print(e)
        #             counter_trf += 1
        #         if counter_trf > max_row:
        #             max_row = counter_trf
        #     counter += 1
        # --------------
        # last_row = max_row
        counter = 1
        for store in stores:
            worksheet.write(counter, 0, store.almacen.unidad.sucursal.nombre, cell_format)
            worksheet.write_number(counter, 1, int(store.almacen.unidad.sucursal.clave), cell_format)
            worksheet.write(counter, 2, store.almacen.unidad.nombre, cell_format)
            worksheet.write_number(counter, 3, int(store.almacen.unidad.clave), cell_format)
            worksheet.write(counter, 4, store.almacen.nombre, cell_format)
            worksheet.write_number(counter, 5, int(store.almacen.clave), cell_format)
            worksheet.write_number(counter, 6, int(store.clave) if store.clave else 0, cell_format)
            exp = store.exp.first()
            
            if exp is not None:
                counter_pge = last_row
                for tr in exp.pagares.all():
                    worksheet.write(0, counter_pge, 'Pagaré Vigente que Ampara el Capital de Trabajo', title_format)
                    if tr.archivo:
                        name, extension = os.path.splitext(tr.archivo.name)
                        root = os.path.join(store.almacen.unidad.sucursal.nombre.strip(), store.almacen.unidad.nombre.strip(), store.almacen.nombre.strip(), store.clave.strip(), f'{name}{extension}').upper()
                        try:
                            zf.write(tr.archivo.path, root)
                            worksheet.write_url(counter, counter_pge, root, cell_format)
                        except Exception as e:
                            print(e)
                    counter_pge += 1
                if counter_pge > max_row:
                    max_row = counter_pge
            counter += 1
        # --------------
        # last_row = max_row
        # counter = 1
        # for store in stores:
        #     worksheet.write(counter, 0, store.almacen.unidad.sucursal.nombre, cell_format)
        #     worksheet.write_number(counter, 1, int(store.almacen.unidad.sucursal.clave), cell_format)
        #     worksheet.write(counter, 2, store.almacen.unidad.nombre, cell_format)
        #     worksheet.write_number(counter, 3, int(store.almacen.unidad.clave), cell_format)
        #     worksheet.write(counter, 4, store.almacen.nombre, cell_format)
        #     worksheet.write_number(counter, 5, int(store.almacen.clave), cell_format)
        #     worksheet.write_number(counter, 6, int(store.clave) if store.clave else 0, cell_format)
        #     exp = store.exp.first()
            
        #     if exp is not None:
        #         counter_ccp = last_row
        #         for tr in exp.constancias_capacitacion.all():
        #             worksheet.write(0, counter_ccp, 'Constancias de Capacitación', title_format)
        #             if tr.archivo:
        #                 name, extension = os.path.splitext(tr.archivo.name)
        #                 root = os.path.join(store.almacen.unidad.sucursal.nombre.strip(), store.almacen.unidad.nombre.strip(), store.almacen.nombre.strip(), store.clave.strip(), f'{name}{extension}').upper()
        #                 try:
        #                     zf.write(tr.archivo.path, root)
        #                     worksheet.write_url(counter, counter_ccp, root, cell_format)
        #                 except Exception as e:
        #                     print(e)
        #             counter_ccp += 1
        #         if counter_ccp > max_row:
        #             max_row = counter_ccp
        #     counter += 1
        # --------------
        # last_row = max_row
        # counter = 1
        # for store in stores:
        #     worksheet.write(counter, 0, store.almacen.unidad.sucursal.nombre, cell_format)
        #     worksheet.write_number(counter, 1, int(store.almacen.unidad.sucursal.clave), cell_format)
        #     worksheet.write(counter, 2, store.almacen.unidad.nombre, cell_format)
        #     worksheet.write_number(counter, 3, int(store.almacen.unidad.clave), cell_format)
        #     worksheet.write(counter, 4, store.almacen.nombre, cell_format)
        #     worksheet.write_number(counter, 5, int(store.almacen.clave), cell_format)
        #     worksheet.write_number(counter, 6, int(store.clave) if store.clave else 0, cell_format)
        #     exp = store.exp.first()
            
        #     if exp is not None:
        #         counter_pme = last_row
        #         for tr in exp.planos_mercancias.all():
        #             worksheet.write(0, counter_pme, 'Plano de Ubicación de Mercancías', title_format)
        #             if tr.archivo:
        #                 name, extension = os.path.splitext(tr.archivo.name)
        #                 root = os.path.join(store.almacen.unidad.sucursal.nombre.strip(), store.almacen.unidad.nombre.strip(), store.almacen.nombre.strip(), store.clave.strip(), f'{name}{extension}').upper()
        #                 try:
        #                     zf.write(tr.archivo.path, root)
        #                     worksheet.write_url(counter, counter_pme, root, cell_format)
        #                 except Exception as e:
        #                     print(e)
        #             counter_pme += 1
        #         if counter_pme > max_row:
        #             max_row = counter_pme
        #     counter += 1
        # --------------
        # last_row = max_row
        # counter = 1
        # for store in stores:
        #     worksheet.write(counter, 0, store.almacen.unidad.sucursal.nombre, cell_format)
        #     worksheet.write_number(counter, 1, int(store.almacen.unidad.sucursal.clave), cell_format)
        #     worksheet.write(counter, 2, store.almacen.unidad.nombre, cell_format)
        #     worksheet.write_number(counter, 3, int(store.almacen.unidad.clave), cell_format)
        #     worksheet.write(counter, 4, store.almacen.nombre, cell_format)
        #     worksheet.write_number(counter, 5, int(store.almacen.clave), cell_format)
        #     worksheet.write_number(counter, 6, int(store.clave) if store.clave else 0, cell_format)
        #     exp = store.exp.first()
            
        #     if exp is not None:
        #         counter_cpd = last_row
        #         for tr in exp.comprobantes_domicilio.all():
        #             worksheet.write(0, counter_cpd, 'Comprobante de Domicilio de la Tienda', title_format)
        #             if tr.archivo:
        #                 name, extension = os.path.splitext(tr.archivo.name)
        #                 root = os.path.join(store.almacen.unidad.sucursal.nombre.strip(), store.almacen.unidad.nombre.strip(), store.almacen.nombre.strip(), store.clave.strip(), f'{name}{extension}').upper()
        #                 try:
        #                     zf.write(tr.archivo.path, root)
        #                     worksheet.write_url(counter, counter_cpd, root, cell_format)
        #                 except Exception as e:
        #                     print(e)
        #             counter_cpd += 1
        #         if counter_cpd > max_row:
        #             max_row = counter_cpd
        #     counter += 1
        # --------------
        # last_row = max_row
        # counter = 1
        # for store in stores:
        #     worksheet.write(counter, 0, store.almacen.unidad.sucursal.nombre, cell_format)
        #     worksheet.write_number(counter, 1, int(store.almacen.unidad.sucursal.clave), cell_format)
        #     worksheet.write(counter, 2, store.almacen.unidad.nombre, cell_format)
        #     worksheet.write_number(counter, 3, int(store.almacen.unidad.clave), cell_format)
        #     worksheet.write(counter, 4, store.almacen.nombre, cell_format)
        #     worksheet.write_number(counter, 5, int(store.almacen.clave), cell_format)
        #     worksheet.write_number(counter, 6, int(store.clave) if store.clave else 0, cell_format)
        #     exp = store.exp.first()
            
        #     if exp is not None:
        #         counter_iof = last_row
        #         for tr in exp.identificaciones_oficiales.all():
        #             worksheet.write(0, counter_iof, 'Identificación Oficial de la Persona Encargada de la Tienda Comunitaria y de los Integrantes del Comité de Abasto', title_format)
        #             if tr.archivo:
        #                 name, extension = os.path.splitext(tr.archivo.name)
        #                 root = os.path.join(store.almacen.unidad.sucursal.nombre.strip(), store.almacen.unidad.nombre.strip(), store.almacen.nombre.strip(), store.clave.strip(), f'{name}{extension}').upper()
        #                 try:
        #                     zf.write(tr.archivo.path, root)
        #                     worksheet.write_url(counter, counter_iof, root, cell_format)
        #                 except Exception as e:
        #                     print(e)
        #             counter_iof += 1
        #         if counter_iof > max_row:
        #             max_row = counter_iof
        #     counter += 1
        # --------------
        last_row = max_row
        counter = 1
        for store in stores:
            worksheet.write(counter, 0, store.almacen.unidad.sucursal.nombre, cell_format)
            worksheet.write_number(counter, 1, int(store.almacen.unidad.sucursal.clave), cell_format)
            worksheet.write(counter, 2, store.almacen.unidad.nombre, cell_format)
            worksheet.write_number(counter, 3, int(store.almacen.unidad.clave), cell_format)
            worksheet.write(counter, 4, store.almacen.nombre, cell_format)
            worksheet.write_number(counter, 5, int(store.almacen.clave), cell_format)
            worksheet.write_number(counter, 6, int(store.clave) if store.clave else 0, cell_format)
            exp = store.exp.first()
            
            if exp is not None:
                counter_acr = last_row
                for tr in exp.autorizaciones_cierre.all():
                    worksheet.write(0, counter_acr, 'Autorización de Cierre de Tienda Comunitaria', title_format)
                    if tr.archivo:
                        name, extension = os.path.splitext(tr.archivo.name)
                        root = os.path.join(store.almacen.unidad.sucursal.nombre.strip(), store.almacen.unidad.nombre.strip(), store.almacen.nombre.strip(), store.clave.strip(), f'{name}{extension}').upper()
                        try:
                            zf.write(tr.archivo.path, root)
                            worksheet.write_url(counter, counter_acr, root, cell_format)
                        except Exception as e:
                            print(e)
                    counter_acr += 1
                if counter_acr > max_row:
                    max_row = counter_acr
            counter += 1
        # --------------
        last_row = max_row
        counter = 1
        for store in stores:
            worksheet.write(counter, 0, store.almacen.unidad.sucursal.nombre, cell_format)
            worksheet.write_number(counter, 1, int(store.almacen.unidad.sucursal.clave), cell_format)
            worksheet.write(counter, 2, store.almacen.unidad.nombre, cell_format)
            worksheet.write_number(counter, 3, int(store.almacen.unidad.clave), cell_format)
            worksheet.write(counter, 4, store.almacen.nombre, cell_format)
            worksheet.write_number(counter, 5, int(store.almacen.clave), cell_format)
            worksheet.write_number(counter, 6, int(store.clave) if store.clave else 0, cell_format)
            exp = store.exp.first()
            
            if exp is not None:
                counter_aud = last_row
                for tr in exp.auditorias.all():
                    worksheet.write(0, counter_aud, 'Auditoría por Cierre de Tienda Comunitaria e inventario de mercancías', title_format)
                    if tr.archivo:
                        name, extension = os.path.splitext(tr.archivo.name)
                        root = os.path.join(store.almacen.unidad.sucursal.nombre.strip(), store.almacen.unidad.nombre.strip(), store.almacen.nombre.strip(), store.clave.strip(), f'{name}{extension}').upper()
                        try:
                            zf.write(tr.archivo.path, root)
                            worksheet.write_url(counter, counter_aud, root, cell_format)
                        except Exception as e:
                            print(e)
                    counter_aud += 1
                if counter_aud > max_row:
                    max_row = counter_aud
            counter += 1
        # --------------
        last_row = max_row
        counter = 1
        for store in stores:
            worksheet.write(counter, 0, store.almacen.unidad.sucursal.nombre, cell_format)
            worksheet.write_number(counter, 1, int(store.almacen.unidad.sucursal.clave), cell_format)
            worksheet.write(counter, 2, store.almacen.unidad.nombre, cell_format)
            worksheet.write_number(counter, 3, int(store.almacen.unidad.clave), cell_format)
            worksheet.write(counter, 4, store.almacen.nombre, cell_format)
            worksheet.write_number(counter, 5, int(store.almacen.clave), cell_format)
            worksheet.write_number(counter, 6, int(store.clave) if store.clave else 0, cell_format)
            exp = store.exp.first()
            
            if exp is not None:
                counter_tkt = last_row
                for tr in exp.tickets.all():
                    worksheet.write(0, counter_tkt, 'Ticket de Cobranza y comprobantes autorizados', title_format)
                    if tr.archivo:
                        name, extension = os.path.splitext(tr.archivo.name)
                        root = os.path.join(store.almacen.unidad.sucursal.nombre.strip(), store.almacen.unidad.nombre.strip(), store.almacen.nombre.strip(), store.clave.strip(), f'{name}{extension}').upper()
                        try:
                            zf.write(tr.archivo.path, root)
                            worksheet.write_url(counter, counter_tkt, root, cell_format)
                        except Exception as e:
                            print(e)
                    counter_tkt += 1
                if counter_tkt > max_row:
                    max_row = counter_tkt
            counter += 1
        # --------------
        last_row = max_row
        counter = 1
        for store in stores:
            worksheet.write(counter, 0, store.almacen.unidad.sucursal.nombre, cell_format)
            worksheet.write_number(counter, 1, int(store.almacen.unidad.sucursal.clave), cell_format)
            worksheet.write(counter, 2, store.almacen.unidad.nombre, cell_format)
            worksheet.write_number(counter, 3, int(store.almacen.unidad.clave), cell_format)
            worksheet.write(counter, 4, store.almacen.nombre, cell_format)
            worksheet.write_number(counter, 5, int(store.almacen.clave), cell_format)
            worksheet.write_number(counter, 6, int(store.clave) if store.clave else 0, cell_format)
            exp = store.exp.first()
            
            if exp is not None:
                counter_acn = last_row
                for tr in exp.activos_cancelados.all():
                    worksheet.write(0, counter_acn, 'Resguardo de Activos Cancelados', title_format)
                    if tr.archivo:
                        name, extension = os.path.splitext(tr.archivo.name)
                        root = os.path.join(store.almacen.unidad.sucursal.nombre.strip(), store.almacen.unidad.nombre.strip(), store.almacen.nombre.strip(), store.clave.strip(), f'{name}{extension}').upper()
                        try:
                            zf.write(tr.archivo.path, root)
                            worksheet.write_url(counter, counter_acn, root, cell_format)
                        except Exception as e:
                            print(e)
                    counter_acn += 1
                if counter_acn > max_row:
                    max_row = counter_acn
            counter += 1
        # --------------
        last_row = max_row
        counter = 1
        for store in stores:
            worksheet.write(counter, 0, store.almacen.unidad.sucursal.nombre, cell_format)
            worksheet.write_number(counter, 1, int(store.almacen.unidad.sucursal.clave), cell_format)
            worksheet.write(counter, 2, store.almacen.unidad.nombre, cell_format)
            worksheet.write_number(counter, 3, int(store.almacen.unidad.clave), cell_format)
            worksheet.write(counter, 4, store.almacen.nombre, cell_format)
            worksheet.write_number(counter, 5, int(store.almacen.clave), cell_format)
            worksheet.write_number(counter, 6, int(store.clave) if store.clave else 0, cell_format)
            exp = store.exp.first()
            
            if exp is not None:
                counter_fct = last_row
                for tr in exp.facturas.all():
                    worksheet.write(0, counter_fct, 'Facturas', title_format)
                    if tr.archivo:
                        name, extension = os.path.splitext(tr.archivo.name)
                        root = os.path.join(store.almacen.unidad.sucursal.nombre.strip(), store.almacen.unidad.nombre.strip(), store.almacen.nombre.strip(), store.clave.strip(), f'{name}{extension}').upper()
                        try:
                            zf.write(tr.archivo.path, root)
                            worksheet.write_url(counter, counter_fct, root, cell_format)
                        except Exception as e:
                            print(e)
                    counter_fct += 1
                if counter_fct > max_row:
                    max_row = counter_fct
            counter += 1
        # --------------
        last_row = max_row
        counter = 1
        for store in stores:
            worksheet.write(counter, 0, store.almacen.unidad.sucursal.nombre, cell_format)
            worksheet.write_number(counter, 1, int(store.almacen.unidad.sucursal.clave), cell_format)
            worksheet.write(counter, 2, store.almacen.unidad.nombre, cell_format)
            worksheet.write_number(counter, 3, int(store.almacen.unidad.clave), cell_format)
            worksheet.write(counter, 4, store.almacen.nombre, cell_format)
            worksheet.write_number(counter, 5, int(store.almacen.clave), cell_format)
            worksheet.write_number(counter, 6, int(store.clave) if store.clave else 0, cell_format)
            exp = store.exp.first()
            
            if exp is not None:
                counter_dvt = last_row
                for tr in exp.devoluciones_venta.all():
                    worksheet.write(0, counter_dvt, 'Devolución sobre la Venta', title_format)
                    if tr.archivo:
                        name, extension = os.path.splitext(tr.archivo.name)
                        root = os.path.join(store.almacen.unidad.sucursal.nombre.strip(), store.almacen.unidad.nombre.strip(), store.almacen.nombre.strip(), store.clave.strip(), f'{name}{extension}').upper()
                        try:
                            zf.write(tr.archivo.path, root)
                            worksheet.write_url(counter, counter_dvt, root, cell_format)
                        except Exception as e:
                            print(e)
                    counter_dvt += 1
                if counter_dvt > max_row:
                    max_row = counter_dvt
            counter += 1
        # --------------
        last_row = max_row
        counter = 1
        for store in stores:
            worksheet.write(counter, 0, store.almacen.unidad.sucursal.nombre, cell_format)
            worksheet.write_number(counter, 1, int(store.almacen.unidad.sucursal.clave), cell_format)
            worksheet.write(counter, 2, store.almacen.unidad.nombre, cell_format)
            worksheet.write_number(counter, 3, int(store.almacen.unidad.clave), cell_format)
            worksheet.write(counter, 4, store.almacen.nombre, cell_format)
            worksheet.write_number(counter, 5, int(store.almacen.clave), cell_format)
            worksheet.write_number(counter, 6, int(store.clave) if store.clave else 0, cell_format)
            exp = store.exp.first()
            
            if exp is not None:
                counter_aac = last_row
                for tr in exp.actas_admin_cierre.all():
                    worksheet.write(0, counter_aac, 'Acta Administrativa por Cierre de Tienda Comunitaria', title_format)
                    if tr.archivo:
                        name, extension = os.path.splitext(tr.archivo.name)
                        root = os.path.join(store.almacen.unidad.sucursal.nombre.strip(), store.almacen.unidad.nombre.strip(), store.almacen.nombre.strip(), store.clave.strip(), f'{name}{extension}').upper()
                        try:
                            zf.write(tr.archivo.path, root)
                            worksheet.write_url(counter, counter_aac, root, cell_format)
                        except Exception as e:
                            print(e)
                    counter_aac += 1
                if counter_aac > max_row:
                    max_row = counter_aac
            counter += 1
        # --------------
        last_row = max_row
        counter = 1
        for store in stores:
            worksheet.write(counter, 0, store.almacen.unidad.sucursal.nombre, cell_format)
            worksheet.write_number(counter, 1, int(store.almacen.unidad.sucursal.clave), cell_format)
            worksheet.write(counter, 2, store.almacen.unidad.nombre, cell_format)
            worksheet.write_number(counter, 3, int(store.almacen.unidad.clave), cell_format)
            worksheet.write(counter, 4, store.almacen.nombre, cell_format)
            worksheet.write_number(counter, 5, int(store.almacen.clave), cell_format)
            worksheet.write_number(counter, 6, int(store.clave) if store.clave else 0, cell_format)
            exp = store.exp.first()
            
            if exp is not None:
                counter_aic = last_row
                for tr in exp.actas_informativas_cierre.all():
                    worksheet.write(0, counter_aic, 'Acta de Asamblea Informativa por Cierre de Tienda Comunitaria', title_format)
                    if tr.archivo:
                        name, extension = os.path.splitext(tr.archivo.name)
                        root = os.path.join(store.almacen.unidad.sucursal.nombre.strip(), store.almacen.unidad.nombre.strip(), store.almacen.nombre.strip(), store.clave.strip(), f'{name}{extension}').upper()
                        try:
                            zf.write(tr.archivo.path, root)
                            worksheet.write_url(counter, counter_aic, root, cell_format)
                        except Exception as e:
                            print(e)
                    counter_aic += 1
                if counter_aic > max_row:
                    max_row = counter_aic
            counter += 1
        # --------------
        last_row = max_row
        counter = 1
        for store in stores:
            worksheet.write(counter, 0, store.almacen.unidad.sucursal.nombre, cell_format)
            worksheet.write_number(counter, 1, int(store.almacen.unidad.sucursal.clave), cell_format)
            worksheet.write(counter, 2, store.almacen.unidad.nombre, cell_format)
            worksheet.write_number(counter, 3, int(store.almacen.unidad.clave), cell_format)
            worksheet.write(counter, 4, store.almacen.nombre, cell_format)
            worksheet.write_number(counter, 5, int(store.almacen.clave), cell_format)
            worksheet.write_number(counter, 6, int(store.clave) if store.clave else 0, cell_format)
            exp = store.exp.first()
            
            if exp is not None:
                counter_btc = last_row
                for tr in exp.bitacoras.all():
                    worksheet.write(0, counter_btc, 'Bitácora de la Tienda Comunitaria', title_format)
                    if tr.archivo:
                        name, extension = os.path.splitext(tr.archivo.name)
                        root = os.path.join(store.almacen.unidad.sucursal.nombre.strip(), store.almacen.unidad.nombre.strip(), store.almacen.nombre.strip(), store.clave.strip(), f'{name}{extension}').upper()
                        try:
                            zf.write(tr.archivo.path, root)
                            worksheet.write_url(counter, counter_btc, root, cell_format)
                        except Exception as e:
                            print(e)
                    counter_btc += 1
                if counter_btc > max_row:
                    max_row = counter_btc
            counter += 1
        # --------------
        last_row = max_row
        counter = 1
        for store in stores:
            worksheet.write(counter, 0, store.almacen.unidad.sucursal.nombre, cell_format)
            worksheet.write_number(counter, 1, int(store.almacen.unidad.sucursal.clave), cell_format)
            worksheet.write(counter, 2, store.almacen.unidad.nombre, cell_format)
            worksheet.write_number(counter, 3, int(store.almacen.unidad.clave), cell_format)
            worksheet.write(counter, 4, store.almacen.nombre, cell_format)
            worksheet.write_number(counter, 5, int(store.almacen.clave), cell_format)
            worksheet.write_number(counter, 6, int(store.clave) if store.clave else 0, cell_format)
            exp = store.exp.first()
            
            if exp is not None:
                counter_cpa = last_row
                for tr in exp.convenios_pagos.all():
                    worksheet.write(0, counter_cpa, 'Reconocimiento de Adeudo o Convenio de Pago en Caso de Existir Faltantes', title_format)
                    if tr.archivo:
                        name, extension = os.path.splitext(tr.archivo.name)
                        root = os.path.join(store.almacen.unidad.sucursal.nombre.strip(), store.almacen.unidad.nombre.strip(), store.almacen.nombre.strip(), store.clave.strip(), f'{name}{extension}').upper()
                        try:
                            zf.write(tr.archivo.path, root)
                            worksheet.write_url(counter, counter_cpa, root, cell_format)
                        except Exception as e:
                            print(e)
                    counter_cpa += 1
                if counter_cpa > max_row:
                    max_row = counter_cpa
            counter += 1
        # --------------
        last_row = max_row
        counter = 1
        for store in stores:
            worksheet.write(counter, 0, store.almacen.unidad.sucursal.nombre, cell_format)
            worksheet.write_number(counter, 1, int(store.almacen.unidad.sucursal.clave), cell_format)
            worksheet.write(counter, 2, store.almacen.unidad.nombre, cell_format)
            worksheet.write_number(counter, 3, int(store.almacen.unidad.clave), cell_format)
            worksheet.write(counter, 4, store.almacen.nombre, cell_format)
            worksheet.write_number(counter, 5, int(store.almacen.clave), cell_format)
            worksheet.write_number(counter, 6, int(store.clave) if store.clave else 0, cell_format)
            exp = store.exp.first()
            
            if exp is not None:
                counter_plz = last_row
                for tr in exp.polizas.all():
                    worksheet.write(0, counter_plz, 'Pólizas', title_format)
                    if tr.archivo:
                        name, extension = os.path.splitext(tr.archivo.name)
                        root = os.path.join(store.almacen.unidad.sucursal.nombre.strip(), store.almacen.unidad.nombre.strip(), store.almacen.nombre.strip(), store.clave.strip(), f'{name}{extension}').upper()
                        try:
                            zf.write(tr.archivo.path, root)
                            worksheet.write_url(counter, counter_plz, root, cell_format)
                        except Exception as e:
                            print(e)
                    counter_plz += 1
                if counter_plz > max_row:
                    max_row = counter_plz
            counter += 1
        # --------------
    workbook.close()
    zf.writestr(f'EXPEDIENTE_TIENDAS.xlsx', output.getvalue())
    zf.close()

def services_exp_structure():
    zf = zipfile.ZipFile(os.path.join(settings.FILE_STRUCTURE_ROOT, 'EXPEDIENTE_CONTRATOS.zip'), 'w')
    output = io.BytesIO()
    # excel
    workbook = xlsxwriter.Workbook(output)
    gral_format = {'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': '#D9D9D9'}
    title_format = workbook.add_format(gral_format | {'font_size': 12, 'font_color': 'white', 'bg_color': '#235B4E', 'bold': True})
    cell_format = workbook.add_format(gral_format | {'font_size': 10})
    
    for suc in Sucursales.objects.all().order_by('nombre'):
        cegaps = CEGAPS.objects.filter(unidad__sucursal=suc)
        print(suc.nombre)
        worksheet = workbook.add_worksheet(suc.nombre.strip())
        worksheet.set_column('A1:O1', 23)
        worksheet.set_row(0, 30)
        worksheet.write('A1', 'Sucursal/Región', title_format)
        worksheet.write('B1', 'Clave de la sucursal/región', title_format)
        worksheet.write('C1', 'Unidad Operativa', title_format)
        worksheet.write('D1', 'Descripción de la partida', title_format)
        worksheet.write('E1', 'Clave de la partida', title_format)
        worksheet.write('F1', 'CEGAP', title_format)
        worksheet.write('G1', 'Archivo CEGAP', title_format)
        worksheet.write('H1', 'Archivo Constancia de Recepción', title_format)
        worksheet.write('I1', 'Archivo Carátula de la Póliza', title_format)
        worksheet.write('J1', 'Contrato', title_format)
        worksheet.write('K1', 'Archivo Contrato', title_format)
        worksheet.write('L1', 'Archivo Expediente Contrato', title_format)
        worksheet.write('M1', 'Factura', title_format)
        worksheet.write('N1', 'Archivo Factura', title_format)
        worksheet.write('O1', 'Archivo Evidencia Justificativa', title_format)
        worksheet.write('P1', 'Archivo Evidencia Complementaria', title_format)
        worksheet.write('Q1', 'Importe Total', title_format)
        worksheet.autofit()
        counter = 1
        for cegap in cegaps:
            root = os.path.join(cegap.unidad.sucursal.nombre, cegap.unidad.nombre, cegap.partida.clave, cegap.folio_cegap)
            archivo_cegap = ''
            archivo_constancia = ''
            archivo_caratula = ''
            archivo_contrato = ''
            archivo_expediente = ''
            if cegap.archivo:
                name, extension = os.path.splitext(cegap.archivo.name)
                archivo_cegap = os.path.join(root, f'{name}{extension}').upper()
                try:
                    # zf.write(cegap.archivo.path, archivo_cegap)
                    pass
                except Exception as e:
                    print(e)
                    archivo_cegap = ''
            if cegap.constancia_recepcion:
                name, extension = os.path.splitext(cegap.constancia_recepcion.name)
                archivo_constancia = os.path.join(root, f'{name}{extension}').upper()
                try:
                    # zf.write(cegap.constancia_recepcion.path, archivo_constancia)
                    pass
                except Exception as e:
                    print(e)
                    archivo_constancia = ''
            if cegap.caratula_poliza:
                name, extension = os.path.splitext(cegap.caratula_poliza.name)
                archivo_caratula = os.path.join(root, f'{name}{extension}').upper()
                try:
                    # zf.write(cegap.caratula_poliza.path, archivo_caratula)
                    pass
                except Exception as e:
                    print(e)
                    archivo_caratula = ''
            if cegap.contratos.first() is not None:
                if cegap.contratos.first().archivo:
                    name, extension = os.path.splitext(cegap.contratos.first().archivo.name)
                    archivo_contrato = os.path.join(root, f'{name}{extension}').upper()
                    try:
                        # zf.write(cegap.contratos.first().archivo.path, archivo_contrato)
                        pass
                    except Exception as e:
                        print(e)
                        archivo_contrato = ''
                if cegap.contratos.first().expediente:
                    name, extension = os.path.splitext(cegap.contratos.first().expediente.name)
                    archivo_expediente = os.path.join(root, f'{name}{extension}').upper()
                    try:
                        # zf.write(cegap.contratos.first().expediente.path, archivo_expediente)
                        pass
                    except Exception as e:
                        print(e)
                        archivo_expediente = ''
            for f in cegap.facturas.all():
                worksheet.write(counter, 0, cegap.unidad.sucursal.nombre, cell_format)
                worksheet.write_number(counter, 1, int(cegap.unidad.sucursal.clave), cell_format)
                worksheet.write(counter, 2, cegap.unidad.nombre, cell_format)
                worksheet.write(counter, 3, cegap.partida.nombre, cell_format)
                worksheet.write_number(counter, 4, int(cegap.partida.clave), cell_format)
                worksheet.write_number(counter, 5, int(cegap.folio_cegap), cell_format)
                worksheet.write_url(counter, 6, archivo_cegap, cell_format)
                worksheet.write_url(counter, 7, archivo_constancia, cell_format)
                worksheet.write_url(counter, 8, archivo_caratula, cell_format)
                worksheet.write_number(counter, 16, f.importe_total, cell_format)
                
                if cegap.contratos.first() is not None:
                    worksheet.write(counter, 9, cegap.contratos.first().clave, cell_format)
                    worksheet.write_url(counter, 10, archivo_contrato, cell_format)
                    worksheet.write_url(counter, 11, archivo_expediente, cell_format)
                    
                worksheet.write(counter, 12, f.folio_fiscal, cell_format)
        
                if f.archivo:
                    name, extension = os.path.splitext(f.archivo.name)
                    root_cegap = os.path.join(root, 'partidas', 'facturas', f'{f.folio}', f'{name}{extension}').upper()
                    try:
                        # zf.write(f.archivo.path, root_cegap)
                        worksheet.write_url(counter, 13, root_cegap, cell_format)
                    except Exception as e:
                        print(e)

                if f.comprobacion:
                    name, extension = os.path.splitext(f.comprobacion.name)
                    root_cegap = os.path.join(root, 'partidas', 'facturas', f'{f.folio}', f'{name}{extension}').upper()
                    try:
                        # zf.write(f.comprobacion.path, root_cegap)
                        worksheet.write_url(counter, 14, root_cegap, cell_format)
                    except Exception as e:
                        print(e)
                if f.justificacion:
                    name, extension = os.path.splitext(f.justificacion.name)
                    root_cegap = os.path.join(root, 'partidas', 'facturas', f'{f.folio}', f'{name}{extension}').upper()
                    try:
                        # zf.write(f.justificacion.path, root_cegap)
                        worksheet.write_url(counter, 15, root_cegap, cell_format)
                    except Exception as e:
                        print(e)
                counter += 1
    workbook.close()
    zf.writestr(f'EXPEDIENTE_CONTRATOS.xlsx', output.getvalue())
    zf.close()

def services_structure():
    zf = zipfile.ZipFile(os.path.join(settings.FILE_STRUCTURE_ROOT, 'CEGAPS_PARTIDAS.zip'), 'w')
    output = io.BytesIO()
    # excel
    workbook = xlsxwriter.Workbook(output)
    gral_format = {'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': '#D9D9D9'}
    title_format = workbook.add_format(gral_format | {'font_size': 12, 'font_color': 'white', 'bg_color': '#235B4E', 'bold': True})
    cell_format = workbook.add_format(gral_format | {'font_size': 10})
    
    for suc in Sucursales.objects.all().order_by('nombre'):
        cegaps = CEGAPS.objects.filter(unidad__sucursal=suc)
        print(suc.nombre)
        worksheet = workbook.add_worksheet(suc.nombre.strip())
        worksheet.set_column('A1:O1', 23)
        worksheet.set_row(0, 30)
        worksheet.write('A1', 'Sucursal/Región', title_format)
        worksheet.write('B1', 'Clave de la sucursal/región', title_format)
        worksheet.write('C1', 'Unidad Operativa', title_format)
        worksheet.write('D1', 'Descripción de la partida', title_format)
        worksheet.write('E1', 'Clave de la partida', title_format)
        worksheet.write('F1', 'CEGAP', title_format)
        worksheet.write('G1', 'Archivo CEGAP', title_format)
        worksheet.write('H1', 'Archivo Constancia de Recepción', title_format)
        worksheet.write('I1', 'Archivo Carátula de la Póliza', title_format)
        worksheet.write('J1', 'Contrato', title_format)
        worksheet.write('K1', 'Archivo Contrato', title_format)
        worksheet.write('L1', 'Factura', title_format)
        worksheet.write('M1', 'Archivo Factura', title_format)
        worksheet.write('N1', 'Archivo Evidencia Justificativa', title_format)
        worksheet.write('O1', 'Archivo Evidencia Complementaria', title_format)
        worksheet.write('P1', 'Importe Total', title_format)
        worksheet.autofit()
        counter = 1
        for cegap in cegaps:
            root = os.path.join(cegap.unidad.sucursal.nombre, cegap.unidad.nombre, cegap.partida.clave, cegap.folio_cegap)
            archivo_cegap = ''
            archivo_constancia = ''
            archivo_caratula = ''
            archivo_contrato = ''
            if cegap.archivo:
                name, extension = os.path.splitext(cegap.archivo.name)
                archivo_cegap = os.path.join(root, f'{name}{extension}').upper()
                try:
                    # zf.write(cegap.archivo.path, archivo_cegap)
                    pass
                except Exception as e:
                    print(e)
                    archivo_cegap = ''
            if cegap.constancia_recepcion:
                name, extension = os.path.splitext(cegap.constancia_recepcion.name)
                archivo_constancia = os.path.join(root, f'{name}{extension}').upper()
                try:
                    # zf.write(cegap.constancia_recepcion.path, archivo_constancia)
                    pass
                except Exception as e:
                    print(e)
                    archivo_constancia = ''
            if cegap.caratula_poliza:
                name, extension = os.path.splitext(cegap.caratula_poliza.name)
                archivo_caratula = os.path.join(root, f'{name}{extension}').upper()
                try:
                    # zf.write(cegap.caratula_poliza.path, archivo_caratula)
                    pass
                except Exception as e:
                    print(e)
                    archivo_caratula = ''
            if cegap.contratos.first() is not None:
                if cegap.contratos.first().archivo:
                    name, extension = os.path.splitext(cegap.contratos.first().archivo.name)
                    archivo_contrato = os.path.join(root, f'{name}{extension}').upper()
                    try:
                        # zf.write(cegap.contratos.first().archivo.path, archivo_contrato)
                        pass
                    except Exception as e:
                        print(e)
                        archivo_contrato = ''
            for f in cegap.facturas.all():
                worksheet.write(counter, 0, cegap.unidad.sucursal.nombre, cell_format)
                worksheet.write_number(counter, 1, int(cegap.unidad.sucursal.clave), cell_format)
                worksheet.write(counter, 2, cegap.unidad.nombre, cell_format)
                worksheet.write(counter, 3, cegap.partida.nombre, cell_format)
                worksheet.write_number(counter, 4, int(cegap.partida.clave), cell_format)
                worksheet.write_number(counter, 5, int(cegap.folio_cegap), cell_format)
                worksheet.write_url(counter, 6, archivo_cegap, cell_format)
                worksheet.write_url(counter, 7, archivo_constancia, cell_format)
                worksheet.write_url(counter, 8, archivo_caratula, cell_format)
                worksheet.write_number(counter, 15, f.importe_total, cell_format)
                
                if cegap.contratos.first() is not None:
                    worksheet.write(counter, 9, cegap.contratos.first().clave, cell_format)
                    worksheet.write_url(counter, 10, archivo_contrato, cell_format)
                    
                worksheet.write(counter, 11, f.folio_fiscal, cell_format)
        
                if f.archivo:
                    name, extension = os.path.splitext(f.archivo.name)
                    root_cegap = os.path.join(root, 'partidas', 'facturas', f'{f.folio}', f'{name}{extension}').upper()
                    try:
                        # zf.write(f.archivo.path, root_cegap)
                        pass
                        worksheet.write_url(counter, 12, root_cegap, cell_format)
                    except Exception as e:
                        print(e)
                if f.comprobacion:
                    name, extension = os.path.splitext(f.comprobacion.name)
                    root_cegap = os.path.join(root, 'partidas', 'facturas', f'{f.folio}', f'{name}{extension}').upper()
                    try:
                        # zf.write(f.comprobacion.path, root_cegap)
                        pass
                        worksheet.write_url(counter, 13, root_cegap, cell_format)
                    except Exception as e:
                        print(e)
                if f.justificacion:
                    name, extension = os.path.splitext(f.justificacion.name)
                    root_cegap = os.path.join(root, 'partidas', 'facturas', f'{f.folio}', f'{name}{extension}').upper()
                    try:
                        # zf.write(f.justificacion.path, root_cegap)
                        pass
                        worksheet.write_url(counter, 14, root_cegap, cell_format)
                    except Exception as e:
                        print(e)
                counter += 1
    workbook.close()
    zf.writestr(f'PARTIDAS_CEGAPS.xlsx', output.getvalue())
    zf.close()

def movs_structure(movs = []):
    zf = zipfile.ZipFile(os.path.join(settings.FILE_STRUCTURE_ROOT, 'MOVIMIENTOS.zip'), 'w')
    output = io.BytesIO()
    # excel
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('MOVIMIENTOS')
    gral_format = {'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': '#D9D9D9'}
    title_format = workbook.add_format(gral_format | {'font_size': 12, 'font_color': 'white', 'bg_color': '#235B4E', 'bold': True})
    cell_format = workbook.add_format(gral_format | {'font_size': 10})
    worksheet.set_column('A1:M1', 23)
    worksheet.set_row(0, 30)
    worksheet.write('A1', 'No.', title_format)
    worksheet.write('B1', 'Movimiento', title_format)
    worksheet.write('C1', 'Año', title_format)
    worksheet.write('D1', 'CEGAP', title_format)
    worksheet.write('E1', 'Importe CEGAP', title_format)
    worksheet.write('F1', 'Volúmen CEGAP (Ton)', title_format)
    worksheet.write('G1', 'Unidad Operativa', title_format)
    worksheet.write('H1', 'Almacén', title_format)
    worksheet.write('I1', 'Documento de entrada', title_format)
    worksheet.write('J1', 'Monto Documento', title_format)
    worksheet.write('K1', 'Volúmen Documento (Ton)', title_format)
    worksheet.write('L1', 'Archivo', title_format)
    worksheet.write('M1', 'Nombre del archivo', title_format)
    worksheet.autofit()
    counter = 1
    decounter = movs.count()
    for m in movs:
        unidad = m.almacen.unidad
        almacen = m.almacen
        producto = m.producto
        name, extension = os.path.splitext(m.archivo.name)
        path = os.path.join(unidad.nombre.strip(), almacen.nombre.strip(), producto.familia, f'M{m.clave}', f'M{m.clave}_{m.fecha.strftime("%Y")}_{producto.familia}_{almacen.clave}_{m.folio_doc}_{m.folio[-4:]}{extension}')
        # path = os.path.join(unidad.nombre, almacen.nombre, producto.familia, f'M{m.clave}', f'M{m.clave}_{m.fecha.strftime("%Y")}_{producto.familia}_{almacen.clave}_{m.folio_doc}_{extension}')
        # excel
        worksheet.write_number(counter, 1, int(m.clave), cell_format)
        worksheet.write_number(counter, 2, int(m.fecha.strftime("%Y")), cell_format)
        worksheet.write(counter, 6, unidad.nombre, cell_format)
        worksheet.write(counter, 7, almacen.nombre, cell_format)
        worksheet.write_number(counter, 8, int(m.folio_doc), cell_format)
        worksheet.write_number(counter, 9, m.importe, cell_format)
        worksheet.write_number(counter, 10, m.volumen, cell_format)
        worksheet.write_url(counter, 11, path, cell_format)
        worksheet.write(counter, 12, f'M{m.clave}_{m.fecha.strftime("%Y")}_{producto.familia}_{almacen.clave}_{m.folio_doc}_{extension}', cell_format)
        counter += 1
        decounter -= 1
        try:
            # zf.write(m.archivo.path, path)
            pass
        except Exception as e:
            print(e, m.folio)
        print(decounter)
    workbook.close()
    zf.writestr(f'MOVIMIENTOS.xlsx', output.getvalue())
    zf.close()

def pagares_structure(pagares = []):
    zf = zipfile.ZipFile(os.path.join(settings.FILE_STRUCTURE_ROOT, 'PAGARES.zip'), 'w')
    output = io.BytesIO()
    # excel
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('PAGARES')
    gral_format = {'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': '#D9D9D9'}
    title_format = workbook.add_format(gral_format | {'font_size': 12, 'font_color': 'white', 'bg_color': '#235B4E', 'bold': True})
    cell_format = workbook.add_format(gral_format | {'font_size': 10})
    worksheet.set_column('A1:H1', 23)
    worksheet.set_row(0, 30)
    worksheet.write('A1', 'Sucursal/Región', title_format)
    worksheet.write('B1', 'Unidad Operativa', title_format)
    worksheet.write('C1', 'Almacén', title_format)
    worksheet.write('D1', 'Clave de Almacén', title_format)
    worksheet.write('E1', 'Tienda', title_format)
    worksheet.write('F1', 'Año', title_format)
    worksheet.write('G1', 'Precio de venta', title_format)
    worksheet.write('H1', 'Pagaré', title_format)
    counter = 1
    decounter = pagares.count()
    for pag in pagares:
        sucursal = pag.expediente.tienda.almacen.unidad.sucursal
        unidad = pag.expediente.tienda.almacen.unidad
        almacen = pag.expediente.tienda.almacen
        tienda = pag.expediente.tienda
        name, extension = os.path.splitext(pag.archivo.name)
        path = os.path.join(sucursal.nombre.strip(), unidad.nombre.strip(), almacen.nombre.strip(), f'PAG_{unidad.clave}_{almacen.clave}_{pag.folio[-4:]}{extension}')
        # excel
        worksheet.write(counter, 0, sucursal.nombre, cell_format)
        worksheet.write(counter, 1, unidad.nombre, cell_format)
        worksheet.write(counter, 2, almacen.nombre, cell_format)
        worksheet.write_number(counter, 3, int(almacen.clave.strip()), cell_format)
        worksheet.write_number(counter, 4, int(tienda.clave.strip()), cell_format)
        worksheet.write_number(counter, 5, int(pag.anio), cell_format)
        worksheet.write_number(counter, 6, pag.precio_venta, cell_format)
        worksheet.write_url(counter, 7, path, cell_format)
        counter += 1
        decounter -= 1
        try:
            # zf.write(pag.archivo.path, path)
            pass
        except Exception as e:
            print(e, pag.folio)
        print(decounter)
    worksheet.autofit()
    workbook.close()
    zf.writestr(f'PAGARES.xlsx', output.getvalue())
    zf.close()