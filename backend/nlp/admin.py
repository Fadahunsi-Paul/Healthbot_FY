from django.contrib import admin
from .models import QuestionEmbedding,CachedAnswer

# Register your models here.
admin.site.register(QuestionEmbedding),
admin.site.register(CachedAnswer)