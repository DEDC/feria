# Django
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator, MinLengthValidator, RegexValidator
# users
from apps.users.models import Usuarios
# utils
from utils.models import ControlInfo, UploadTo
from utils.validators import validate_pdf_file


class Solicitudes(ControlInfo):
    identifier = 'SLC'
    regimen_fiscal = models.CharField('Régimen fiscal', max_length = 100, choices = (('moral', 'Persona Moral'), ('fisica', 'Persona Física')))
    rfc_txt = models.CharField('RFC', max_length = 13, validators = [RegexValidator('^[A-Za-z0-9]*$', 'Ingrese un RFC correcto'), MinLengthValidator(12)])
    nombre_persona = models.CharField('Nombre de la Persona Física o del Representante Legal', max_length = 100)
    nombre_comercial = models.CharField('Nombre Comercial o Razón Social', max_length = 100)
    constancia_fiscal = models.FileField('Constancia de Situación Fiscal', upload_to = UploadTo('CONSTANCIA_FISCAL', 'solicitudes'), validators = [validate_pdf_file])
    comprobante_domicilio = models.FileField('Comprobante de Domicilio', upload_to = UploadTo('COMPROBANTE_DOMICILIO', 'solicitudes'), validators = [validate_pdf_file])
    acta_constitutiva = models.FileField('Acta Constitutiva', upload_to = UploadTo('ACTA_CONSTITUTIVA', 'solicitudes'), validators = [validate_pdf_file])
    poder_notarial = models.FileField('Poder Notarial', upload_to = UploadTo('PODER_NOTARIAL', 'solicitudes'), validators = [validate_pdf_file])
    identificacion = models.FileField('Identificación Oficial', upload_to = UploadTo('IDENTIFICACION_OFICIAL', 'solicitudes'), validators = [validate_pdf_file])
    calle = models.CharField('Calle', max_length = 200)
    no_calle = models.CharField('Número de Calle', max_length = 6)
    colonia = models.CharField('Colonia', max_length = 200)
    codigo_postal = models.CharField('Código Postal', max_length = 5, validators = [MinLengthValidator(5), RegexValidator('^[0-9]*$', 'Ingrese un código postal correcto')])
    municipio = models.CharField('Municipio', max_length = 200)
    cantidad_espacios = models.PositiveSmallIntegerField('Cantidad de espacios para el comercio', validators=[MinValueValidator(1)], null=True)
    estado = models.CharField('Estado', max_length = 200, choices=(('tabasco', 'Tabasco'),))    
    usuario = models.ForeignKey(Usuarios, editable=False, on_delete=models.PROTECT, related_name='solicitudes')

class Comercios(ControlInfo):
    identifier = 'COM'
    nombre = models.CharField('Nombre del Comercio', max_length = 100)
    descripcion = models.TextField('Describe tu Comercio')
    imagen = models.ImageField('En una imagen, representa la estructura física de tu local', upload_to=UploadTo('PROPUESTA_LOCAL', 'propuestas_locales'))
    vende_alcohol = models.BooleanField('¿En su Comercio vende alcohol?', choices=((True, 'Sí'), (False, 'No')))
    voltaje = models.CharField('¿Qué voltaje necesita su Comercio?',   max_length=10, choices=(('110', '110v'), ('220', '220v')), null=True)
    equipos = models.CharField('¿Qué equipos usará para operar en su Comercio?', max_length=500, null=True)
    solicitud = models.OneToOneField(Solicitudes, editable=False, on_delete=models.PROTECT, related_name='comercio')