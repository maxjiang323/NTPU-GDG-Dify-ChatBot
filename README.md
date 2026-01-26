# Dify ChatBot Backend (NTPU LawHelper)

這是一個基於 Django 框架開發的聊天機器人後端 API 服務，主要用於整合 Dify 平台，提供使用者驗證、聊天對話管理及訊息紀錄儲存等功能。本系統目前服務於 **NTPU LawHelper (北大法規問答小幫手)**。

**🎉 前後端已整合：React 前端與 Django 後端共享同一部署環境，無需分開部署。**

**上屆使用的聊天機器人前端專案 (Lovable)**
**URL**: https://lovable.dev/projects/143b11e0-fb4c-47b9-b578-7c14f8113770

---

## 快速開始

### 環境需求

- Python 3.12+
- Node.js 16+ (前端開發)
- PostgreSQL 或 SQLite (開發環境)
- Redis (快取與 Token 黑名單)

### 開發環境運行 (前後端合併)

#### 1. 後端啟動

```bash
# 克隆專案
git clone <repository>
cd Dify-ChatBot-Backend

# 安裝依賴 (使用 uv 或 pip)
uv pip install -r requirements.txt
# 或
pip install -r requirements.txt

# 設定環境變數
cp .env.example .env
# 編輯 .env，填入必要配置 (Dify API Key, ALLOWED_EMAIL_DOMAINS 等)
# 確保 DJANGO_ENV=local (開發環境)

# 資料庫遷移
python manage.py migrate

# 建立超級使用者 (可選)
python manage.py createsuperuser

# 開發模式運行後端
python manage.py runserver
# 後端服務器在 http://localhost:8000
```

#### 2. 前端啟動 (另開終端)

```bash
cd frontend/Dify-ChatBot-V2

# 安裝前端依賴
npm install

# 開發模式
npm run dev
# 前端開發伺服器在 http://localhost:8080

# 注意：Vite 開發伺服器會將 /api 請求代理至後端 (http://localhost:8000/api)
```

---

## 自動化測試 (Testing)

本專案建立了完善的測試架構，包含後端單元測試與前端 E2E 整合測試。

### 1. 測試環境設定

```bash
# 安裝測試相依套件 (由 uv 自動管理)
uv sync --dev

# 安裝瀏覽器相關系統依賴 (僅 Linux/WSL 需要)
sudo .venv/bin/playwright install-deps
```

### 2. 執行測試

```bash
# 執行所有測試並查看覆蓋率摘要
pytest

# 生成詳細的網頁版覆蓋率報告 (htmlcov/)
pytest --cov=apps --cov-report=html

# 執行 E2E 測試並觀看瀏覽器操作畫面 (僅限支援 GUI 環境)
pytest tests/e2e/ --headed
```

### 3. CI/CD 持續整合

專案整合了 **GitHub Actions** (`.github/workflows/test.yml`)。
每當有新的程式碼推送至 `main` 分支或提交 Pull Request 時，系統會自動在雲端跑完所有測試，確保功能的穩定性。

---

## 認證機制說明

本項目採用 **JWT + HttpOnly Cookie + CSRF 防護** 的三層安全機制：

### Cookie 配置 (自動根據環境設置)

```python
# config/settings/base.py
if ENV == "local":
    COOKIE_SECURE = False      # 開發環境使用 HTTP
    COOKIE_SAMESITE = "Lax"
else:
    COOKIE_SECURE = True       # 生產環境強制 HTTPS
    COOKIE_SAMESITE = "Lax"    # 前後端同源，無需 None
```

---

## 專案結構 (Project Tree)

