# Generated by Django 4.1.7 on 2024-02-10 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0014_alter_solicitudes_cantidad_espacios'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solicitudes',
            name='estado',
            field=models.CharField(choices=[('1', 'AGUASCALIENTES'), ('2', 'BAJA CALIFORNIA'), ('3', 'BAJA CALIFORNIA SUR'), ('4', 'CHIHUAHUA'), ('5', 'CHIAPAS'), ('6', 'CAMPECHE'), ('7', 'CIUDAD DE MEXICO'), ('8', 'COAHUILA'), ('9', 'COLIMA'), ('10', 'DURANGO'), ('11', 'GUERRERO'), ('12', 'GUANAJUATO'), ('13', 'HIDALGO'), ('14', 'JALISCO'), ('15', 'MICHOACAN'), ('16', 'ESTADO DE MEXICO'), ('17', 'MORELOS'), ('18', 'NAYARIT'), ('19', 'NUEVO LEON'), ('20', 'OAXACA'), ('21', 'PUEBLA'), ('22', 'QUINTANA ROO'), ('23', 'QUERETARO'), ('24', 'SINALOA'), ('25', 'SAN LUIS POTOSI'), ('26', 'SONORA'), ('27', 'TABASCO'), ('28', 'TLAXCALA'), ('29', 'TAMAULIPAS'), ('30', 'VERACRUZ'), ('31', 'YUCATAN'), ('32', 'ZACATECAS')], max_length=200, verbose_name='Estado'),
        ),
        migrations.AlterField(
            model_name='solicitudes',
            name='municipio',
            field=models.CharField(max_length=200, verbose_name='Municipio o Delegación'),
        ),
        migrations.AlterField(
            model_name='solicitudes',
            name='nombre',
            field=models.CharField(max_length=100, null=True, verbose_name='Nombre o Razón Social'),
        ),
    ]
