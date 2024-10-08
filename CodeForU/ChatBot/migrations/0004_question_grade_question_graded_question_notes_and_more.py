# Generated by Django 4.1.13 on 2024-08-17 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ChatBot", "0003_question_answer_text_question_answered_by_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="grade",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="question",
            name="graded",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="question",
            name="notes",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="question",
            name="original_question_id",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
