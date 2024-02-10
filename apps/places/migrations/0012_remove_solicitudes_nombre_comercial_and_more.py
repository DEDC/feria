# Generated by Django 4.1.7 on 2024-02-10 09:43

import django.core.validators
from django.db import migrations, models
import utils.models
import utils.validators


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0011_solicitudes_factura'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='solicitudes',
            name='nombre_comercial',
        ),
        migrations.RemoveField(
            model_name='solicitudes',
            name='nombre_persona',
        ),
        migrations.RemoveField(
            model_name='solicitudes',
            name='poder_notarial',
        ),
        migrations.AddField(
            model_name='solicitudes',
            name='curp',
            field=models.FileField(blank=True, null=True, upload_to=utils.models.UploadTo('CURP', 'solicitudes'), validators=[utils.validators.validate_pdf_file], verbose_name='CURP'),
        ),
        migrations.AddField(
            model_name='solicitudes',
            name='curp_txt',
            field=models.CharField(blank=True, max_length=18, null=True, validators=[django.core.validators.RegexValidator('^[A-Za-z0-9]*$', 'Ingrese una CURP correcta'), django.core.validators.MinLengthValidator(18)], verbose_name='CURP'),
        ),
        migrations.AddField(
            model_name='solicitudes',
            name='nombre',
            field=models.CharField(max_length=100, null=True, verbose_name='Nombre'),
        ),
        migrations.AddField(
            model_name='solicitudes',
            name='nombre_replegal',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Nombre del Representante Legal'),
        ),
        migrations.AlterField(
            model_name='comercios',
            name='descripcion',
            field=models.TextField(verbose_name='Describa a qué se dedica su Comercio'),
        ),
        migrations.AlterField(
            model_name='comercios',
            name='imagen',
            field=models.ImageField(upload_to=utils.models.UploadTo('PROPUESTA_LOCAL', 'propuestas_locales'), verbose_name='Adjunte el diseño en un archivo de imagen (JPG, PNG) del módulo o stand de su Comercio'),
        ),
        migrations.AlterField(
            model_name='comercios',
            name='vende_alcohol',
            field=models.BooleanField(choices=[(True, 'Sí'), (False, 'No')], verbose_name='¿Vendará bedidas alcohólicas en su Comercio?'),
        ),
        migrations.AlterField(
            model_name='solicitudes',
            name='acta_constitutiva',
            field=models.FileField(blank=True, null=True, upload_to=utils.models.UploadTo('ACTA_CONSTITUTIVA', 'solicitudes'), validators=[utils.validators.validate_pdf_file], verbose_name='Acta Constitutiva'),
        ),
        migrations.AlterField(
            model_name='solicitudes',
            name='cantidad_espacios',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Cantidad de espacios para el comercio'),
        ),
        migrations.AlterField(
            model_name='solicitudes',
            name='constancia_fiscal',
            field=models.FileField(blank=True, null=True, upload_to=utils.models.UploadTo('CONSTANCIA_FISCAL', 'solicitudes'), validators=[utils.validators.validate_pdf_file], verbose_name='Constancia de Situación Fiscal'),
        ),
        migrations.AlterField(
            model_name='solicitudes',
            name='estatus',
            field=models.CharField(choices=[('pending', 'Pendiente'), ('validated', 'Validado'), ('rejected', 'Rechazado')], editable=False, max_length=20),
        ),
        migrations.AlterField(
            model_name='solicitudes',
            name='factura',
            field=models.BooleanField(choices=[(True, 'Sí'), (False, 'No')], verbose_name='Factura'),
        ),
        migrations.AlterField(
            model_name='solicitudes',
            name='regimen_fiscal',
            field=models.CharField(blank=True, choices=[('moral', 'Persona Moral'), ('fisica', 'Persona Física')], max_length=100, null=True, verbose_name='Régimen fiscal'),
        ),
        migrations.AlterField(
            model_name='solicitudes',
            name='rfc_txt',
            field=models.CharField(blank=True, max_length=13, null=True, validators=[django.core.validators.RegexValidator('^[A-Za-z0-9]*$', 'Ingrese un RFC correcto'), django.core.validators.MinLengthValidator(12)], verbose_name='RFC'),
        ),
    ]