from django.contrib import admin
from .model.session import ChatSession
from .model.history import History
from .model.healthtip import HealthTip
from .model.dailytip import DailyTip
from .model.unanswered import Unanswered
import csv
from django.http import HttpResponse
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

@admin.register(HealthTip)
class HealthTipAdmin(admin.ModelAdmin):
    list_display = ('title', 'body')
    search_fields = ('title', 'body')
    list_filter = ('title', 'body')

@admin.register(DailyTip)
class DailyTipAdmin(admin.ModelAdmin):
    list_display = ('tip', 'date')
    search_fields = ('tip', 'date')
    list_filter = ('tip', 'date')

@admin.register(Unanswered)
class UnansweredAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'answer', 'is_answered')
    search_fields = ('user', 'question', 'answer')
    list_filter = ('is_answered', 'user')
    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="unanswered_export.csv"'

        writer = csv.writer(response)
        writer.writerow(["Question", "Answer"])  # header

        qs = queryset if queryset.exists() else Unanswered.objects.filter(is_answered=True)
        for item in qs:
            writer.writerow([item.question, item.answer])

        return response

    export_to_csv.short_description = "📥 Export selected (or all answered) to CSV"
    actions = [export_to_csv]
