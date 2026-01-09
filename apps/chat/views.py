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
from .services.dify import DifyService
from django.http import StreamingHttpResponse
import os
import json

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



class ChatStreamView(APIView):
    """
    Proxy view for Dify streaming chat.
    Saves user and AI messages to the database.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        query = request.data.get('query')
        session_id = request.data.get('session_id')
        
        if not query:
            return Response({"error": "Query is required"}, status=status.HTTP_400_BAD_MODULE)

        # Get or create session
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id, user=request.user)
            except (ChatSession.DoesNotExist, ValueError):
                return Response({"error": "Invalid session ID"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Create a default topic or use part of the query
            topic = query[:50] + "..." if len(query) > 50 else query
            session = ChatSession.objects.create(user=request.user, topic=topic)

        # Save User Message
        ChatMessage.objects.create(session=session, role='USER', content=query)

        dify_service = DifyService()
        
        def stream_generator():
            yield f"data: {json.dumps({'event': 'session_created', 'session_id': str(session.id)})}\n\n"
            full_answer = ""
            try:
                for chunk in dify_service.stream_chat(
                    query=query, 
                    user_id=str(request.user.id), 
                    conversation_id=session.dify_conversation_id
                ):
                    event = chunk.get('event')
                    if event == 'message':
                        answer = chunk.get('answer', '')
                        full_answer += answer
                        yield f"data: {json.dumps(chunk)}\n\n"
                    elif event == 'message_end':
                        # Update session with Dify conversation ID
                        dify_conv_id = chunk.get('conversation_id')
                        if dify_conv_id and not session.dify_conversation_id:
                            session.dify_conversation_id = dify_conv_id
                            session.save()
                        
                        # Save AI Message
                        ChatMessage.objects.create(session=session, role='AI', content=full_answer)
                        yield f"data: {json.dumps(chunk)}\n\n"
                    else:
                        yield f"data: {json.dumps(chunk)}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'event': 'error', 'message': str(e)})}\n\n"

        return StreamingHttpResponse(stream_generator(), content_type='text/event-stream')
