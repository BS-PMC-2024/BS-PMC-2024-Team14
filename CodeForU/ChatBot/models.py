from django.db import models
from django.conf import settings

class Question(models.Model):
    user = models.IntegerField(blank=True,null=True)
    question_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Question by user ID {self.user} at {self.created_at}"

