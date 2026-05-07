from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Chat, Message
from .serializers import (
    ChatListSerializer,
    ChatDetailSerializer,
    MessageSerializer,
)
from .ml_model import predict_disease, build_caring_reply, is_symptom_message
from .input_handler import clean_input, extract_symptoms

# ============================================================
# HELPER: Auto-generate a chat title from first user message
# ============================================================
def generate_title(message_text):
    """
    Creates a short, clean title from the first user message.
    Examples:
        "I have fever, cough and headache" → "I have fever, cough and..."
        "fever cough" → "fever cough"
    """
    # Capitalize first letter, trim to 60 chars
    title = message_text.strip().capitalize()
    if len(title) > 60:
        title = title[:57] + '...'
    return title


# ============================================================
# ENDPOINT 1 + 2: List Chats / Create New Chat
# GET  /api/chats/   → returns sidebar list
# POST /api/chats/   → creates a new empty chat session
# ============================================================
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def chat_list(request):

    # ─── GET: Return all chats for the sidebar ───────────────
    if request.method == 'GET':
        chats = Chat.objects.filter(user=request.user)
        serializer = ChatListSerializer(chats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ─── POST: Create a brand-new empty chat session ─────────
    if request.method == 'POST':
        chat = Chat.objects.create(
            user=request.user,
            title='New Chat',
        )
        serializer = ChatDetailSerializer(chat)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ============================================================
# ENDPOINT 3 + 5: Get Chat Detail / Delete Chat
# GET    /api/chats/<id>/  → returns full chat with all messages
# DELETE /api/chats/<id>/  → deletes the chat + all its messages
# ============================================================
@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def chat_detail(request, chat_id):

    # Security: make sure this chat belongs to the logged-in user
    try:
        chat = Chat.objects.get(id=chat_id, user=request.user)
    except Chat.DoesNotExist:
        return Response(
            {'error': 'Chat not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    # ─── GET: Return full chat with all messages ─────────────
    if request.method == 'GET':
        serializer = ChatDetailSerializer(chat)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ─── DELETE: Remove chat + all its messages ───────────────
    if request.method == 'DELETE':
        chat.delete()
        return Response(
            {'message': 'Chat deleted successfully.'},
            status=status.HTTP_200_OK
        )


# ============================================================
# ENDPOINT 4: Send a Message (MAIN ENDPOINT)
# POST /api/chats/<id>/messages/
#
# Body: { "message": "I have fever and cough" }
#
# Flow:
#   1. Validate + clean input
#   2. Save user message
#   3. Run ML prediction
#   4. Build caring reply
#   5. Save bot message
#   6. Return both messages + metadata
# ============================================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request, chat_id):

    # ── Get the chat ─────────────────────────────────────────
    try:
        chat = Chat.objects.get(id=chat_id, user=request.user)
    except Chat.DoesNotExist:
        return Response(
            {'error': 'Chat not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    # ── Get + validate raw message ────────────────────────────
    raw_message = request.data.get('message', '')
    cleaned     = clean_input(raw_message)

    if not cleaned:
        return Response(
            {'error': 'Message cannot be empty.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # ── Auto-title from first message ─────────────────────────
    is_first = not chat.messages.exists()
    if is_first:
        chat.title = generate_title(cleaned)
        chat.save(update_fields=['title'])

    # ── Save user message ─────────────────────────────────────
    user_message = Message.objects.create(
        chat=chat,
        sender='user',
        text=cleaned,
    )

    # ── Check for casual input FIRST ─────────────────────────
    from .input_handler import is_casual_message
    if is_casual_message(cleaned):
        # Give friendly redirect — no ML prediction needed
        bot_reply_text = (
            "Hello! 👋 I'm your AI health assistant.\n"
            "Please describe your symptoms and I'll help you understand "
            "what might be going on.\n\n"
            "Example: \"I have fever, cough, and headache.\""
        )
        bot_message = Message.objects.create(
            chat=chat,
            sender='bot',
            text=bot_reply_text,
        )

        from django.utils import timezone
        chat.updated_at = timezone.now()
        chat.save(update_fields=['updated_at'])

        return Response({
            'chat_id':            chat.id,
            'chat_title':         chat.title,
            'user_message':       MessageSerializer(user_message).data,
            'bot_message':        MessageSerializer(bot_message).data,
            'show_booking_popup': False,   # no popup for casual input
            'prediction':         None,
        }, status=status.HTTP_201_CREATED)

    # ── Extract symptoms + run ML ─────────────────────────────
    symptoms   = extract_symptoms(cleaned)
    prediction = predict_disease(symptoms)

    # ── Symptom flag (for booking popup) ─────────────────────
    symptom_flag = is_symptom_message(prediction)
    user_message.is_symptom_message = symptom_flag
    user_message.save(update_fields=['is_symptom_message'])

    # ── Build reply ───────────────────────────────────────────
    bot_reply_text = build_caring_reply(
        prediction, original_message=cleaned
    )

    # ── Save bot message ──────────────────────────────────────
    bot_message = Message.objects.create(
        chat=chat,
        sender='bot',
        text=bot_reply_text,
        predicted_disease=prediction.get('top_disease', ''),
        confidence=prediction.get('confidence', None),
    )

    # ── Bump updated_at ───────────────────────────────────────
    from django.utils import timezone
    chat.updated_at = timezone.now()
    chat.save(update_fields=['updated_at'])

    # ── Return full response ──────────────────────────────────
    return Response({
        'chat_id':            chat.id,
        'chat_title':         chat.title,
        'user_message':       MessageSerializer(user_message).data,
        'bot_message':        MessageSerializer(bot_message).data,
        'show_booking_popup': symptom_flag,
        'prediction': {
            'top_disease':  prediction.get('top_disease'),
            'confidence':   prediction.get('confidence'),
            'is_confident': prediction.get('is_confident'),
        },
    }, status=status.HTTP_201_CREATED)