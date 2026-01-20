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
import requests

@method_decorator(csrf_exempt, name='dispatch')
class GoogleAuthCodeLoginView(APIView):
    """
    Handle Google Auth Code Login (Redirect Flow).
    Exchanges authorization code for tokens, then logs user in.
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        code = request.data.get('code')
        redirect_uri = request.data.get('redirect_uri')
        
        if not code or not redirect_uri:
            return Response({"error": "Missing code or redirect_uri"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Exchange Code for Tokens
        token_endpoint = "https://oauth2.googleapis.com/token"
        client_id = os.getenv('SOCIAL_AUTH_GOOGLE_CLIENT_ID')
        client_secret = os.getenv('SOCIAL_AUTH_GOOGLE_CLIENT_SECRET')
        
        if not client_id or not client_secret:
             return Response({"error": "Server configuration error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        payload = {
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        try:
            res = requests.post(token_endpoint, data=payload)
            token_data = res.json()
            
            if 'error' in token_data:
                return Response({"error": token_data.get('error_description', 'Token exchange failed')}, status=status.HTTP_400_BAD_REQUEST)
                
            id_token_str = token_data.get('id_token')
            
            # 2. Verify ID Token
            # We verify it to get the claims safely
            idinfo = id_token.verify_oauth2_token(
                id_token_str, 
                google_requests.Request(), 
                client_id,
                clock_skew_in_seconds=10
            )
            
            # 3. Get User Info
            email = idinfo.get('email')
            if not email:
                return Response({"error": "Email not provided in token"}, status=status.HTTP_400_BAD_REQUEST)

            # --- Domain Whitelist Check ---
            allowed_domains_str = os.getenv('ALLOWED_EMAIL_DOMAINS', '')
            if allowed_domains_str:
                allowed_domains = [d.strip().lower() for d in allowed_domains_str.split(',') if d.strip()]
                user_domain = email.split('@')[-1].lower()
                if user_domain not in allowed_domains:
                    return Response({
                        "error": f"不支援使用 @{user_domain} 網域登入，請使用授權網域。"
                    }, status=status.HTTP_403_FORBIDDEN)
            
            name = idinfo.get('name', '')
            picture = idinfo.get('picture', '')
            
            # 4. Find or Create User
            User = get_user_model()
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                username = f"{email.split('@')[0]}_{str(uuid.uuid4())[:8]}"
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=name
                )
            
            if hasattr(user, 'avatar') and not user.avatar and picture:
                user.avatar = picture
                user.save()

            # 5. Issue JWT
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            response = Response({"detail": "Login successful"})
            
            response.set_cookie(
                key='access_token', value=access_token, httponly=True,
                secure=COOKIE_SECURE, samesite=COOKIE_SAMESITE, max_age=3600
            )
            response.set_cookie(
                key='refresh_token', value=refresh_token, httponly=True,
                secure=COOKIE_SECURE, samesite=COOKIE_SAMESITE, max_age=86400
            )
            
            get_token(request) # Ensure CSRF
            return response

        except Exception as e:
            # print(e)
            return Response({"error": f"Login failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

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
