from django.shortcuts import render, redirect, get_object_or_404
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
from django.db import transaction

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
        logger.info(f"🔴 Invalidating cache for messages: user_{self.request.user.id}_session_{instance.id}_messages")
        cache.delete(f"user_{self.request.user.id}_session_{instance.id}_messages")
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
        Cache key: user_{user_id}_session_{session_id}_messages
        """
        session_id = request.query_params.get('session')
        
        if session_id:
            # Security Fix: Explicitly verify session ownership before ANY cache lookup.
            # This prevents accessing cache of another user if cache key construction fails
            # or if collision occurs, although we use user_id in key.
            # It mainly ensures we don't return cached data for a session the user lost access to.
            # Using get_object_or_404 triggers a DB call, which sounds counter-intuitive for caching?
            # HOWEVER, ChatSession lookup is very fast (PK index) compared to fetching all messages.
            # AND it is a necessary security gate.
            
            # Note: get_object_or_404(ChatSession, id=session_id, user=request.user)
            # If session doesn't exist or doesn't belong to user -> 404 immediately.
            try:
                # We use specific validation instead of get_object_or_404 to avoid HTML 404 in some setups if direct template
                # but DRF handles it fine. Let's use filter().first() to be safe and explicit or standard get().
                if not ChatSession.objects.filter(id=session_id, user=request.user).exists():
                     # If session invalid, standard logic would return empty list or 404 from get_queryset?
                     # get_queryset filters by user, so list() would return empty. 
                     # But here we want to STOP cache lookup.
                     pass 
                else:
                    # Session exists and belongs to user. Safe to proceed with cache lookup.
                    cache_key = f"user_{request.user.id}_session_{session_id}_messages"
                    cached_data = cache.get(cache_key)
                    if cached_data is not None:
                        logger.info(f"🟢 Cache HIT for messages: {cache_key}")
                        return Response(cached_data)

                    logger.info(f"🟡 Cache MISS for messages: {cache_key} - Fetching from DB")
            except Exception:
                # In case of UUID format error etc, fall through to standard processing
                pass

            response = super().list(request, *args, **kwargs)
            
            # Only cache if response is successful
            if response.status_code == 200:
                # Re-verify we constructed the key correctly if we reached here
                cache_key = f"user_{request.user.id}_session_{session_id}_messages"
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

        # Save User Message with transaction check
        # Robustness Fix: Use transaction.on_commit to ensure cache deletion happens ONLY after DB commit.
        # This prevents "stale cache" where delete happens but DB write fails (rare but possible),
        # or more importantly, ensures race condition where next read happens before DB commit is finalized.
        with transaction.atomic():
            ChatMessage.objects.create(session=session, role='USER', content=query)
            # Invalidate messages cache
            cache_key_msg = f"user_{request.user.id}_session_{session.id}_messages"
            # Invalidate sessions cache (update timestamp)
            cache_key_session = f"user_{request.user.id}_sessions"

            # Log first
            logger.info(f"🔴 Schuduling cache invalidation for: {cache_key_msg} & {cache_key_session}")

            # Schedule invalidation
            transaction.on_commit(lambda: cache.delete(cache_key_msg))
            
            # Explicitly save session to update timestamp
            session.save() 
            transaction.on_commit(lambda: cache.delete(cache_key_session))


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
                        # Wrap DB updates in atomic block
                        with transaction.atomic():
                            if dify_conv_id and not session.dify_conversation_id:
                                session.dify_conversation_id = dify_conv_id
                                session.save()
                            
                            # Save AI Message
                            ChatMessage.objects.create(session=session, role='AI', content=full_answer)
                            
                            cache_key_ai_msg = f"user_{request.user.id}_session_{session.id}_messages"
                            logger.info(f"🔴 Schuduling cache invalidation for (AI msg): {cache_key_ai_msg}")
                            transaction.on_commit(lambda: cache.delete(cache_key_ai_msg))
                        
                        yield f"data: {json.dumps(chunk)}\n\n"
                    else:
                        yield f"data: {json.dumps(chunk)}\n\n"
            except Exception as e:
                logger.error(f"Chat Stream Error: {str(e)}", exc_info=True)
                yield f"data: {json.dumps({'event': 'error', 'message': '系統暫時無法處理您的請求，請稍後再試。'})}\n\n"

        return StreamingHttpResponse(stream_generator(), content_type='text/event-stream')
