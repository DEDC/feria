# Python
import uuid
# Django
from django.db import models
from django.core.validators import MinValueValidator, MinLengthValidator, RegexValidator
# users
from apps.users.models import Usuarios
# utils
from utils.models import ControlInfo, UploadTo
from utils.validators import validate_pdf_file
from utils.naves import estadosmexico

giros = (
    ('ambulante', 'Comercio Ambulante'),
    ('chocolates', 'Chocolates'), 
    ('postres', 'Postres'),
    ('pasteleria', 'Pastelería y Panadería'),
    ('cafe', 'Café'),
    ('miel', 'Miel'),
    ('salsas', 'Salsas y Aderezos'),
    ('frituras', 'Frituras y Botanas'),
    ('quesos', 'Quesos y Embutidos'),
    ('cervezas', 'Cerveza artesanal'),
    ('cremas', 'Cremas de licor'),
    ('vinos', 'Vinos artesanales'),
    ('butifarras', 'Butifarras'),
    ('pozol', 'Pozol y Dulces'),
    ('snacks', 'Carrito de Snacks'),
    ('restaurantes', 'Restaurantes'),
    ('bares', 'Bares'),
    ('cocina_humo', 'Cocina de humo'),
    ('antojitos', 'Antojitos tabasqueños'),
    ('botanas', 'Botanas y Comida rápida'),
    ('bebidas', 'Bebidas preparadas y refrescos'),
    ('panaderia', 'Postres y Panadería'),
    ('bebidas_alcohol', 'Bebidas preparadas con alcohol'),
    ('conservas', 'Conservas y Encurtidos'),
    ('artesanias', 'Artesanías'),
    ('juegos', 'Juguetes y Juegos'),
    ('joyeria', 'Joyería, Bisutería y Accesorios'),
    ('ropa', 'Ropa y Textiles'),
    ('articulos_hogar', 'Artículos para el hogar'),
    ('zapateria', 'Zapatería'),
    ('perfumeria', 'Perfumería y Cosméticos'),
    ('regalos', 'Regalos y Novedades'),
    ('telefonia', 'Telefonía celular y Accesorios'),
    ('articulos_belleza', 'Artículos de belleza'),
    ('articulos_electro', 'Artículos electrónicos'),
    ('electrodomesticos', 'Electrodomésticos'),
    ('abarrotes', 'Abarrotes'),
    ('otro', 'Otro')
)


