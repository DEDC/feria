# Generated by Django 4.2.7 on 2025-04-08 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0065_alter_lugares_zona'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productosextras',
            name='tipo',
            field=models.CharField(choices=[('terraza', 'Terraza'), ('terraza_grande', 'Terraza Grande'), ('licencia_alcohol', 'Permiso de Alcohol')], max_length=20, null=True),
        ),
    ]
