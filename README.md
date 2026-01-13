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
*   **CSRF 防護機制**: 針對 Cookie-based 認證實作了強制的 CSRF 檢查。
    *   **記憶體共享 Token**: 考慮到跨網域 (Cross-origin) 環境下 JavaScript 無法讀取 Cookie 的限制，後端在 `/api/auth/status/` 的回應中會夾帶 `csrfToken` 字串，供前端儲存於記憶體變數中使用。
*   **自定義認證後端**: 透過 `CookieJWTAuthentication` 自動從 Cookie 中提取並驗證 JWT，並結合 CSRF 驗證邏輯。

### 2. 聊天代理與串流 (Chat Proxy & Streaming)
*   **API 金鑰保護**: 前端不直接與 Dify 通訊，所有請求均由後端 `ChatStreamView` 代理，前端完全接觸不到 Dify API Key。
*   **即時串流 (SSE)**: 使用 `StreamingHttpResponse` 將 Dify 的 `text/event-stream` 回應即時轉發至前端，實現零延遷的打字機效果。
*   **流量控制 (Rate Limiting)**: 針對 Chat API 實作每分鐘 20 次的請求限制 (`UserRateThrottle`)，防止惡意腳本消耗系統資源或產生過多 LLM 費用。
*   **強健性與超時處理**: 
    - **Timeout 限制**: 連線 5s / 讀取 30s，防止 Dify 服務異常導致後端掛起。
    - **安全錯誤處理**: 發生異常時，後端詳細日誌 (Logging) 紀錄堆棧資訊，但僅回傳通用錯誤訊息給前端，防止內部架構資訊洩露。
*   **自動持久化**: 後端採取「先存問題、後串流、再存回答」的策略。即使 Dify API 回傳錯誤，使用者的原始問題 (USER role) 也會被優先保留於資料庫，確保紀錄完整性。

### 3. 多層級資料模型
*   **ChatSession**: 每一個對話獨立為一個 Session，並綁定一個 `dify_conversation_id` 以維持長期的對話上下文。
*   **ChatMessage**: 紀錄每筆訊息的角色（USER/AI/SYSTEM）、內容與時間。

---

## 重要檔案用途說明

| 檔案路徑 | 用途描述 |
| :--- | :--- |
| `apps/accounts/authentication.py` | 實作從 HttpOnly Cookie 讀取 JWT 的認證邏輯。 |
| `apps/accounts/views.py` | 處理 Google OAuth 成功後的「認證橋接」，核發 Cookie 並提供登出 API。 |
| `apps/accounts/views.py (LogoutView)` | API 登出入口，負責發送指令叫瀏覽器清除 HttpOnly Cookies。 |
| `apps/chat/models/session.py` | 管理聊天室對話，紀錄所屬使用者及對應的 Dify 會話 ID。 |
| `apps/chat/models/message.py` | 儲存每一條對話訊息的詳細內容與角色。 |
| `apps/chat/views.py` | 核心代理視圖 `ChatStreamView`，負責協調 Dify API 與資料庫儲存。 |
| `apps/chat/services/dify.py` | 封裝 Dify API 通訊邏輯，解析 SSE 串流封包 |
| `config/settings/base.py` | 包含安全設定、Cookie 安全原則與全域 CSRF 策略。 |

---

## 開發指南

### 環境準備
本專案建議使用 [uv](https://github.com/astral-sh/uv) 進行依賴管理。

### 啟動服務
1.  安裝依賴: `uv sync`
2.  執行資料庫遷移: `python manage.py migrate`
3.  啟動開發伺服器: `python manage.py runserver`
4.  (選配) 使用 `python manage.py createsuperuser` 建立管理員以進入 `/admin` 查看紀錄。

