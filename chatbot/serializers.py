from rest_framework import serializers
from .models import Chat, Message


class MessageSerializer(serializers.ModelSerializer):
    """
    Converts a single Message to/from JSON.
    Used inside chat detail views.
    """
    class Meta:
        model = Message
        fields = [
            'id',
            'sender',
            'text',
            'is_symptom_message',
            'predicted_disease',
            'confidence',
            'created_at',
        ]
        read_only_fields = ['created_at', 'is_symptom_message', 
                            'predicted_disease', 'confidence']


class ChatListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for sidebar list.
    Includes title + last message preview + count + dates.
    """
    last_message_preview = serializers.CharField(read_only=True)
    message_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Chat
        fields = [
            'id',
            'title',
            'last_message_preview',
            'message_count',
            'created_at',
            'updated_at',
        ]


class ChatDetailSerializer(serializers.ModelSerializer):
    """
    Full chat with all its messages.
    Used when user opens a specific chat from sidebar.
    """
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = [
            'id',
            'title',
            'created_at',
            'updated_at',
            'messages',
        ]