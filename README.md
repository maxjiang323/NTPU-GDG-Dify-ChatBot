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
│   │   ├── exceptions.py   # 自訂錯誤處理器 (生產環境資訊遮蔽)
│   │   └── admin.py        # 管理介面設定
│   └── chat/               # 聊天功能模組
│       ├── models/         # 聊天相關模型 (Session, Message)
│       ├── views.py        # 聊天代理 (Streaming) 與 Session 管理 API
│       ├── serializers.py  # DRF 資料序列化
│       ├── admin.py        # 聊天紀錄管理介面
│       └── services/       # 服務層
│           └── dify.py     # Dify API 整合服務 (Streaming)
├── config/                 # 專案配置設定
│   ├── settings/           # 分層設定檔
│   │   ├── base.py         # 共用基礎設定
│   │   ├── development.py  # 開發環境 (DEBUG=True, 保留 DRF 可瀏覽介面)
│   │   └── production.py   # 生產環境 (安全強化, 禁用可瀏覽 API)
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
*   **Google SSO (Redirect Flow)**: 從 One-Tap/Popup 模式切換為更穩定的 **Authorization Code (Redirect) Flow**。前端取得授權碼後由後端直接與 Google 交換 Token，解決了工業級瀏覽器（包含行動裝置與 strict COOP 設定）對彈窗的封鎖問題。支援網域限制 (`ALLOWED_EMAIL_DOMAINS`) 確保僅授權帳號可進入系統。
*   **JWT 進階安全**: 
    - **Token 黑名單與輪轉**: 啟用 `SimpleJWT` 的 Token 黑名單 (Blacklist) 與旋轉 (Rotation) 機制。當 Refresh Token 被使用時，會簽發新的並將舊的作廢，降低 Token 遭竊取的風險。
    - **動態效期控制**: 同步 Access Token 效期為 1 小時，Refresh Token 效期為 1 天，平衡安全性與使用者體驗。
*   **HttpOnly Cookies**: 不同於傳統將 JWT 存放在 LocalStorage，本系統將 Access/Refresh Token 儲存於 **HttpOnly, Secure, SameSite** Cookies 中。這有效防禦了 XSS 攻擊，確保權限憑證不被惡意腳本讀取。
*   **CSRF 防護機制**: 針對 Cookie-based 認證實作了強制的 CSRF 檢查。
    *   **CSRF Cookie 安全強化**: 設定 `CSRF_COOKIE_HTTPONLY = True`，防止 CSRF Token 被 JavaScript 讀取。
    *   **記憶體共享 Token**: 透過 `/api/auth/status/` 的回應夾帶 `csrfToken` 字串，供前端安全地傳遞檢查碼。
*   **自定義認證後端**: 透過 `CookieJWTAuthentication` 自動從 Cookie 中提取並驗證 JWT，並結合 CSRF 驗證邏輯。

### 2. 聊天代理與串流 (Chat Proxy & Streaming)
*   **API 金鑰保護**: 前端不直接與 Dify 通訊，所有請求均由後端 `ChatStreamView` 代理，前端完全接觸不到 Dify API Key。
*   **即時串流 (SSE)**: 使用 `StreamingHttpResponse` 將 Dify 的 `text/event-stream` 回應即時轉發至前端，實現零延遷的打字機效果。
*   **流量控制 (Rate Limiting)**: 針對 Chat API 實作每分鐘 20 次的請求限制 (`UserRateThrottle`)，防止惡意腳本消耗系統資源或產生過多 LLM 費用。
*   **輸入內容驗證**：在 `ChatStreamView` 實作嚴格的輸入驗證，限制查詢長度（最大 500 字元）並過濾不安全字元，預防注入攻擊。
*   **強健性與超時處理**: 
    - **Timeout 限制**: 連線 5s / 讀取 30s，防止 Dify 服務異常導致後端掛起。
    - **安全錯誤處理**: 發生異常時，後端詳細日誌 (Logging) 紀錄堆棧資訊，但僅回傳通用錯誤訊息給前端，防止內部架構資訊洩露。
*   **自動持久化**: 後端採取「先存問題、後串流、再存回答」的策略。即使 Dify API 回傳錯誤，使用者的原始問題 (USER role) 也會被優先保留於資料庫，確保紀錄完整性。

### 3. 環境分離與生產安全強化 (Environment-Specific Security)

本系統採用 **開發/生產分離設定**，確保開發便利性與生產安全性的平衡：

