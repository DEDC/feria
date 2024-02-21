# Generated by Django 4.1.7 on 2024-02-19 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0020_validaciones_comercio_alter_validaciones_solicitud'),
    ]

    operations = [
        migrations.AddField(
            model_name='comercios',
            name='estatus',
            field=models.CharField(choices=[('pending', 'Observado'), ('validated', 'Validado'), ('rejected', 'Rechazado'), ('resolved', 'Solventado')], default='', editable=False, max_length=20),
        ),
    ]