```text
.
├── apps/                           # Django 應用程式目錄
│   ├── accounts/                   # 使用者帳號與驗證模組
│   │   ├── models/
│   │   │   └── user.py             # 自訂使用者模型
│   │   ├── migrations/             # 資料庫遷移檔
│   │   ├── views.py                # 帳號相關 API (Google SSO, Auth Status)
│   │   ├── authentication.py       # 自訂 CookieJWTAuthentication
│   │   ├── adapters.py             # Django-allauth 適配器
│   │   ├── exceptions.py           # 自訂錯誤處理器
│   │   ├── admin.py                # 管理介面設定
│   │   ├── apps.py                 # 應用配置
│   │   └── tests/                  # 單元測試集 (包含網域限制測試)
│   └── chat/                       # 聊天功能模組
│       ├── models/
│       │   ├── session.py          # ChatSession 模型
│       │   └── message.py          # ChatMessage 模型
│       ├── services/
│       │   └── dify.py             # Dify API 整合服務 (Streaming)
│       ├── migrations/             # 資料庫遷移檔
│       ├── views.py                # 聊天代理 API (SSE Streaming)
│       ├── serializers.py          # DRF 序列化器
│       ├── admin.py                # 聊天紀錄管理介面
│       └── apps.py                 # 應用配置
├── tests/                          # 整合與 E2E 測試
│   └── e2e/                        # Playwright E2E 測試腳本
├── config/                         # 專案配置設定
│   ├── settings/
│   │   ├── base.py                 # 共用基礎設定
│   │   ├── development.py          # 開發環境配置
│   │   ├── production.py           # 生產環境配置
│   │   ├── test.py                 # 測試環境專屬設定 (SQLite/Mock)
│   │   └── __init__.py
│   ├── urls.py                     # 根路由設定
│   ├── wsgi.py                     # WSGI 入口 (生產環境)
│   ├── asgi.py                     # ASGI 入口
│   └── __pycache__/                # Python 快取
├── conftest.py                     # Pytest 全域 Fixtures 與 Mock 設定
├── pytest.ini                      # Pytest 設定檔
├── frontend/                       # 前端應用
│   └── Dify-ChatBot-V2/            # React + TypeScript + Vite
│       ├── src/
│       │   ├── App.tsx             # 主應用組件
│       │   ├── main.tsx            # 入口點
│       │   ├── components/         # 可複用元件
│       │   ├── pages/              # 頁面組件
│       │   ├── services/           # API 服務層
│       │   ├── hooks/              # 自訂 React Hooks
│       │   ├── contexts/           # React Context
│       │   └── lib/                # 工具函式庫
│       ├── public/                 # 靜態資源
│       ├── package.json            # 前端依賴
│       ├── vite.config.ts          # Vite 配置
│       ├── tailwind.config.ts      # Tailwind CSS 配置
│       ├── tsconfig.json           # TypeScript 配置
│       └── index.html              # HTML 入口
├── staticfiles/                    # 收集的靜態檔案 (生產環境)
├── manage.py                       # Django 管理腳本
├── main.py                         # Python 入口 (備用)
├── pyproject.toml                  # 專案元資料與依賴定義 (uv)
├── requirements.txt                # pip 依賴列表
├── db.sqlite3                      # SQLite 資料庫 (開發環境)
├── Dockerfile                      # Docker 鏡像配置
├── .env.example                    # 環境變數範例
├── .gitignore                      # Git 忽略清單
├── uv.lock                         # uv 依賴鎖定檔
└── README.md                       # 專案說明文件
```

---

## 主要特性 (Key Features)

### 後端特性

- ✅ **Google SSO 整合**: 使用 `django-allauth` 實現 Google 單一登入
- ✅ **JWT 自動刷新機制**: 支援無感 Access Token 刷新，短期閒置使用者免重新登入
- ✅ **智慧 CSRF 處理**: 業務 API 完整檢查，認證端點適度豁免避免死鎖
- ✅ **即時串流**: Server-Sent Events (SSE) 實現 AI 回覆的即時串流
- ✅ **聊天管理**: 完整的對話、訊息紀錄管理
- ✅ **API 安全**: 速率限制、輸入驗證、CSRF 防護
- ✅ **生產就緒**: 環境分離、詳細日誌、安全 Headers

### 前端特性

- ✅ **React 18 + TypeScript**: 類型安全的前端開發
- ✅ **Vite 構建工具**: 極快的開發伺服器與優化的生產構建
- ✅ **TailwindCSS**: 實用優先的 CSS 框架
- ✅ **響應式設計**: 適配各種設備尺寸
- ✅ **實時聊天**: 即時訊息串流顯示

---

## 系統設計 (System Architecture)

### 1. 安全的使用者認證 (High Security Auth)

#### Google SSO 整合

- **django-allauth 集成**: 提供 Google 帳號快速登入
- **組織限定登入**: 透過 `CustomSocialAccountAdapter` 實作登入攔截，僅允許 `ALLOWED_EMAIL_DOMAINS` 設定的特定 Email 網域 (如 `ntpu.edu.tw`) 進行登入

