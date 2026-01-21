# Dify ChatBot Backend (NTPU LawHelper)

這是一個基於 Django 框架開發的聊天機器人後端 API 服務，主要用於整合 Dify 平台，提供使用者驗證、聊天對話管理及訊息紀錄儲存等功能。本系統目前服務於 **NTPU LawHelper (北大法規問答小幫手)**，部分行動裝置可能無法使用單一登入。

**目前已將前後端整合 (前端：React, 後端：Django)，但保留原本 Repository 的名稱**

**上屆使用的聊天機器人前端專案 (Lovable)**
**URL**: https://lovable.dev/projects/143b11e0-fb4c-47b9-b578-7c14f8113770

---

## 快速開始

### 環境需求
- Python 3.12+
- Node.js 16+ (前端開發)
- PostgreSQL 或 SQLite (開發環境)
- Redis (快取與 Token 黑名單)

### 後端安裝與運行

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

# 資料庫遷移
python manage.py migrate

# 建立超級使用者 (可選)
python manage.py createsuperuser

# 開發模式運行
python manage.py runserver
# 服務器在 http://localhost:8000
```

### 前端安裝與運行

```bash
cd frontend/Dify-ChatBot-V2

# 安裝前端依賴
npm install

# 開發模式
npm run dev
# 前端在 http://localhost:8080

# 生產構建
npm run build
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
│   │   └── tests.py                # 單元測試
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
│       ├── apps.py                 # 應用配置
│       └── tests.py                # 單元測試
├── config/                         # 專案配置設定
│   ├── settings/
│   │   ├── base.py                 # 共用基礎設定
│   │   ├── development.py          # 開發環境配置
│   │   ├── production.py           # 生產環境配置
│   │   └── __init__.py
│   ├── urls.py                     # 根路由設定
│   ├── wsgi.py                     # WSGI 入口 (生產環境)
│   ├── asgi.py                     # ASGI 入口
│   └── __pycache__/                # Python 快取
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
- ✅ **JWT 認證**: 支援 Token 黑名單、Token 旋轉、自訂 Cookie-based 認證
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
*   **django-allauth 集成**: 提供 Google 帳號快速登入
*   **組織限定登入**: 透過 `CustomSocialAccountAdapter` 實作登入攔截，僅允許 `ALLOWED_EMAIL_DOMAINS` 設定的特定 Email 網域 (如 `ntpu.edu.tw`) 進行登入

#### JWT 進階安全
*   **Token 黑名單與輪轉**: 啟用 `SimpleJWT` 的 Token 黑名單 (Blacklist) 與旋轉 (Rotation) 機制
    - 當 Refresh Token 被使用時，會簽發新的並將舊的作廢
    - 有效降低 Token 遭竊取的風險
*   **動態效期控制**: 
    - Access Token 效期：1 小時
    - Refresh Token 效期：1 天
    - 平衡安全性與使用者體驗
*   **HttpOnly Cookies**:
    - 與傳統 LocalStorage 不同，本系統將 JWT 存放在 **HttpOnly, Secure, SameSite** Cookies 中
    - 有效防禦 XSS 攻擊，確保權限憑證不被惡意腳本讀取

#### CSRF 防護機制
*   **強制 CSRF 檢查**: 針對 Cookie-based 認證實作強制檢查
*   **CSRF Cookie 安全強化**: 設定 `CSRF_COOKIE_HTTPONLY = True`，防止 CSRF Token 被 JavaScript 讀取
*   **記憶體共享 Token**: 透過 `/api/auth/status/` 的回應夾帶 `csrfToken` 字串，供前端安全地傳遞檢查碼

#### 自定義認證後端
透過 `CookieJWTAuthentication` 自動從 Cookie 中提取並驗證 JWT，並結合 CSRF 驗證邏輯。

### 2. 聊天代理與串流 (Chat Proxy & Streaming)

#### API 金鑰保護
*   前端不直接與 Dify 通訊
*   所有請求均由後端 `ChatStreamView` 代理
*   前端完全接觸不到 Dify API Key

#### 即時串流 (SSE)
*   使用 `StreamingHttpResponse` 將 Dify 的 `text/event-stream` 回應即時轉發至前端
*   實現零延遲的打字機效果

#### 流量控制 (Rate Limiting)
*   針對 Chat API 實作每分鐘 20 次的請求限制 (`UserRateThrottle`)
*   防止惡意腳本消耗系統資源或產生過多 LLM 費用

#### 輸入內容驗證
*   嚴格的輸入驗證，限制查詢長度（最大 500 字元）
*   過濾不安全字元，預防注入攻擊

#### 強健性與超時處理
*   **Timeout 限制**: 連線 5s / 讀取 30s，防止 Dify 服務異常導致後端掛起
*   **安全錯誤處理**: 發生異常時，後端詳細日誌 (Logging) 紀錄堆棧資訊，但僅回傳通用錯誤訊息給前端

#### 自動持久化
*   採取「先存問題、後串流、再存回答」的策略
*   即使 Dify API 回傳錯誤，使用者的原始問題 (USER role) 也會被優先保留於資料庫
*   確保紀錄完整性

### 3. 環境分離與生產安全強化 (Environment-Specific Security)

本系統採用 **開發/生產分離設定**，確保開發便利性與生產安全性的平衡：

#### 開發環境 (`development.py`)
*   **DEBUG 模式**: 啟用詳細錯誤追蹤，方便除錯
*   **DRF 可瀏覽 API**: 保留 `BrowsableAPIRenderer`，提供友善的 API 測試介面
*   **詳細錯誤訊息**: 完整顯示堆疊追蹤與錯誤細節

#### 生產環境 (`production.py`)
*   **禁用 DRF 可瀏覽 API**: 只保留 `JSONRenderer`，防止 API 結構與欄位資訊洩露
*   **自訂錯誤處理器** (`custom_exception_handler`):
    - **內部詳細日誌**: 完整記錄錯誤堆棧、請求資訊到後端日誌
    - **外部通用訊息**: 只返回通用的中文錯誤訊息給前端（如「未授權，請先登入」）
    - **防止資訊洩露**: 避免暴露內部架構、資料庫結構或敏感配置
*   **安全 Headers 強化**:
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
