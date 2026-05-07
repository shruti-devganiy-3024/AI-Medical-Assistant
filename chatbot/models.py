from django.db import models
from django.contrib.auth.models import User


class Chat(models.Model):
    """
    Represents one conversation session.
    A user can have many Chats. Each Chat contains many Messages.
    
    Example:
        - Chat #1: "Fever and cough" (4 messages)
        - Chat #2: "Headache concerns" (2 messages)
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chats',
    )
    title = models.CharField(
        max_length=100,
        default='New Chat',
        help_text="Auto-generated from the first user message",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # bumps when new message arrives

    class Meta:
        # Sidebar shows most recently active chats first
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.created_at:%Y-%m-%d})"

    @property
    def message_count(self):
        """Convenience: how many messages are in this chat."""
        return self.messages.count()

    @property
    def last_message_preview(self):
        """First 60 characters of the latest message — used in sidebar."""
        last = self.messages.order_by('-created_at').first()
        if not last:
            return ""
        text = last.text
        return text[:60] + ('...' if len(text) > 60 else '')


class Message(models.Model):
    """
    A single message inside a Chat.
    'sender' tells us who said it: the user or the bot.
    """
    SENDER_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
    ]

    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,    # if Chat is deleted, all its Messages go too
        related_name='messages',     # so we can do: chat.messages.all()
    )
    sender = models.CharField(
        max_length=10,
        choices=SENDER_CHOICES,
    )
    text = models.TextField()

    # Extra fields useful for the bot
    is_symptom_message = models.BooleanField(
        default=False,
        help_text="True if this user message contained recognizable symptoms",
    )
    predicted_disease = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Top disease prediction (only set on bot messages)",
    )
    confidence = models.FloatField(
        blank=True,
        null=True,
        help_text="Confidence score 0-1 (only set on bot messages)",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Inside a chat, oldest messages first (chronological order)
        ordering = ['created_at']

    def __str__(self):
        preview = self.text[:40] + ('...' if len(self.text) > 40 else '')
        return f"[{self.sender}] {preview}"