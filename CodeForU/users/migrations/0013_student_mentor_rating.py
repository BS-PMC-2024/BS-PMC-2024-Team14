# Generated by Django 4.1.13 on 2024-08-08 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_student_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='mentor_rating',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
