# Generated by Django 4.2.7 on 2025-02-22 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0051_lugares_recibo_url_historialtapy'),
    ]

    operations = [
        migrations.AddField(
            model_name='lugares',
            name='tpay_descuento',
            field=models.BooleanField(default=False),
        ),
    ]
