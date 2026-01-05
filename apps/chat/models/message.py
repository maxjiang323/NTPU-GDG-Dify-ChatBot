from django.db import models

class ChatMessage(models.Model):
    """
    對話訊息模型
    儲存單一條訊息內容
    """
    ROLE_CHOICES = (
        ('USER', 'User'),
        ('AI', 'AI'),
        ('SYSTEM', 'System'),
    )

    session = models.ForeignKey(
        'chat.ChatSession',
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='所屬對話'
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        verbose_name='角色'
    )

    content = models.TextField(
        verbose_name='內容'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='建立時間'
    )

    class Meta:
        verbose_name = '對話訊息'
        verbose_name_plural = '對話訊息'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.get_role_display()}: {self.content[:50]}"
