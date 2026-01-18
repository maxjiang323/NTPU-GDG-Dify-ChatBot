from pathlib import Path
import os
from dotenv import load_dotenv
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')


ENV = os.getenv("DJANGO_ENV", "local")  # local / staging / production

if ENV == "local":
    COOKIE_SECURE = False
    COOKIE_SAMESITE = "Lax"
else:
    COOKIE_SECURE = True
    COOKIE_SAMESITE = "None"

# CSRF Cookie 不讓 js 讀取，因為已經透過 /api/auth/status 來驗證並設定
CSRF_COOKIE_HTTPONLY =True

# CSRF Cookie 設定，跟隨環境變數 (local/prod)
CSRF_COOKIE_SECURE = COOKIE_SECURE
CSRF_COOKIE_SAMESITE = COOKIE_SAMESITE

# Session Cookie 設定，跟隨環境變數 (local/prod)
SESSION_COOKIE_SECURE = COOKIE_SECURE
SESSION_COOKIE_SAMESITE = COOKIE_SAMESITE

ALLOWED_HOSTS = [x.strip() for x in os.getenv('ALLOWED_HOSTS').split(',') if x.strip()]

CORS_ALLOWED_ORIGINS = [x.strip() for x in os.getenv('CORS_ALLOWED_ORIGINS').split(',') if x.strip()]

CSRF_TRUSTED_ORIGINS = [x.strip() for x in os.getenv('CSRF_TRUSTED_ORIGINS').split(',') if x.strip()]

CORS_ALLOW_CREDENTIALS = True

# Application definition

INSTALLED_APPS = [
    # 'daphne',  # 不需要非同步功能，故移除
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # allauth 需要
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',

    # startapp 之後都要到這邊新增 app
    'apps.accounts', # 新增 accounts 這個 app
    'apps.chat', # 新增 chat 這個 app   

    # allauth 相關
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',  # Google 登入
]

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    # Django 預設的認證後端
    'django.contrib.auth.backends.ModelBackend',

    # allauth 的認證後端 (支援社交登入)
    'allauth.account.auth_backends.AuthenticationBackend',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ← 加在這裡 (SecurityMiddleware 之後)
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # ← 加在這裡！allauth 必要的 middleware
]


ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,  # 讓 Django 自動尋找每個 app 下的 templates/ 目錄
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'zh-hant'

TIME_ZONE = 'Asia/Taipei'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# 靜態檔案設定
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # ← 新增:收集後的靜態檔案存放位置

# Whitenoise 設定
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",  # ← 使用 Whitenoise
    },
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 自訂使用者模型
AUTH_USER_MODEL = 'accounts.User'


# allauth 設定
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'  # 允許使用 username 或 email 登入
ACCOUNT_EMAIL_REQUIRED = True  # 註冊時必須填寫 email
ACCOUNT_EMAIL_VERIFICATION = 'optional'  # email 驗證為選填 (可改為 'mandatory' 強制驗證)
ACCOUNT_USERNAME_REQUIRED = False  # 社交登入不需要 username，使用 email 即可
LOGIN_REDIRECT_URL = '/api/auth/google/success/'  # 登入後導向至生成 JWT 的 API 端點
LOGOUT_REDIRECT_URL = '/'  # 登出後導向首頁

# 社交登入設定
SOCIALACCOUNT_AUTO_SIGNUP = True  # 使用社交登入時自動建立帳號
SOCIALACCOUNT_QUERY_EMAIL = True  # 向社交平台請求 email
SOCIALACCOUNT_LOGIN_ON_GET = True  # 直接重定向到 OAuth 頁面，跳過中間確認頁面
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True  # 允許使用 email 進行社交帳號認證
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True  # 自動連結相同 email 的既有帳號

# Google OAuth 設定：指定要取得的資訊範圍
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',  # 取得個人資料（名字、頭像等）
            'email',    # 取得 email
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',  # 不需要 refresh token
            'prompt': 'select_account', # 強制顯示帳號選擇器
        },
        'FETCH_USERINFO': True,  # 從 Google 取得用戶資訊
    }
}


# ==========================================
# Cache 設定 - 使用 Redis
# ==========================================
REDIS_URI = os.getenv('REDIS_URI', 'redis://127.0.0.1:6379/1')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URI,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'library',  # 所有 key 都會加上這個前綴
        'TIMEOUT': 300,  # 預設快取時間 5 分鐘（單位：秒）
    }
}

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'apps.accounts.authentication.CookieJWTAuthentication',
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
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True, # 每次登入都產生新的 refresh token
    'BLACKLIST_AFTER_ROTATION': True, # 登出時將舊的 refresh token 加入黑名單
    'AUTH_HEADER_TYPES': ('Bearer',),
}

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
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.chat': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
