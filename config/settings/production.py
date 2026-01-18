from .base import *
import os
import dj_database_url

DEBUG = False

# 資料庫設定
# Zeabur 會自動注入 POSTGRES_CONNECTION_STRING
postgres_connection_string = os.getenv('POSTGRES_CONNECTION_STRING')

if postgres_connection_string:
    # 在 Zeabur 上使用 PostgreSQL
    DATABASES = {
        'default': dj_database_url.parse(
            postgres_connection_string,
            conn_max_age=600  # 連線池:連線最多保持 600 秒
        )
    }
else:
    # 本地開發使用 SQLite (fallback)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# 生產環境安全設定
# SECURE_SSL_REDIRECT = True  # 強制使用 HTTPS，使用 Nginx 在內網使用 http，需要把這行註解掉
SESSION_COOKIE_SECURE = True  # Cookie 只能透過 HTTPS 傳輸
CSRF_COOKIE_SECURE = True  # CSRF Cookie 只能透過 HTTPS 傳輸

# 信任 Zeabur 的代理伺服器
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ==========================================
# DRF 安全設定 - 生產環境
# ==========================================
REST_FRAMEWORK = {
    **REST_FRAMEWORK,  # 繼承 base.py 的設定
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',  # 只允許 JSON 輸出，禁用可瀏覽 API
    ],
    'EXCEPTION_HANDLER': 'apps.accounts.exceptions.custom_exception_handler',  # 自訂錯誤處理
}

# 額外的安全 Headers
SECURE_HSTS_SECONDS = 31536000  # 啟用 HSTS (1 年)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True  # 防止 MIME 類型嗅探
X_FRAME_OPTIONS = 'DENY'  # 防止 Clickjacking 攻擊

# ==========================================
# Logging 設定 - 生產環境
# ==========================================
# 覆蓋 base.py 的設定，只記錄 WARNING 以上的訊息
# 這樣一來，Console 就不會出現大量的 Cache HIT/MISS 資訊，只會保留錯誤日誌
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',  # 只記錄 WARNING, ERROR, CRITICAL
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'apps.chat': {
            'handlers': ['console'],
            'level': 'WARNING',  # 這裡也設為 WARNING，隱藏 INFO 級別的快取日誌
            'propagate': False,
        },
    },
}