#### JWT 進階安全

- **Token 黑名單與輪轉**: 啟用 `SimpleJWT` 的 Token 黑名單 (Blacklist) 與旋轉 (Rotation) 機制
  - 當 Refresh Token 被使用時，會簽發新的並將舊的作廢
  - 有效降低 Token 遭竊取的風險
- **動態效期控制**:
  - Access Token 效期：1 小時
  - Refresh Token 效期：1 天
  - 平衡安全性與使用者體驗
- **HttpOnly Cookies**:
  - 與傳統 LocalStorage 不同，本系統將 JWT 存放在 **HttpOnly, Secure, SameSite** Cookies 中
  - 有效防禦 XSS 攻擊，確保權限憑證不被惡意腳本讀取

#### CSRF 防護機制

- **強制 CSRF 檢查**: 針對 Cookie-based 認證實作強制檢查
- **CSRF Cookie 安全強化**: 設定 `CSRF_COOKIE_HTTPONLY = True`，防止 CSRF Token 被 JavaScript 讀取
- **記憶體共享 Token**: 透過 `/api/auth/status/` 的回應夾帶 `csrfToken` 字串，供前端安全地傳遞檢查碼

#### 自定義認證後端

透過 `CookieJWTAuthentication` 自動從 Cookie 中提取並驗證 JWT，並結合 CSRF 驗證邏輯。

#### JWT 自動刷新機制 (Auto Refresh)

- **無感體驗**: Access Token 過期（1小時）時自動刷新，使用者無需重新登入
- **觸發機制**:
  - 前端 API 攔截 `access_token_expired` 錯誤碼
  - 自動發起 `/api/auth/refresh/` 請求（豁免 CSRF 檢查）
  - 重試原本失敗的請求，使用者僅感受輕微延遲
- **刷新流程**:
  ```
  1. 前端請求 → Access Token 過期 → 後端返回 access_token_expired
  2. 前端觸發刷新 → POST /api/auth/refresh/（使用 Refresh Token）
  3. 後端驗證 → 發放新 Access/Refresh Token（Set-Cookie）
  4. 前端重試原請求 → 成功完成操作
  ```
- **安全性保證**:
  - Refresh Token 儲存於 HttpOnly Cookie，無法被 XSS 竊取
  - Token Rotation：每次刷新產生新 Refresh Token，舊的加入黑名單
  - 長期未使用（1天）：Refresh Token 過期 → 要求重新登入

#### 智慧 CSRF 防護策略

- **分層檢查策略**:
  - **業務 API**（聊天、資料操作）：完整 CSRF 檢查，防止狀態變更攻擊
  - **認證端點豁免**：
    - `/api/auth/refresh/`：POST 請求豁免（避免 Token 失效死鎖）
    - `/api/auth/logout/`：POST 請求豁免（允許失效時登出）
    - `/api/auth/status/`：GET 請求不檢查（僅讀取狀態）
- **安全平衡**: 保持敏感操作的完整防護，適當放寬認證流程限制
- **防死鎖設計**: 避免 Access Token 與 CSRF Token 同時失效時的無限循環

#### 認證狀態精確判斷

- **三種狀態區分** (`AuthStatusView.get()`):
  1. ✅ **有效 Access Token** → 返回用戶資訊 + CSRF Token
  2. 🔄 **Access Token 過期 + 有 Refresh Token** → 返回 `access_token_expired`（觸發自動刷新）
  3. ❌ **完全無有效 Token** → 返回 `not_authenticated`（需重新登入）
- **防止誤判**: 精確識別 token 狀態，避免不必要的登出

### 2. 聊天代理與串流 (Chat Proxy & Streaming)

#### API 金鑰保護

- 前端不直接與 Dify 通訊
- 所有請求均由後端 `ChatStreamView` 代理
- 前端完全接觸不到 Dify API Key

#### 即時串流 (SSE)

- 使用 `StreamingHttpResponse` 將 Dify 的 `text/event-stream` 回應即時轉發至前端
- 實現零延遲的打字機效果

#### 流量控制 (Rate Limiting)

- 針對 Chat API 實作每分鐘 20 次的請求限制 (`UserRateThrottle`)
- 防止惡意腳本消耗系統資源或產生過多 LLM 費用

