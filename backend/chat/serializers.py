from rest_framework import serializers
from .models import ChatSession, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'session', 'message_type', 'text', 'timestamp', 'feedback', 'sources']
        read_only_fields = ['id', 'timestamp']


class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'created_at', 'updated_at', 'messages', 'last_message']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-timestamp').first()
        if last_msg:
            return ChatMessageSerializer(last_msg).data
        return None


class ChatSessionListSerializer(serializers.ModelSerializer):
    """Lighter serializer for listing sessions (no full messages)."""
    message_count = serializers.SerializerMethodField()
    last_message_preview = serializers.SerializerMethodField()

    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'created_at', 'updated_at', 'message_count', 'last_message_preview']

    def get_message_count(self, obj):
        return obj.messages.count()

    def get_last_message_preview(self, obj):
        last_msg = obj.messages.order_by('-timestamp').first()
        if last_msg:
            return last_msg.text[:80]
        return None


class SendMessageSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=4000)
    session_id = serializers.UUIDField(required=False, allow_null=True)


class FeedbackSerializer(serializers.Serializer):
    feedback = serializers.ChoiceField(choices=['up', 'down', 'none'])
