# Generated by Django 4.1.7 on 2024-02-13 08:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dates', '0004_alter_citasagendadas_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='citasagendadas',
            unique_together=set(),
        ),
    ]