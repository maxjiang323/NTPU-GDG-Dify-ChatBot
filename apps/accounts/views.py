from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework_simplejwt.tokens import RefreshToken
import os
import datetime

def login_cancelled_redirect(request):
    """
    當使用者在 SSO 頁面點選取消時，將其導向回前端登入頁面，
    避免停留在 Django 預設的成功/取消頁面。
    """
    # 清除 Django 內部的訊息（例如你看到的「成功登入」但其實已取消的誤導訊息）
    storage = messages.get_messages(request)
    for _ in storage:
        pass  # 讀取訊息即會將其從 storage 中移除
    
    frontend_url = os.getenv("FRONTEND_URL")
    frontend_login_url = f"{frontend_url}/login"
    return redirect(frontend_login_url)

class GoogleLoginCallback(APIView):
    """
    Callback for Google Login.
    Exchanges the session/auth from Allauth for a JWT and redirects to Frontend.
    Sets HttpOnly cookies for security.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        frontend_url = os.getenv("FRONTEND_URL")
        
        if request.user.is_authenticated:
            # Generate JWT
            refresh = RefreshToken.for_user(request.user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            response = redirect(f"{frontend_url}/chat")
            
            # Set Access Token Cookie (Short-lived)
            # Use strict/lax settings for SameSite to prevent CSRF, but ensure it works across domains if needed.
            # Localhost dev usually needs Lax.
            response.set_cookie(
                key='access_token', 
                value=access_token,
                httponly=True,
                secure=False, # Set to True in Production (HTTPS)
                samesite='Lax', 
                max_age=60 * 60 # 1 hour
            )
            
            # Set Refresh Token Cookie (Long-lived)
            response.set_cookie(
                key='refresh_token', 
                value=refresh_token,
                httponly=True,
                secure=False, # Set to True in Production (HTTPS)
                samesite='Lax',
                max_age=60 * 60 * 24 # 1 day
            )
            
            return response
        else:
            # Not authenticated, redirect to login with error?
            return redirect(f"{frontend_url}/login?error=auth_failed")

class AuthStatusView(APIView):
    """
    Endpoint for Frontend to check authentication status.
    Reads the HttpOnly cookie via the custom CookieJWTAuthentication class.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "isAuthenticated": True,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username
            }
        })
