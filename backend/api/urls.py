from django.urls import path
from .views import *

urlpatterns = [
    path('chatbot/', ChatbotAPIView.as_view(), name='chatbot'),
    path('chat-sessions/', ChatSessionListAPIView.as_view(), name='chat-sessions'),
    path('chat-sessions/<int:session_id>/', ChatHistoryAPIView.as_view(), name='chat-session-messages'),
    path('chat-sessions/<int:session_id>/delete/', ChatSessionDeleteAPIView.as_view(), name='delete-chat-session'),
    path("chat/audio/", ChatbotAudioAPIView.as_view(), name="chat-audio"),
    path("daily-tip/", DailyTipView.as_view(), name="daily-tip"),
] 