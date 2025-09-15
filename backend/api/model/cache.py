from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import now
from datetime import timedelta
from backend.basemodel import TimeBaseModel

class CachedAnswer(TimeBaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cached_answers')
    query_text = models.TextField(unique=True, db_index=True)
    answer = models.TextField()
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        # Set expiry if not already set and update answer
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=1)
        super().save(update_fields=['answer', 'expires_at'], *args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return self.query_text[:50]
