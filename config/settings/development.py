from .base import *

# 開發環境設定
DEBUG = True

# 開發環境使用 SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# 開發環境允許使用 DRF 可瀏覽 API 介面（方便除錯）
REST_FRAMEWORK = {
    **REST_FRAMEWORK,  # 繼承 base.py 的設定（認證、權限、Throttle 等）
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # 開發環境保留可瀏覽介面
    ],
    # 顯式宣告以通過 Semgrep 靜態掃描（實際值已由 base.py 繼承）
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '100/min',
        'chat': '20/min',
    },
}