# Generated by Django 4.1.13 on 2024-07-10 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_remove_user_is_mentor'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='gender',
            field=models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], default='Male', max_length=10, verbose_name='Gender'),
        ),
        migrations.AddField(
            model_name='user',
            name='passport_id',
            field=models.CharField(default=0, max_length=10, unique=True, verbose_name='Passport ID'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(db_index=True, max_length=254, unique=True, verbose_name='Email Address'),
        ),
    ]
