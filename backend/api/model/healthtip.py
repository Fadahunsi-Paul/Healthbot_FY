from backend.basemodel import TimeBaseModel
from django.db import models

class HealthTip(TimeBaseModel):
    source = models.CharField(max_length=100)            # e.g. "myhealthfinder" or "adviceslip"
    external_id = models.CharField(max_length=200, null=True, blank=True)
    title = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    published_at = models.DateTimeField(null=True, blank=True)
    fetched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (self.title or self.body[:50]).strip()