import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.test import Client

@pytest.fixture
def api_client():
    """
    提供 Django Rest Framework 的 APIClient 實例，
    用於測試 API 請求。
    """
    return APIClient()

@pytest.fixture
def create_test_user(db):
    """
    建立測試使用者的工廠函數 (Factory Function)。
    使用方法: user = create_test_user(email="test@example.com")
    """
    def make_user(**kwargs):
        User = get_user_model()
        if 'email' not in kwargs:
            kwargs['email'] = 'test@example.com'
        if 'username' not in kwargs:
            kwargs['username'] = kwargs['email'].split('@')[0]
        if 'password' not in kwargs:
            kwargs['password'] = 'password123'
        return User.objects.create_user(**kwargs)
    return make_user

@pytest.fixture
def auto_login_user(db, create_test_user):
    """
    建立一個已透過 session 登入的使用者。
    這模擬了使用者在 Google 登入後，Redirect 回到我們先前的狀態（或者是已登入狀態）。
    返回 (client, user) tuple。
    """
    user = create_test_user()
    client = Client()
    client.force_login(user)
    return client, user

@pytest.fixture(autouse=True)
def mock_dify_service(monkeypatch):
    """
    自動 Mock DifyService，避免測試時需要真實的 API Key 或連線外部伺服器。
    """
    from apps.chat.services.dify import DifyService
    
    def mocked_stream_chat(self, query, user_id, conversation_id=None):
        # 模擬 Dify 的流式回覆格式
        yield {"event": "message", "answer": "這是一個模擬的 AI 回應：", "conversation_id": "mock-conv-id"}
        yield {"event": "message", "answer": f"您剛剛說了「{query}」", "conversation_id": "mock-conv-id"}
        yield {"event": "message_end", "conversation_id": "mock-conv-id"}
        
    monkeypatch.setattr(DifyService, "stream_chat", mocked_stream_chat)
