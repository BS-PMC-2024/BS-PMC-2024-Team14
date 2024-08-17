from django.db import models
from django.conf import settings

class Question(models.Model):
    user = models.IntegerField(blank=True, null=True)
    question_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    level = models.IntegerField(blank=True, null=True)
    answered_by = models.IntegerField(blank=True, null=True)  # New field for the user who answered
    answer_text = models.TextField(blank=True, null=True)  # New field for the answer text
    original_question_id = models.IntegerField(blank=True, null=True)  # Reference to the original question
    
    grade = models.IntegerField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    graded = models.BooleanField(default=False)

    def __str__(self):
        return f"Question by user ID {self.user} at {self.created_at}"
