from django.shortcuts import render, redirect
from django.conf import settings
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model

from .models.session import ChatSession
from .models.message import ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer

User = get_user_model()

class ChatSessionViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user).order_by('-updated_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ChatMessageViewSet(viewsets.ModelViewSet):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only allow accessing messages from sessions owned by the user
        return ChatMessage.objects.filter(session__user=self.request.user).order_by('created_at')

class GoogleLoginCallback(APIView):
    """
    Callback for Google Login.
    Exchanges the session/auth from Allauth for a JWT and redirects to Frontend.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        if request.user.is_authenticated:
            # Generate JWT
            refresh = RefreshToken.for_user(request.user)
            access_token = str(refresh.access_token)
            
            # Redirect to Frontend with token
            # Note: In production, consider a more secure way than query params, 
            # or ensure the frontend immediately consumes and clears it.
            frontend_url = "http://localhost:8080" # Default Vite port, confirm if different
            redirect_url = f"{frontend_url}?token={access_token}&email={request.user.email}"
            return redirect(redirect_url)
        
        return Response({"error": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)
