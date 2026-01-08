from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.chat.views import ChatSessionViewSet, ChatMessageViewSet, ChatStreamView


from apps.accounts.views import login_cancelled_redirect, GoogleLoginCallback, AuthStatusView


router = DefaultRouter()
router.register(r'sessions', ChatSessionViewSet, basename='session')
router.register(r'messages', ChatMessageViewSet, basename='message')

urlpatterns = [
    path('gdg-ntpu/dify-chatbot/admin/', admin.site.urls),
    
    # 攔截 allauth 的取消登入頁面路徑，導向到自定義 view
    path('accounts/3rdparty/login/cancelled/', login_cancelled_redirect),
    path('accounts/', include('allauth.urls')),  # allauth 的所有 URLs
    
    # API Routes
    path('api/chat/', include(router.urls)),
    path('api/chat/stream/', ChatStreamView.as_view(), name='chat_stream'),
    path('api/auth/google/success/', GoogleLoginCallback.as_view(), name='google_login_success'),
    path('api/auth/status/', AuthStatusView.as_view(), name='auth_status'),

    
    # path('', include('apps.core.urls')),  # 引入 core app 的 URLs
]