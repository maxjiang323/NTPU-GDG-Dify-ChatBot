from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.chat.views import ChatSessionViewSet, ChatMessageViewSet, ChatStreamView


from apps.accounts.views import AuthStatusView, LogoutView, GoogleAuthCodeLoginView


router = DefaultRouter()
router.register(r'sessions', ChatSessionViewSet, basename='session')
router.register(r'messages', ChatMessageViewSet, basename='message')

urlpatterns = [
    path('gdg-ntpu/dify-chatbot/admin/', admin.site.urls),
    
    # API Routes
    path('api/chat/', include(router.urls)),
    path('api/chat/stream/', ChatStreamView.as_view(), name='chat_stream'),
    path('api/auth/status/', AuthStatusView.as_view(), name='auth_status'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
    path('api/auth/google/', GoogleAuthCodeLoginView.as_view(), name='google_auth_code_login'),

    
    # path('', include('apps.core.urls')),  # 引入 core app 的 URLs
]