# Generated by Django 4.1.7 on 2024-02-16 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0016_alter_solicitudes_no_calle'),
    ]

    operations = [
        migrations.AddField(
            model_name='validaciones',
            name='validador',
            field=models.CharField(editable=False, max_length=200, null=True),
        ),
    ]
