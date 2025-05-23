# Generated by Django 4.2.7 on 2025-04-16 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0070_alter_estacionamiento_placa'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lugares',
            name='zona',
            field=models.CharField(choices=[('z_a', 'Zona A'), ('z_b', 'Zona B'), ('z_c', 'Zona C'), ('z_d', 'Zona D'), ('n_1', 'Nave 1'), ('n_2', 'Nave 2'), ('n_3', 'Nave 3'), ('s_t', 'Sabor a Tab.'), ('teatro', 'Teatro al A. L.'), ('amb', 'Ambulantes'), ('patrocinador', 'Patrocinador'), ('ganadera', 'Ganadera'), ('flor', 'Elección Flor'), ('bandas', 'Imposición de Bandas')], max_length=20, null=True),
        ),
    ]
