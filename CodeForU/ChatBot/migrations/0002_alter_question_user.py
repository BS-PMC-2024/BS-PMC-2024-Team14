# Generated by Django 4.1.13 on 2024-08-05 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ChatBot', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='user',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
