from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework_simplejwt.tokens import RefreshToken
import os
import datetime
from config.settings.base import COOKIE_SECURE, COOKIE_SAMESITE
from rest_framework.authentication import SessionAuthentication
from django.middleware.csrf import get_token

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
    Authentication Bridge:
    This view acts as a bridge between Django's internal Session-based authentication
    (used by Allauth during the OAuth flow) and the project's JWT-based API.

    We explicitly use [SessionAuthentication] here because:
    1. The browser is hitting this URL directly after the Google redirect (same-origin).
    2. We need to read the session set by Allauth to identify the user.
    3. We want to ignore any invalid JWT cookies that might be lingering in the browser.
    """
    authentication_classes = [SessionAuthentication]
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
                secure=COOKIE_SECURE,
                samesite=COOKIE_SAMESITE,
                max_age=60 * 60 # 1 hour
            )
            
            # Set Refresh Token Cookie (Long-lived)
            response.set_cookie(
                key='refresh_token', 
                value=refresh_token,
                httponly=True,
                secure=COOKIE_SECURE,
                samesite=COOKIE_SAMESITE,
                max_age=60 * 60 * 24 # 1 day
            )
            
            # Ensure CSRF cookie is set
            get_token(request)
            return response
        else:
            # Not authenticated: The OAuth flow failed or was session expired.
            # We must clear the toxic cookies now, otherwise they will cause 401s elsewhere.
            response = redirect(f"{frontend_url}/login")
            
            # 確保失敗跳轉時也能同步最新的 CSRF 狀態
            get_token(request) 
            response.delete_cookie('access_token', samesite=COOKIE_SAMESITE)
            response.delete_cookie('refresh_token', samesite=COOKIE_SAMESITE)
            return response

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
            },
            "csrfToken": get_token(request)
        })

class LogoutView(APIView):
    """
    Endpoint to logout user by clearing cookies.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        response = Response({"detail": "Logged out successfully"}, status=status.HTTP_200_OK)
        # Clear cookies
        response.delete_cookie('access_token', samesite=COOKIE_SAMESITE)
        response.delete_cookie('refresh_token', samesite=COOKIE_SAMESITE)
        return response
