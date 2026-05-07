from django.contrib import admin
from .models import Chat, Message


class MessageInline(admin.TabularInline):
    """Show messages inline inside a Chat in admin."""
    model = Message
    extra = 0
    readonly_fields = ['sender', 'text', 'is_symptom_message',
                       'predicted_disease', 'confidence', 'created_at']
    can_delete = False


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'message_count', 'created_at', 'updated_at']
    list_filter = ['created_at', 'user']
    search_fields = ['title', 'user__username']
    inlines = [MessageInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'chat', 'sender', 'text_preview', 'is_symptom_message', 'created_at']
    list_filter = ['sender', 'is_symptom_message', 'created_at']
    search_fields = ['text', 'chat__title']
    readonly_fields = ['created_at']

    def text_preview(self, obj):
        return obj.text[:60] + ('...' if len(obj.text) > 60 else '')
    text_preview.short_description = 'Text'