from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from config.settings.base import COOKIE_SECURE, COOKIE_SAMESITE
from rest_framework.authentication import SessionAuthentication
from django.middleware.csrf import get_token
from django.contrib.auth import get_user_model

def login_cancelled_redirect(request):
    """
    當使用者在 SSO 頁面點選取消時，將其導向回前端登入頁面，
    避免停留在 Django 預設的成功/取消頁面。
    """
    # 清除 Django 內部的訊息（例如你看到的「成功登入」但其實已取消的誤導訊息）
    storage = messages.get_messages(request)
    for _ in storage:
        pass  # 讀取訊息即會將其從 storage 中移除
    
    frontend_login_url = f"/login"
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
        if request.user.is_authenticated:
            # Generate JWT
            refresh = RefreshToken.for_user(request.user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            response = redirect(f"/chat")
            
            # Set Access Token Cookie (Short-lived)
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
            # Not authenticated: The OAuth flow failed, was session expired, or domain blocked.
            # (Note: Specific domain blocks are already handled in the adapter via ImmediateHttpResponse)
            
            response = redirect("/login?err_code=AUTH_FAILED")
            
            # 確保失敗跳轉時也能同步最新的 CSRF 狀態
            get_token(request) 
            response.delete_cookie('access_token', samesite=COOKIE_SAMESITE)
            response.delete_cookie('refresh_token', samesite=COOKIE_SAMESITE)
            return response

class AuthStatusView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def get(self, request):
        access_token = request.COOKIES.get("access_token")
        refresh_token = request.COOKIES.get("refresh_token")
        
        # 情況1：完全沒有 token → 未登入
        if not access_token and not refresh_token:
            return JsonResponse(
                {"code": "not_authenticated", "detail": "User not authenticated"},
                status=401
            )
        
        # 情況2：嘗試驗證 access_token
        if access_token:
            try:
                token = AccessToken(access_token)  # ← 這會自動驗證！
                user_id = token['user_id']  # ← 從 token 讀取 user_id

                User = get_user_model()
                try:
                    user = User.objects.get(id=user_id)
                    return Response({
                        "isAuthenticated": True,
                        "user": {
                            "id": user.id,
                            "email": user.email,
                            "username": user.username
                        },
                        "csrfToken": get_token(request)
                    })
                except User.DoesNotExist:
                    # 用戶不存在（不常見）
                    pass
                    
            except (InvalidToken, TokenError):
                # Token 無效或過期，繼續檢查其他情況
                pass
        
        # 情況3：有 refresh_token（無論 access_token 是否存在）
        # 這表示用戶之前登入過，但 access_token 可能過期了
        if refresh_token:
            return JsonResponse(
                {"code": "access_token_expired", "detail": "Access token expired"},
                status=401
            )
        
        # 情況4：只有 access_token，沒有 refresh_token
        # 這是不正常的狀態，應該視為未登入
        if access_token and not refresh_token:
            return JsonResponse(
                {"code": "not_authenticated", "detail": "Session expired"},
                status=401
            )
        
        # 情況5：其他意外情況
        return JsonResponse(
            {"code": "not_authenticated", "detail": "User not authenticated"},
            status=401
        )

class LogoutView(APIView):
    """
    Endpoint to logout user by clearing cookies.
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        response = Response({"detail": "Logged out successfully"}, status=status.HTTP_200_OK)
        # 確保設置 CSRF cookie
        get_token(request)

        # Clear cookies
        response.delete_cookie('access_token', samesite=COOKIE_SAMESITE)
        response.delete_cookie('refresh_token', samesite=COOKIE_SAMESITE)
        return response
