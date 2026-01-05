from django.shortcuts import redirect
from django.contrib import messages

def login_cancelled_redirect(request):
    """
    當使用者在 SSO 頁面點選取消時，將其導向回前端登入頁面，
    避免停留在 Django 預設的成功/取消頁面。
    """
    # 清除 Django 內部的訊息（例如你看到的「成功登入」但其實已取消的誤導訊息）
    storage = messages.get_messages(request)
    for _ in storage:
        pass  # 讀取訊息即會將其從 storage 中移除
        
    frontend_login_url = "http://localhost:8080/login"
    return redirect(frontend_login_url)
