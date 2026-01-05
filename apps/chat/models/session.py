import uuid
from django.db import models

class ChatSession(models.Model):
    """
    聊天室/對話 Session 模型
    代表一次完整的對話紀錄容器
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='chat_sessions',
        verbose_name='使用者',
        null=True,
        blank=True
    )

    topic = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='對話主題'
    )

    dify_conversation_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Dify Conversation ID'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='建立時間'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新時間'
    )

    class Meta:
        verbose_name = '對話 Session'
        verbose_name_plural = '對話 Sessions'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user} - {self.topic or str(self.id)}"
