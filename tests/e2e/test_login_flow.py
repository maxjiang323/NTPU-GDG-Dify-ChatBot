import pytest
from playwright.sync_api import Page, expect
from django.test import Client

@pytest.mark.django_db
def test_google_login_flow_e2e(page: Page, live_server, create_test_user):
    """
    E2E 測試：模擬 Google SSO 登入流程。
    
    測試策略：
    我們不真正的去點擊 Google 登入按鈕 (因為那會跳轉到外部 Google 頁面，且需要真實帳號)，
    而是模擬「已經在 Google 完成驗證並被導回」的狀態。
    
    步驟：
    1. 建立測試使用者。
    2. 使用 Django Test Client 預先登入該使用者 (產生 session)。
    3. 將 Django session cookie 注入到 Playwright 的瀏覽器 context 中。
    4. 讓 Playwright 瀏覽器存取 Google Login Callback URL。
    5. 驗證是否成功轉址到 /chat 並且 UI 顯示正確內容。
    """
    
    # 1. 建立使用者
    user = create_test_user(email="e2e_user@example.com")
    
    # 2. 透過 Django Client 登入以取得 sessionid
    client = Client()
    client.force_login(user)
    sessionid = client.cookies['sessionid'].value
    
    # 3. 注入 sessionid 到 Playwright
    # live_server.url 包含 http://localhost:port
    page.context.add_cookies([
        {
            "name": "sessionid",
            "value": sessionid,
            "domain": "localhost", # live_server 預設通常是 localhost
            "path": "/",
        }
    ])
    
    # 計算 Callback URL (需加上 live_server 的 host:port)
    callback_url = f"{live_server.url}/api/auth/google/success/"
    
    # 4. 訪問 Callback URL
    # 這會觸發後端的 GoogleLoginCallback View，該 View 會檢查 session，
    # 發現使用者已登入，然後發發 JWT 並轉址。
    page.goto(callback_url)
    
    # 5. 驗證轉址與結果
    # 預期轉址到前端頁面 (但在測試環境中，前端頁面可能不存在或由 Django static 服務)
    # 這裡我們主要驗證 URL 是否改變，以及 cookies 是否被設定
    
    # 等待 URL 變更 (至少不應該停留在 callback 頁面)
    # 假設前端路由是 /chat
    expect(page).to_have_url(f"{live_server.url}/chat")
    
    # 如果這是真正的整合測試且前端有被 serve，我們可以檢查 UI
    # expect(page.locator("text=e2e_user")).to_be_visible()
    
    # 檢查瀏覽器 Cookies 是否包含 access_token
    cookies = page.context.cookies()
    cookie_names = [c['name'] for c in cookies]
    assert 'access_token' in cookie_names
    assert 'refresh_token' in cookie_names
