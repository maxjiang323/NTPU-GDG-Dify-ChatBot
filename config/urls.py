from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('gdg-ntpu/dify-chatbot/admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # allauth 的所有 URLs
    # path('', include('apps.core.urls')),  # 引入 core app 的 URLs
]