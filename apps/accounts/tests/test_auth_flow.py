import pytest
from django.urls import reverse
from rest_framework import status
from apps.accounts.views import AuthStatusView

@pytest.mark.django_db
class TestAuthFlow:
    """
    測試 Authentication 相關流程，包含 AuthStatus, Login Callback, Logout。
    """

    def test_auth_status_unauthenticated(self, api_client):
        """
        測試未登入使用者存取 /auth/status 應回傳 401。
        """
        url = reverse('auth_status')  # 假設 urls.py 中有 name='auth_status'
        # 如果沒有 name，請使用實際路徑，例如 '/api/auth/status/'
        # 這裡我們先假設路徑為 '/api/auth/status/' 如果 reverse 失敗
        try:
            url = reverse('auth_status')
        except:
            url = '/api/auth/status/'
            
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()['code'] == 'not_authenticated'

    def test_google_login_callback_simulation(self, auto_login_user):
        """
        測試 Google Login Callback。
        情境：使用者已經通過 Google 驗證 (由 auto_login_user 模擬 session 登入)，
        然後被 redirect 回 /api/auth/google/callback/。
        
        預期：
        1. Server 應回傳 302 Redirect 到前端 /chat。
        2. Set-Cookie 應包含 access_token 和 refresh_token。
        """
        client, user = auto_login_user
        # 假設 callback url 為 /api/auth/google/success/
        # 請根據實際 urls.py 調整
        url = '/api/auth/google/success/' 
        
        response = client.get(url)
        
        assert response.status_code == 302
        assert response.url == '/chat'
        
        # 驗證 Cookies
        assert 'access_token' in response.cookies
        assert 'refresh_token' in response.cookies
        
        # 驗證 Cookie 屬性 (安全考量)
        access_token_cookie = response.cookies['access_token']
        assert access_token_cookie['httponly'] is True
        # secure 在測試環境可能為 False，除非 settings.COOKIE_SECURE = True
        
    def test_logout(self, api_client):
        """
        測試登出功能，應清除 cookies。
        """
        url = '/api/auth/logout/' # 假設登出路徑
        response = api_client.post(url)
        
        assert response.status_code == 200
        
        # 驗證 Cookies 已過期 (即清除)
        # Django 刪除 cookie 通常是將 max-age 設為 0 或 expires 設為過去時間
        assert response.cookies['access_token'].value == ''
        assert response.cookies['refresh_token'].value == ''

    def test_google_login_restricted_domain_direct_test(self, db):
        """
        測試 Adapter 是否會正確擋下非指定網域的 Email。
        """
        from apps.accounts.adapters import CustomSocialAccountAdapter
        from allauth.core.exceptions import ImmediateHttpResponse
        from types import SimpleNamespace
        
        adapter = CustomSocialAccountAdapter()
        
        # 模擬一個非法網域的請求
        bad_sociallogin = SimpleNamespace(user=SimpleNamespace(email="attacker@gmail.com"))
        
        # 預期會拋出 ImmediateHttpResponse (Allauth 的攔截機制)
        with pytest.raises(ImmediateHttpResponse) as excinfo:
            adapter.pre_social_login(None, bad_sociallogin)
        
        # 驗證重定向的路徑是否包含錯誤代碼
        response = excinfo.value.response
        assert response.status_code == 302
        assert "err_code=DOMAIN_RESTRICTED" in response.url

    def test_google_login_allowed_domain_direct_test(self, db):
        """
        測試 Adapter 是否會允許正確網域的 Email。
        """
        from apps.accounts.adapters import CustomSocialAccountAdapter
        from types import SimpleNamespace
        
        adapter = CustomSocialAccountAdapter()
        
        # 模擬一個正確網域的請求
        good_sociallogin = SimpleNamespace(user=SimpleNamespace(email="student@gm.ntpu.edu.tw"))
        
        # 預期不會拋出任何異常 (順利通過)
        adapter.pre_social_login(None, good_sociallogin)
