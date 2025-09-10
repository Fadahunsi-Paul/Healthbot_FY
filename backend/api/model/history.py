from backend.basemodel import TimeBaseModel
from django.db import models
from .session import ChatSession

class History(TimeBaseModel):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=[('user', 'User'), ('bot', 'Bot')])
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    audio = models.FileField(upload_to='chat_audio/', null=True, blank=True)    


    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender}: {self.message[:20]}..."