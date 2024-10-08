# Generated by Django 4.1.13 on 2024-08-05 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ChatBot', '0002_alter_question_user'),
        ('users', '0009_remove_helprequest_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='helprequest',
            name='user',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='saved_questions',
            field=models.ManyToManyField(blank=True, related_name='saved_by', to='ChatBot.question'),
        ),
    ]
