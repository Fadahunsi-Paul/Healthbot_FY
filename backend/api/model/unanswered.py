from backend.basemodel import TimeBaseModel
from django.db import models
from django.conf import settings

class Unanswered(TimeBaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='unanswered')
    question = models.TextField()
    answer = models.TextField()
    is_answered = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.question[:50]}"