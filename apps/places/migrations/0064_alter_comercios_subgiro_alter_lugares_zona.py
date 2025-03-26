# Generated by Django 4.2.7 on 2025-03-26 18:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0063_comercios_subgiro'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comercios',
            name='subgiro',
            field=models.CharField(blank=True, choices=[('amb_1', 'Chicharrones y otros'), ('amb_2', 'Cigarros y otros'), ('amb_3', 'Esquites, aguas')], max_length=100, null=True, verbose_name='SubGiro del Comercio'),
        ),
        migrations.AlterField(
            model_name='lugares',
            name='zona',
            field=models.CharField(choices=[('z_a', 'Zona A'), ('z_b', 'Zona B'), ('z_c', 'Zona C'), ('z_d', 'Zona D'), ('n_1', 'Nave 1'), ('n_2', 'Nave 2'), ('n_3', 'Nave 3'), ('s_t', 'Sabor a Tab.'), ('teatro', 'Teatro al A. L.'), ('amb', 'Ambulantes'), ('patrocinador', 'Patrocinador')], max_length=20, null=True),
        ),
    ]
