# Generated by Django 4.1.7 on 2024-03-22 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0035_alter_estacionamiento_zona_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='estacionamiento',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='estacionamiento',
            name='placa',
            field=models.CharField(max_length=100, unique=True, verbose_name='Placa'),
        ),
        migrations.RemoveField(
            model_name='estacionamiento',
            name='local',
        ),
        migrations.RemoveField(
            model_name='estacionamiento',
            name='nombre_comercial',
        ),
        migrations.RemoveField(
            model_name='estacionamiento',
            name='zona',
        ),
    ]
