# Generated by Django 4.2.7 on 2025-02-17 04:36

from django.db import migrations, models
import utils.models
import utils.validators


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0041_merge_20250215_1733'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitudes',
            name='poder_notarial',
            field=models.FileField(blank=True, null=True, upload_to=utils.models.UploadTo('PODER_NOTARIAL', 'solicitudes'), validators=[utils.validators.validate_pdf_file], verbose_name='Poder Notarial'),
        ),
    ]