#### 輸入內容驗證

- 嚴格的輸入驗證，限制查詢長度（最大 500 字元）
- 過濾不安全字元，預防注入攻擊

#### 強健性與超時處理

- **Timeout 限制**: 連線 5s / 讀取 30s，防止 Dify 服務異常導致後端掛起
- **安全錯誤處理**: 發生異常時，後端詳細日誌 (Logging) 紀錄堆棧資訊，但僅回傳通用錯誤訊息給前端

#### 自動持久化

- 採取「先存問題、後串流、再存回答」的策略
- 即使 Dify API 回傳錯誤，使用者的原始問題 (USER role) 也會被優先保留於資料庫
- 確保紀錄完整性

### 3. 環境分離與生產安全強化 (Environment-Specific Security)

本系統採用 **開發/生產分離設定**，確保開發便利性與生產安全性的平衡：

#### 開發環境 (`development.py`)

- **DEBUG 模式**: 啟用詳細錯誤追蹤，方便除錯
- **DRF 可瀏覽 API**: 保留 `BrowsableAPIRenderer`，提供友善的 API 測試介面
- **詳細錯誤訊息**: 完整顯示堆疊追蹤與錯誤細節

#### 生產環境 (`production.py`)

- **禁用 DRF 可瀏覽 API**: 只保留 `JSONRenderer`，防止 API 結構與欄位資訊洩露
- **自訂錯誤處理器** (`custom_exception_handler`):
  - **內部詳細日誌**: 完整記錄錯誤堆棧、請求資訊到後端日誌
  - **外部通用訊息**: 只返回通用的中文錯誤訊息給前端（如「未授權，請先登入」）
  - **防止資訊洩露**: 避免暴露內部架構、資料庫結構或敏感配置
- **安全 Headers 強化**:
  - `SECURE_HSTS_SECONDS`: 啟用 HSTS (1 年)，強制 HTTPS
  - `SECURE_CONTENT_TYPE_NOSNIFF`: 防止 MIME 類型嗅探攻擊
  - `X_FRAME_OPTIONS`: 設為 DENY，防止 Clickjacking 攻擊
  - `SECURE_HSTS_PRELOAD`: 允許加入瀏覽器 HSTS preload list

#### 安全效果對比

```
開發環境訪問 /api/auth/status/
→ 顯示 DRF 可瀏覽介面，包含 API 文檔、欄位說明、詳細錯誤

生產環境訪問 /api/auth/status/
→ 只返回 JSON：{"error": "未授權，請先登入", "status_code": 401}
→ 詳細錯誤只記錄在後端日誌，外部無法存取
```

---

## API 文檔

### 認證相關

#### 1. 獲取認證狀態

```
GET /api/auth/status/
```

返回當前使用者的認證狀態及 CSRF Token

**成功回應 (200)**:

```json
{
  "is_authenticated": true,
  "user": {
    "id": 1,
    "email": "user@ntpu.edu.tw",
    "username": "username"
  },
  "csrf_token": "xxx..."
}
```

#### 2. Google OAuth 回調

```
GET /accounts/google/callback/?code=...&state=...
```

Google SSO 回調端點，由前端重定向使用

#### 3. 登出

```
POST /api/auth/logout/
```

清除認證 Token 並登出使用者

### 聊天相關

#### 1. 建立聊天對話

```
POST /api/chat/sessions/
```

建立一個新的聊天對話 Session

**請求範例**:

```json
{
  "title": "法律諮詢"
}
```

**成功回應 (201)**:

```json
{
  "id": 1,
  "title": "法律諮詢",
  "created_at": "2025-01-21T10:00:00Z",
  "user": 1
}
```

#### 2. 獲取所有對話

```
GET /api/chat/sessions/
```

取得當前使用者的所有聊天對話

#### 3. 聊天串流

```
POST /api/chat/stream/
```

發送訊息並獲取 AI 回覆的實時串流

**請求範例**:

```json
{
  "session_id": 1,
  "user_message": "什麼是侵權行為？"
}
```

**回應**: Server-Sent Events (SSE) 串流

```
data: {"type": "message_start"}
data: {"type": "message", "content": "侵權行為是..."}
data: {"type": "message_end"}
```

