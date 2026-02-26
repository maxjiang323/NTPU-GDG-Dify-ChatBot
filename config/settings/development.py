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
REST_FRAMEWORK = { # nosemgrep: python.django.security.audit.django-rest-framework.missing-throttle-config.missing-throttle-config
    **REST_FRAMEWORK,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # 開發環境保留可瀏覽介面
    ],
}