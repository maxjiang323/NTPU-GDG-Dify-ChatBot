from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.chat.views import ChatSessionViewSet, ChatMessageViewSet, GoogleLoginCallback

router = DefaultRouter()
router.register(r'sessions', ChatSessionViewSet, basename='session')
router.register(r'messages', ChatMessageViewSet, basename='message')

urlpatterns = [
    path('gdg-ntpu/dify-chatbot/admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # allauth 的所有 URLs
    
    # API Routes
    path('api/chat/', include(router.urls)),
    path('api/auth/google/success/', GoogleLoginCallback.as_view(), name='google_login_success'),
    
    # path('', include('apps.core.urls')),  # 引入 core app 的 URLs
]