class Solicitudes(ControlInfo):
    identifier = 'SLC'
    estatus = models.CharField(max_length=20, editable=False, choices=(('pending', 'Observado'), ('validated', 'Validado'), ('validated-direct', 'Validado Directamente'), ('rejected', 'Rechazado'), ('resolved', 'Solventado'),))
    usuario = models.ForeignKey(Usuarios, editable=False, on_delete=models.PROTECT, related_name='solicitudes')
    cantidad_espacios = models.PositiveSmallIntegerField('Cantidad de espacios para el comercio', validators=[MinValueValidator(1)])
    mas_espacios = models.BooleanField('Requiero más de 3 espacios', choices=((True, 'Sí'), (False, 'No')), default=False)
    regimen_fiscal = models.CharField('Régimen fiscal', max_length=100, choices = (('moral', 'Persona Moral'), ('fisica', 'Persona Física')), null=True, blank=True)
    # direccion
    colonia = models.CharField('Colonia', max_length=200)
    calle = models.CharField('Calle', max_length=200)
    no_calle = models.CharField('Número de Casa', max_length=6)
    estado = models.CharField('Estado', max_length=200, choices=estadosmexico)
    municipio = models.CharField('Municipio o Delegación', max_length=200)
    codigo_postal = models.CharField('Código Postal', max_length=5, validators=[MinLengthValidator(5), RegexValidator('^[0-9]*$', 'Ingrese un código postal correcto')])
    # general info
    nombre = models.CharField('Nombre o Razón Social', max_length=100, null=True)
    rfc_txt = models.CharField('RFC', max_length = 13, validators = [RegexValidator('^[A-Za-z0-9]*$', 'Ingrese un RFC correcto'), MinLengthValidator(12)], null=True, blank=True)
    curp_txt = models.CharField('CURP', max_length = 18, validators = [RegexValidator('^[A-Za-z0-9]*$', 'Ingrese una CURP correcta'), MinLengthValidator(18)], null=True, blank=True)
    # general docs
    identificacion = models.FileField('Identificación Oficial', upload_to=UploadTo('IDENTIFICACION_OFICIAL', 'solicitudes'), validators=[validate_pdf_file])
    acta_constitutiva = models.FileField('Acta Constitutiva', upload_to=UploadTo('ACTA_CONSTITUTIVA', 'solicitudes'), validators=[validate_pdf_file], null=True, blank=True)
    poder_notarial = models.FileField('Poder Notarial', upload_to=UploadTo('PODER_NOTARIAL', 'solicitudes'), validators=[validate_pdf_file], null=True, blank=True)
    comprobante_domicilio = models.FileField('Comprobante de Domicilio', upload_to=UploadTo('COMPROBANTE_DOMICILIO', 'solicitudes'), validators=[validate_pdf_file])
    constancia_fiscal = models.FileField('Constancia de Situación Fiscal', upload_to=UploadTo('CONSTANCIA_FISCAL', 'solicitudes'), validators=[validate_pdf_file], null=True, blank=True)
    curp = models.FileField('CURP', upload_to=UploadTo('CURP', 'solicitudes'), validators=[validate_pdf_file], null=True, blank=True)
    # others
    nombre_replegal = models.CharField('Nombre del Representante Legal', max_length=100, null=True, blank=True)
    factura = models.BooleanField('Factura', choices=((True, 'Sí'), (False, 'No')))
    data_tpay = models.JSONField(null=True, blank=True)

    def get_last_unattended_validation(self):
        return self.validaciones.filter(atendido=False, estatus='pending').last()


class Comercios(ControlInfo):
    identifier = 'COM'
    estatus = models.CharField(max_length=20, editable=False, choices=(('pending', 'Observado'), ('validated', 'Validado'), ('rejected', 'Rechazado'), ('resolved', 'Solventado'),), default='')
    nombre = models.CharField('Nombre del Comercio', max_length = 100)
    descripcion = models.TextField('Describa a qué se dedica su Comercio')
    imagen = models.ImageField('Adjunte el diseño en un archivo de imagen (JPG, PNG) del módulo o stand de su Comercio', upload_to=UploadTo('PROPUESTA_LOCAL', 'propuestas_locales'), blank=True, null=True)
    vende_alcohol = models.BooleanField('¿Vendará bedidas alcohólicas en su Comercio?', choices=((True, 'Sí'), (False, 'No')), null=True, blank=True)
    voltaje = models.CharField('¿Qué voltaje necesita su Comercio?',   max_length=10, choices=(('110', '110v'), ('220', '220v')), null=True, blank=True)
    equipos = models.CharField('¿Qué equipos usará para operar en su Comercio?', max_length=500, null=True, blank=True)
    giro = models.CharField('Giro del Comercio',   max_length=100, choices=giros, null=True)
    solicitud = models.OneToOneField(Solicitudes, editable=False, on_delete=models.PROTECT, related_name='comercio')

    def get_last_unattended_validation(self):
        return self.validaciones_com.filter(atendido=False, estatus='pending').last()


class Validaciones(ControlInfo):
    identifier = 'VAL'
    estatus = models.CharField(max_length=20, editable=False, choices=(('pending', 'Observado'), ('validated', 'Validado'), ('rejected', 'Rechazado'), ('resolved', 'Solventado'), ('validated-direct', 'Validado Directamente'),), null=True)
    solicitud = models.ForeignKey(Solicitudes, related_name='validaciones', on_delete=models.CASCADE, null=True)
    comercio = models.ForeignKey(Comercios, related_name='validaciones_com', on_delete=models.CASCADE, null=True)
    campos = models.JSONField(null=True)
    comentarios = models.TextField(null=True)
    atendido = models.BooleanField(default=False, editable=False)
    validador = models.CharField(max_length=200, editable=False, null=True)


