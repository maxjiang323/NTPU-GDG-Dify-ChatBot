from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.chat.views import ChatSessionViewSet, ChatMessageViewSet, ChatStreamView


from apps.accounts.views import login_cancelled_redirect, GoogleLoginCallback, AuthStatusView, LogoutView
from django.views.generic import TemplateView
from django.urls import re_path
from django.conf import settings
from django.views.static import serve
import os

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
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),

    # Fallback for public assets (lovable-uploads, robots.txt, etc.) if requested without /static/
    re_path(r'^(?P<path>(lovable-uploads|favicon\.ico|robots\.txt|placeholder\.svg).*)$', 
        serve, {'document_root': os.path.join(settings.BASE_DIR, 'frontend/Dify-ChatBot-V2/dist')}),
    
    # 讓 React 的 index.html 靜態頁面能被 Django 載入 (SPA Catch-all)
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),  
]