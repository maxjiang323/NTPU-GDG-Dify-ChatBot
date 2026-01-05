from .base import *
import os
from dotenv import load_dotenv
import dj_database_url

# 載入 .env 檔案 (如果存在)
load_dotenv()

DEBUG = False

# 從環境變數讀取允許的主機
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

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
CSRF_TRUSTED_ORIGINS = ["https://tnt-management.zeabur.app"]  # 根據你的 Zeabur 應用程式 URL 設定