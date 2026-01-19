from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework_simplejwt.tokens import RefreshToken
import os
import datetime
import uuid
from config.settings.base import COOKIE_SECURE, COOKIE_SAMESITE
from rest_framework.authentication import SessionAuthentication
from django.middleware.csrf import get_token
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

@method_decorator(csrf_exempt, name='dispatch')
class GoogleIdentityLoginView(APIView):
    """
    Handle Google Identity Services (GIS) login.
    Receives an ID token from the frontend, verifies it with Google,
    and returns a JWT pair (access + refresh) set in cookies.
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = [] # Disable DRF auth to prevent CSRF check by CookieJWTAuthentication

    def post(self, request):
        token = request.data.get('credential')
        if not token:
            return Response({"error": "No credential provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1. Verify ID Token
            # Retrieve Google Client ID from environment variables
            GOOGLE_CLIENT_ID = os.getenv('SOCIAL_AUTH_GOOGLE_CLIENT_ID')
            if not GOOGLE_CLIENT_ID:
                # Fallback or error if not set. Warning log would be good here.
                return Response({"error": "Server configuration error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            idinfo = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                GOOGLE_CLIENT_ID,
                clock_skew_in_seconds=10
            )

            # 2. Get User Info
            email = idinfo.get('email')
            if not email:
                return Response({"error": "Email not provided in token"}, status=status.HTTP_400_BAD_REQUEST)

            # --- Domain Whitelist Check ---
            # 從環境變數讀取允許的網域，例如 ALLOWED_EMAIL_DOMAINS=gm.ntpu.edu.tw,gmail.com
            allowed_domains_str = os.getenv('ALLOWED_EMAIL_DOMAINS', '')
            if allowed_domains_str:
                allowed_domains = [d.strip().lower() for d in allowed_domains_str.split(',') if d.strip()]
                user_domain = email.split('@')[-1].lower()
                if user_domain not in allowed_domains:
                    print(f"Login rejected for {email}: domain {user_domain} not in {allowed_domains}")
                    return Response({
                        "error": f"不支援使用 @{user_domain} 網域登入，請使用授權網域。"
                    }, status=status.HTTP_403_FORBIDDEN)
            # ------------------------------
                
            name = idinfo.get('name', '')
            picture = idinfo.get('picture', '')
            
            # 3. Find or Create User
            User = get_user_model()
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # Create a new user
                # Use email prefix + uuid for unique username
                username = f"{email.split('@')[0]}_{str(uuid.uuid4())[:8]}"
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=name
                )
            
            # Update avatar if missing
            if hasattr(user, 'avatar') and not user.avatar and picture:
                user.avatar = picture
                user.save()

            # 4. Issue JWT
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            response = Response({"detail": "Login successful"})
            
            # Set Access Token Cookie
            response.set_cookie(
                key='access_token', 
                value=access_token,
                httponly=True,
                secure=COOKIE_SECURE,
                samesite=COOKIE_SAMESITE,
                max_age=60 * 60 # 1 hour
            )
            
            # Set Refresh Token Cookie
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

        except ValueError as e:
            return Response({"error": f"Invalid token: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

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
