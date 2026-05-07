from django.urls import path
from . import views

urlpatterns = [
    # ── Chat sessions (list + create) ──────────────────────────
    # GET  /api/chats/   → list all chats (sidebar)
    # POST /api/chats/   → create new chat
    path('chats/', views.chat_list, name='chat_list'),

    # ── Single chat (detail + delete) ──────────────────────────
    # GET    /api/chats/<id>/  → get chat with all messages
    # DELETE /api/chats/<id>/  → delete chat
    path('chats/<int:chat_id>/', views.chat_detail, name='chat_detail'),

    # ── Send message (main chat endpoint) ──────────────────────
    # POST /api/chats/<id>/messages/  → send message, get AI reply
    path('chats/<int:chat_id>/messages/', views.send_message, name='send_message'),
]