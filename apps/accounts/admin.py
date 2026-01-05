from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from apps.chat.models import ChatSession


class ChatSessionInline(admin.TabularInline):
    model = ChatSession
    extra = 0
    fields = ('id', 'topic', 'created_at', 'updated_at')
    readonly_fields = ('id', 'created_at', 'updated_at')
    show_change_link = True
    can_delete = False
    ordering = ('-updated_at',)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """自訂使用者的 Admin 介面"""
    inlines = [ChatSessionInline]

    # 列表頁顯示的欄位
    list_display = ['username', 'email', 'phone', 'is_staff', 'date_joined']

    # 可以篩選的欄位
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']

    # 可以搜尋的欄位
    search_fields = ['username', 'email', 'phone']

    # 編輯頁面的欄位分組
    fieldsets = UserAdmin.fieldsets + (
        ('額外資訊', {
            'fields': ('phone', 'avatar', 'bio')
        }),
    )

    # 新增使用者時的欄位
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('額外資訊', {
            'fields': ('phone', 'bio')
        }),
    )