#### 4. 獲取對話訊息

```
GET /api/chat/sessions/{session_id}/messages/
```

取得特定對話的所有訊息

---

## 常見問題 (FAQ)

### Q: 如何配置 Google SSO？

**A**:

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立 OAuth 2.0 認證資訊
3. 在 `.env` 填入 `CLIENT_ID` 和 `SECRET`
4. 在 Django 管理界面設定 Site 和 Social Application

### Q: 如何增加 Rate Limit？

**A**: 在 `config/settings/base.py` 修改：

```python
DEFAULT_THROTTLE_RATES = {
    'chat': '20/min',  # 改為想要的限制
}
```

---

## JWT Token Refresh 流程與安全實務

### 1. Token 儲存方式

- **Access Token / Refresh Token** 皆儲存於 **HttpOnly Cookie**，前端 JS 無法直接存取，防止 XSS 竊取。
- **CSRF Token** 由後端 `/api/auth/status/` 回傳，前端以 closure 變數 (`internalCsrfToken`) 暫存，僅用於 header 傳遞。

### 2. 自動 Refresh Token 流程

#### 觸發條件：

- Access Token 過期（1小時）但 Refresh Token 仍有效（30天）
- 後端返回特定錯誤碼：`{"code": "access_token_expired"}`

#### 前端處理流程：

1. **偵測錯誤碼**：前端 API 層攔截 `access_token_expired`
2. **單次刷新控制**：避免多個請求同時觸發刷新（`isRefreshing` 標誌）
3. **請求隊列管理**：暫存等待中的請求到 `pendingRequests`
4. **觸發刷新**：發送 POST `/api/auth/refresh/`（豁免 CSRF 檢查）
5. **結果處理**：
   - ✅ 成功：更新 Cookie，重試所有暫存請求
   - ❌ 失敗（Refresh Token 也過期）：觸發登出流程

#### 後端刷新端點：

- **路徑**：`POST /api/auth/refresh/`
- **豁免 CSRF**：允許在 token 失效時呼叫
- **Token Rotation**：每次刷新產生新的 Refresh Token
- **黑名單機制**：舊的 Refresh Token 加入黑名單防止重用

### 3. 防止多重 refresh（Race Condition）

- 前端僅允許同時一個 refresh 請求進行，其他 401 請求會等待 refresh 結果，避免多重觸發。
- refresh 成功後，所有等待中的 API 會自動重試。
- refresh 失敗時，所有等待中的 API 皆失敗並觸發登出。

### 4. 後端設定（Django SimpleJWT）

- `ACCESS_TOKEN_LIFETIME = 60 分鐘`
- `REFRESH_TOKEN_LIFETIME = 1 天`
- `ROTATE_REFRESH_TOKENS = True`（每次 refresh 產生新 refresh token）
- `BLACKLIST_AFTER_ROTATION = True`（舊 refresh token 失效）
- `/api/auth/refresh/` endpoint 會自動處理 cookie 設定與黑名單

### 5. 實作重點

#### 前端實現 (`src/services/api.ts`)

- **請求攔截機制**：`request()` 函數統一處理所有 API 請求
- **自動刷新觸發**：偵測 `access_token_expired` 錯誤碼時自動觸發刷新
- **Race Condition 控制**：使用 `isRefreshing` 和 `refreshPromise` 避免多重刷新
- **請求隊列管理**：`pendingRequests` 暫存等待中的請求，刷新後重試
- **安全導向**：刷新失敗時呼叫 `performLogout()`，安全跳轉至登入頁

#### 後端實現

- **Refresh 端點**：`apps/accounts/views_token_refresh.py` 提供 `TokenRefreshView`
- **狀態檢查端點**：`apps/accounts/views.py` 中的 `AuthStatusView` 精確判斷認證狀態
- **Cookie 安全設定**：HttpOnly + Secure + SameSite，根據環境自動調整
- **智慧 CSRF 檢查**：`CookieJWTAuthentication` 實作分層防護策略
- **Token Rotation**：SimpleJWT 配置自動處理 Token 旋轉與黑名單

### 6. 實務安全建議

- 不建議將 JWT 儲存於 localStorage/sessionStorage
- 僅於 Access Token 過期時被動 refresh，避免定時輪詢
- 登出時清除所有 cookie 並安全導向登入頁
