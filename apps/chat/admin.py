from django.contrib import admin
from .models import ChatSession, ChatMessage

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('role', 'content', 'created_at')
    can_delete = False
    ordering = ('created_at',)

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'topic', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('topic', 'user__username', 'id')
    inlines = [ChatMessageInline]
    ordering = ('-updated_at',)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'role', 'content_preview', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('content',)
    ordering = ('-created_at',)

    def content_preview(self, obj):
        return obj.content[:50]
    content_preview.short_description = '內容預覽'
