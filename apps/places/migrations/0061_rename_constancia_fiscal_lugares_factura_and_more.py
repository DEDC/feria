# Generated by Django 4.2.7 on 2025-03-01 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0060_lugares_constancia_fiscal'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lugares',
            old_name='constancia_fiscal',
            new_name='factura',
        ),
        migrations.AddField(
            model_name='lugares',
            name='observacion',
            field=models.TextField(blank=True, null=True),
        ),
    ]