#### 開發環境 (`development.py`)
*   **DEBUG 模式**: 啟用詳細錯誤追蹤，方便除錯
*   **DRF 可瀏覽 API**: 保留 `BrowsableAPIRenderer`，提供友善的 API 測試介面
*   **詳細錯誤訊息**: 完整顯示堆疊追蹤與錯誤細節

#### 生產環境 (`production.py`)
*   **禁用 DRF 可瀏覽 API**: 只保留 `JSONRenderer`，防止 API 結構與欄位資訊洩露
*   **自訂錯誤處理器** (`custom_exception_handler`):
    - **內部詳細日誌**: 完整記錄錯誤堆疊、請求資訊到後端日誌
    - **外部通用訊息**: 只返回通用的中文錯誤訊息給前端（如「未授權，請先登入」）
    - **防止資訊洩露**: 避免暴露內部架構、資料庫結構或敏感配置
*   **安全 Headers 強化**:
    - `SECURE_HSTS_SECONDS`: 啟用 HSTS (1 年)，強制 HTTPS
    - `SECURE_CONTENT_TYPE_NOSNIFF`: 防止 MIME 類型嗅探攻擊
    - `X_FRAME_OPTIONS`: 設為 DENY，防止 Clickjacking 攻擊
    - `SECURE_HSTS_PRELOAD`: 允許加入瀏覽器 HSTS preload list

**安全效果對比**:
```
開發環境訪問 /api/auth/status/
→ 顯示 DRF 可瀏覽介面，包含 API 文檔、欄位說明、詳細錯誤

生產環境訪問 /api/auth/status/
→ 只返回 JSON：{"error": "未授權，請先登入", "status_code": 401}
→ 詳細錯誤只記錄在後端日誌，外部無法存取
```

### 4. 多層級資料模型
*   **ChatSession**: 每一個對話獨立為一個 Session，並綁定一個 `dify_conversation_id` 以維持長期的對話上下文。
*   **ChatMessage**: 紀錄每筆訊息的角色（USER/AI/SYSTEM）、內容與時間。

### 5. 效能優化與快取 (Performance & Caching)
*   **Redis 快取機制**: 使用 Redis 作為快取後端 (`django-redis`)。
    *   **對話記錄快取**: 針對使用者的 Session 列表與單一 Session 的訊息記錄進行快取 (TTL 5分鐘)，大幅減少資料庫查詢負擔。
    *   **Rate Limiting**: 同時作為 DRF Throttle 的後端儲存，高效追踪 API 請求頻率。

---

## 重要檔案用途說明

| 檔案路徑 | 用途描述 |
| :--- | :--- |
| `apps/accounts/authentication.py` | 實作從 HttpOnly Cookie 讀取 JWT 的認證邏輯。 |
| `apps/accounts/exceptions.py` | 自訂 DRF 錯誤處理器，生產環境中隱藏敏感資訊，只返回通用錯誤訊息。 |
| `apps/accounts/views.py` | 處理 Google OAuth 成功後的「認證橋接」，核發 Cookie 並提供登出 API。 |
| `apps/accounts/views.py (LogoutView)` | API 登出入口，負責發送指令叫瀏覽器清除 HttpOnly Cookies。 |
| `apps/chat/models/session.py` | 管理聊天室對話，紀錄所屬使用者及對應的 Dify 會話 ID。 |
| `apps/chat/models/message.py` | 儲存每一條對話訊息的詳細內容與角色。 |
| `apps/chat/views.py` | 核心代理視圖 `ChatStreamView`，負責協調 Dify API 與資料庫儲存。 |
| `apps/chat/services/dify.py` | 封裝 Dify API 通訊邏輯，解析 SSE 串流封包 |
| `config/settings/base.py` | 共用基礎設定，包含安全設定、Cookie 安全原則與全域 CSRF 策略。 |
| `config/settings/development.py` | 開發環境設定，啟用 DEBUG 與 DRF 可瀏覽 API。 |
| `config/settings/production.py` | 生產環境設定，禁用可瀏覽 API、啟用錯誤遮蔽與安全 Headers。 |

---

## 開發指南

### 環境準備
本專案建議使用 [uv](https://github.com/astral-sh/uv) 進行依賴管理。

### 啟動服務
1.  安裝依賴: `uv sync`
2.  執行資料庫遷移: `python manage.py migrate`
3.  啟動開發伺服器: `python manage.py runserver`
4.  (選配) 使用 `python manage.py createsuperuser` 建立管理員以進入 `/admin` 查看紀錄。

