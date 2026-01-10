# Dify ChatBot Backend (NTPU LawHelper)

這是一個基於 Django 框架開發的聊天機器人後端 API 服務，主要用於整合 Dify 平台，提供使用者驗證、聊天對話管理及訊息紀錄儲存等功能。本系統目前服務於 **NTPU LawHelper (北大法規問答小幫手)**，部分行動裝置可能無法使用單一登入。

## 專案結構 (Project Tree)

```text
.
├── apps/                   # Django 應用程式目錄
│   ├── accounts/           # 使用者帳號與驗證模組
│   │   ├── models/         # 使用者模型定義 (自訂 User)
│   │   ├── views.py        # 帳號相關 API 視圖 (Google Callback, Auth Status)
│   │   ├── authentication.py # 自定義 CookieJWTAuthentication
│   │   └── admin.py        # 管理介面設定
│   └── chat/               # 聊天功能模組
│       ├── models/         # 聊天相關模型 (Session, Message)
│       ├── views.py        # 聊天代理 (Streaming) 與 Session 管理 API
│       ├── serializers.py  # DRF 資料序列化
│       ├── admin.py        # 聊天紀錄管理介面
│       └── services/       # 服務層
│           └── dify.py     # Dify API 整合服務 (Streaming)
├── config/                 # 專案配置設定
│   ├── settings/           # 分層設定檔 (Base, Development, Production)
│   ├── urls.py             # 根路由設定
│   ├── wsgi.py             # WSGI 入口
│   └── asgi.py             # ASGI 入口 (目前主要使用 WSGI)
├── manage.py               # Django 管理腳本
├── pyproject.toml          # 專案依賴與工具設定 (使用 uv 管理)
├── uv.lock                 # uv 依賴鎖定檔
└── README.md               # 專案說明文件
```

---

## 系統設計 (System Architecture)

### 1. 安全的使用者認證 (High Security Auth)
*   **Google SSO**: 整合 `django-allauth` 提供 Google 帳號快速登入。
*   **HttpOnly Cookies**: 不同於傳統將 JWT 存放在 LocalStorage，本系統將 Access/Refresh Token 儲存於 **HttpOnly, Secure, SameSite** Cookies 中。這有效防禦了 XSS 攻擊，確保權限憑證不被惡意腳本讀取。
*   **自定義認證後端**: 透過 `CookieJWTAuthentication` 自動從 Cookie 中提取並驗證 JWT。

### 2. 聊天代理與串流 (Chat Proxy & Streaming)
*   **API 金鑰保護**: 前端不直接與 Dify 通訊，所有請求均由後端 `ChatStreamView` 代理，前端完全接觸不到 Dify API Key。
*   **即時串流 (SSE)**: 使用 `StreamingHttpResponse` 將 Dify 的 `text/event-stream` 回應即時轉發至前端，實現零延遲的打字機效果。
*   **自動持久化**: 後端在串流過程結束後，會自動將完整的 USER 訊息與 AI 回答存入資料庫，確保對話紀錄不遺失。

### 3. 多層級資料模型
*   **ChatSession**: 每一個對話獨立為一個 Session，並綁定一個 `dify_conversation_id` 以維持長期的對話上下文。
*   **ChatMessage**: 紀錄每筆訊息的角色（USER/AI/SYSTEM）、內容與時間。

---

## 重要檔案用途說明

| 檔案路徑 | 用途描述 |
| :--- | :--- |
| `apps/accounts/authentication.py` | 實作從 HttpOnly Cookie 讀取 JWT 的認證邏輯。 |
| `apps/accounts/views.py` | 處理 Google OAuth 回傳並核發 Cookie，以及提供 `/api/auth/status/` 供前端核對狀態。 |
| `apps/chat/models/session.py` | 管理聊天室對話，紀錄所屬使用者及對應的 Dify 會話 ID。 |
| `apps/chat/models/message.py` | 儲存每一條對話訊息的詳細內容與角色。 |
| `apps/chat/views.py` | 核心代理視圖 `ChatStreamView`，負責協調 Dify API 與資料庫儲存。 |
| `apps/chat/services/dify.py` | 封裝 Dify API 通訊邏輯，解析 SSE 串流封包。 |
| `config/settings/base.py` | 包含 Cookie 安全設定 (`COOKIE_SAMESITE`, `COOKIE_SECURE`) 及 CORS 設定。 |

---

## 開發指南

### 環境準備
本專案建議使用 [uv](https://github.com/astral-sh/uv) 進行依賴管理。

### 啟動服務
1.  安裝依賴: `uv sync`
2.  執行資料庫遷移: `python manage.py migrate`
3.  啟動開發伺服器: `python manage.py runserver`
4.  (選配) 使用 `python manage.py createsuperuser` 建立管理員以進入 `/admin` 查看紀錄。

