import pytest
from playwright.sync_api import Page, expect
from django.test import Client

@pytest.mark.django_db
def test_chat_reply_flow_e2e(page: Page, live_server, create_test_user):
    # 1. 建立使用者
    user = create_test_user(email="chat_user@example.com")
    
    # 2. 使用 Django Client 登入
    client = Client()
    client.force_login(user)
    sessionid = client.cookies['sessionid'].value
    
    # 3. 先訪問 callback URL 來設定 JWT
    # 像 test_login_flow.py 一樣
    callback_url = f"{live_server.url}/api/auth/google/success/"
    
    # 注入 sessionid 到 Playwright
    page.context.add_cookies([
        {
            "name": "sessionid",
            "value": sessionid,
            "domain": "localhost",
            "path": "/",
        }
    ])
    
    # 訪問 callback URL 以設定 JWT
    page.goto(callback_url)
    
    # 等待轉址到 chat 頁面
    expect(page).to_have_url(f"{live_server.url}/chat")
    
    # 4. 現在可以進行聊天測試
    # 先鎖定 <main> 區域，確保我們是在操作「聊天室」而不是「側邊欄」
    chat_area = page.get_by_role("main")
    
    # 在聊天區域內尋找輸入框（假設為 input 或 textarea）
    # 使用 regex 匹配 placeholder 包含「輸入」的欄位
    import re
    input_field = chat_area.get_by_placeholder(re.compile(r"輸入"))
    
    input_field.wait_for()
    input_field.fill("你好，這是一個測試訊息")
    input_field.press("Enter")
    
    # 5. 驗證
    # 同樣在 chat_area 內驗證，避免抓到側邊欄剛更新的摘要
    expect(chat_area.get_by_text("你好，這是一個測試訊息")).to_be_visible()
    expect(chat_area.get_by_text("這是一個模擬的 AI 回應")).to_be_visible(timeout=10000)
