from django.contrib import admin
from .model.session import ChatSession
from .model.history import History
# Register your models here.

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'title')
    search_fields = ('user','title')
    list_filter = ('title', 'user')

@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ('session', 'sender','message')
    search_fields = ('session','sender')
    list_filter = ('sender', 'message')