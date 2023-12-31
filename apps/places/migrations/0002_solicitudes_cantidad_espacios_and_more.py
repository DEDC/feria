# Generated by Django 4.2.7 on 2023-11-17 17:07

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import utils.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('places', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitudes',
            name='cantidad_espacios',
            field=models.PositiveSmallIntegerField(null=True, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Cantidad de espacios para el comercio'),
        ),
        migrations.AlterField(
            model_name='solicitudes',
            name='no_calle',
            field=models.CharField(max_length=6, verbose_name='Número de Calle'),
        ),
        migrations.CreateModel(
            name='Comercios',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('folio', models.CharField(editable=False, max_length=25, null=True, unique=True)),
                ('fecha_reg', models.DateTimeField(auto_now_add=True)),
                ('fecha_mod', models.DateTimeField(auto_now=True)),
                ('activo', models.BooleanField(default=True, editable=False)),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre del Comercio')),
                ('descripcion', models.TextField(verbose_name='Describe tu Comercio')),
                ('imagen', models.ImageField(upload_to=utils.models.UploadTo('PROPUESTA_LOCAL', 'propuestas_locales'), verbose_name='En una imagen, representa la estructura física de tu local')),
                ('vende_alcohol', models.BooleanField(choices=[(True, 'Sí'), (False, 'No')], verbose_name='¿En su Comercio vende alcohol?')),
                ('solicitud', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='comercio', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
