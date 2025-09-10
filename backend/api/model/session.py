from django.db import models
from django.conf import settings
from backend.basemodel import TimeBaseModel

class ChatSession(TimeBaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=255, default="New Chat")
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} ({getattr(self.user, 'email', 'Unknown')})"

    @property
    def message_count(self):
        return self.messages.count()

    def update_title_from_first_message(self):
        """Update the title based on the first user message"""
        first_message = self.messages.filter(sender='user').exclude(message='').first()
        if first_message and first_message.message:
            # Truncate to 50 characters and add ellipsis if needed
            title = first_message.message[:50]
            if len(first_message.message) > 50:
                title += "..."
            self.title = title
            self.save() 