class Lugares(ControlInfo):
    identifier='PLC'
    uuid_place = models.UUIDField(editable=False, unique=True)
    estatus = models.CharField(max_length=20, choices=(('temp', 'Temporal'), ('assign', 'Asignado')), default='temp')
    zona = models.CharField(max_length=20, choices=(('z_a', 'Zona A'), ('z_b', 'Zona B'), ('z_c', 'Zona C'), ('z_d', 'Zona D'), ('n_1', 'Nave 1'), ('n_2', 'Nave 2'), ('n_3', 'Nave 3')), null=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    m2 = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    nombre = models.CharField(max_length=10, default='')
    tramite_id = models.IntegerField(default=0)
    usuario = models.ForeignKey(Usuarios, editable=False, on_delete=models.PROTECT, related_name='usuario_lugar')
    solicitud = models.ForeignKey(Solicitudes, editable=False, on_delete=models.PROTECT, related_name='solicitud_lugar')
    data_tpay = models.JSONField(null=True, blank=True)
    tpay_val = models.JSONField(null=True, blank=True)
    tpay_folio = models.CharField(max_length=150, null=True, blank=True)
    tpay_pagado = models.BooleanField(default=False)
    tpay_web = models.BooleanField(default=False)
    tpay_socket = models.BooleanField(default=False)
    tpay_service = models.BooleanField(default=False)


class ProductosExtras(ControlInfo):
    identifier = 'PDX'
    lugar = models.ForeignKey(Lugares, editable=False, on_delete=models.PROTECT, related_name='extras')
    tipo = models.CharField(max_length=20, null=True, choices=(('terraza', 'Terraza'), ('terraza_grande', 'Terraza Grande'), ('licencia_alcohol', 'Licencia de Alcohol')))
    precio = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    m2 = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    to_places = models.TextField(default='')


class Pagos(ControlInfo):
    estatus = (
        (1, "En proceso"),
        (2, "Aceptado"),
        (3, "Cancelado"),
    )
    identifier = 'PAG'
    solicitud = models.ForeignKey(Solicitudes, editable=False, on_delete=models.PROTECT, related_name='solicitud_pagos')
    usuario = models.ForeignKey(Usuarios, editable=False, on_delete=models.PROTECT, related_name='usuario_pagos')
    tipo = models.CharField(
        max_length=20, null=True,
        choices=(
            ('tpay', 'TPAY'),
            ('tarjeta', 'Tarjeta'),
            ('efectivo', 'Efectivo'),
            ('transferencia', 'Transferencia')
        )
    )
    pagado = models.BooleanField(default=False)
    data_tpay = models.JSONField(null=True, blank=True)
    validador = models.CharField(max_length=200, editable=False, null=True)
    estatus = models.PositiveSmallIntegerField(choices=estatus, default=1)


class Estacionamiento(ControlInfo):
    identifier = 'TES'
    nombre = models.CharField('Nombre o Razón Social', max_length=100)
    acceso = models.CharField('Puerta de Acceso', max_length=20, choices=(('puerta_1', 'Puerta 1'), ('puerta_2', 'Puerta 2'), ('puerta_3', 'Puerta 3'), ('puerta_herradura', 'Puerta Herradura')))
    no_estacionamiento = models.CharField('No. de Estacionamiento', max_length=2, choices=(('2', '2'), ('3', '3'), ('4', '4'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9')))
    ubicacion = models.CharField('Ubicación', max_length=30, choices=(('n_1', 'Nave 1'), ('n_2', 'Nave 2'), ('n_3', 'Nave 3'), ('plaza_infantil', 'Plaza Infantil'), ('zona_extrema', 'Zona Extrema'), ('antojeria', 'Antojería'), ('circo', 'Atrás del Circo')))
    tipo = models.CharField('Tipo', max_length=12)
    marca = models.CharField('Marca', max_length=12)
    color = models.CharField('Color', max_length=12)
    placa = models.CharField('Placa', max_length=12, unique=True)