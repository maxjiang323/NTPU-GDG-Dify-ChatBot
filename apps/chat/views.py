from django.shortcuts import render, redirect
from django.conf import settings
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from rest_framework.throttling import UserRateThrottle
import logging
from django.core.cache import cache

from .models.session import ChatSession
from .models.message import ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer
from .services.dify import DifyService
from django.http import StreamingHttpResponse
import os
import json
import re

User = get_user_model()
logger = logging.getLogger(__name__)

class ChatSessionViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user).order_by('-updated_at')

    def list(self, request, *args, **kwargs):
        """
        List user sessions with Redis caching.
        Cache key: user_{user_id}_sessions
        """
        cache_key = f"user_{request.user.id}_sessions"
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            logger.info(f"🟢 Cache HIT for sessions: {cache_key}")
            return Response(cached_data)

        logger.info(f"🟡 Cache MISS for sessions: {cache_key} - Fetching from DB")
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)  # 5 minutes
        return response

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        # Invalidate sessions cache
        logger.info(f"🔴 Invalidating cache for sessions: user_{self.request.user.id}_sessions")
        cache.delete(f"user_{self.request.user.id}_sessions")

    def perform_update(self, serializer):
        super().perform_update(serializer)
        # Invalidate sessions cache
        logger.info(f"🔴 Invalidating cache for sessions: user_{self.request.user.id}_sessions")
        cache.delete(f"user_{self.request.user.id}_sessions")

    def perform_destroy(self, instance):
        # Invalidate messages cache for this session
        logger.info(f"🔴 Invalidating cache for messages: session_{instance.id}_messages")
        cache.delete(f"session_{instance.id}_messages")
        super().perform_destroy(instance)
        # Invalidate sessions cache
        logger.info(f"🔴 Invalidating cache for sessions: user_{self.request.user.id}_sessions")
        cache.delete(f"user_{self.request.user.id}_sessions")

class ChatMessageViewSet(viewsets.ModelViewSet):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only allow accessing messages from sessions owned by the user
        return ChatMessage.objects.filter(session__user=self.request.user).order_by('created_at')

    def list(self, request, *args, **kwargs):
        """
        List messages for a session with Redis caching.
        Expects ?session=<session_id> in query params.
        Cache key: session_{session_id}_messages
        """
        session_id = request.query_params.get('session')
        
        if session_id:
            # Cache key must include USER ID or we must validate ownership before cache lookup.
            # OR better: Only cache if we are sure the session belongs to the user.
            cache_key = f"user_{request.user.id}_session_{session_id}_messages"
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                logger.info(f"🟢 Cache HIT for messages: {cache_key}")
                return Response(cached_data)

            logger.info(f"🟡 Cache MISS for messages: {cache_key} - Fetching from DB")
            response = super().list(request, *args, **kwargs)
            
            # Only cache if response is successful
            if response.status_code == 200:
                cache.set(cache_key, response.data, timeout=300)
            
            return response

        return super().list(request, *args, **kwargs)


class ChatRateThrottle(UserRateThrottle):
    scope = 'chat'

class ChatStreamView(APIView):
    """
    Proxy view for Dify streaming chat.
    Saves user and AI messages to the database.
    """
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ChatRateThrottle]

    def post(self, request):
        query = request.data.get('query', '').strip()
        session_id = request.data.get('session_id')
        
        # Validation: check if query exists
        if not query:
            return Response({"error": "查詢內容不能為空"}, status=status.HTTP_400_BAD_REQUEST)

        # Validation: check maximum length (e.g., 2000 chars)
        MAX_QUERY_LENGTH = 500
        if len(query) > MAX_QUERY_LENGTH:
            return Response(
                {"error": f"查詢內容過長，最多 {MAX_QUERY_LENGTH} 字元"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validation: check for malicious/non-printable characters
        if re.search(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', query):
            return Response(
                {"error": "查詢內容包含不允許的字元"},
                status=status.HTTP_400_BAD_REQUEST
            )

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
            # Invalidate user sessions cache on creation
            logger.info(f"🔴 Invalidating cache for sessions (new session): user_{request.user.id}_sessions")
            cache.delete(f"user_{request.user.id}_sessions")

        # Save User Message
        ChatMessage.objects.create(session=session, role='USER', content=query)
        # Invalidate messages cache
        # Using the same user-scoped key: f"user_{user_id}_session_{session_id}_messages"
        logger.info(f"🔴 Invalidating cache for messages (new user msg): user_{request.user.id}_session_{session.id}_messages")
        cache.delete(f"user_{request.user.id}_session_{session.id}_messages")

        # Update session timestamp explicitly to ensure ordering
        session.save() 
        logger.info(f"🔴 Invalidating cache for sessions (session update): user_{request.user.id}_sessions")
        cache.delete(f"user_{request.user.id}_sessions")

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
                        
                        # Invalidate messages cache again for the AI response
                        # logger cannot be used comfortably inside generator unless we are sure about context, but yes we can.
                        # Note: StreamingHttpResponse runs in a separate context potentially? 
                        # Actually standard blocking generator runs in thread worker, logging is fine.
                        logger.info(f"🔴 Invalidating cache for messages (AI msg): user_{request.user.id}_session_{session.id}_messages")
                        cache.delete(f"user_{request.user.id}_session_{session.id}_messages")
                        
                        yield f"data: {json.dumps(chunk)}\n\n"
                    else:
                        yield f"data: {json.dumps(chunk)}\n\n"
            except Exception as e:
                logger.error(f"Chat Stream Error: {str(e)}", exc_info=True)
                yield f"data: {json.dumps({'event': 'error', 'message': '系統暫時無法處理您的請求，請稍後再試。'})}\n\n"

        return StreamingHttpResponse(stream_generator(), content_type='text/event-stream')
