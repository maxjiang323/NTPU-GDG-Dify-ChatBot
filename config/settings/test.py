from .base import *

# 測試環境專用設定
# 使用 SQLite 記憶體資料庫以加快測試速度
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# 測試用的 Secret Key
SECRET_KEY = 'test-secret-key-for-pytest'

# 限制測試環境的 Email 後綴
ALLOWED_EMAIL_DOMAINS = ["gm.ntpu.edu.tw"]

# 測試時不使用 Redis，改用 DummyCache 或 LocMemCache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# 測試時可能不需要 WhiteNoise 處理靜態檔，可選
# STORAGES = ... 

# 確保在測試中 Email 不會真的寄出
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# 解決 Playwright/pytest-asyncio 在同個執行緒跑同步資料庫操作時的 SynchronousOnlyOperation 錯誤
import os
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

# 匯入專屬測試環境的 REST_FRAMEWORK 設定
# 這裡採直接定義而非繼承，是為了確保 SAST 掃描能正確識別 Throttle 配置，並移除不必要的 Renderer
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'apps.accounts.authentication.CookieJWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.UserRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'user': '100/min',
        'chat': '20/min',
    },
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}
