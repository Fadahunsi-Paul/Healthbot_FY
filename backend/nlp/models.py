# nlp/models.py
from django.db import models
from django.utils import timezone
from datetime import timedelta

class QuestionEmbedding(models.Model):
    """
    Optional storage of embeddings for persistence (one row per dataset question).
    You can skip using this model if you prefer storing embeddings only on disk.
    """
    question = models.TextField(unique=True)
    embedding = models.JSONField()  # list of floats
    qtype = models.CharField(max_length=128, blank=True, null=True)
    answer = models.TextField()

    def __str__(self):
        return self.question[:80]


class CachedAnswer(models.Model):
    """
    Persistent cache for answers with TTL (expires_at).
    """
    query_text = models.TextField(unique=True, db_index=True)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        return self.expires_at > timezone.now()

    def __str__(self):
        return f"{self.query_text[:50]} -> {self.answer[:50]}"
