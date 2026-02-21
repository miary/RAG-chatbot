from django.db import models
import uuid


class ChatSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Session {self.id} - {self.title or 'Untitled'}"


class ChatMessage(models.Model):
    MESSAGE_TYPES = [
        ('user', 'User'),
        ('bot', 'Bot'),
    ]

    FEEDBACK_CHOICES = [
        ('none', 'None'),
        ('up', 'Thumbs Up'),
        ('down', 'Thumbs Down'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        ChatSession,
        related_name='messages',
        on_delete=models.CASCADE,
    )
    message_type = models.CharField(max_length=4, choices=MESSAGE_TYPES)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    feedback = models.CharField(
        max_length=4,
        choices=FEEDBACK_CHOICES,
        default='none',
    )
    sources = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.message_type}: {self.text[:50]}"
