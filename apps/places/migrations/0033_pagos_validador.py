# Generated by Django 4.1.7 on 2024-03-04 01:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0032_alter_pagos_tipo'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagos',
            name='validador',
            field=models.CharField(editable=False, max_length=200, null=True),
        ),
    ]