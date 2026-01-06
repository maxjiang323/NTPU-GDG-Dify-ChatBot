# Dify ChatBot Backend

這是一個基於 Django 框架開發的聊天機器人後端 API 服務，主要用於整合 Dify 平台，提供使用者驗證、聊天對話管理及訊息紀錄儲存等功能。

## 專案結構 (Project Tree)

```text
.
├── apps/                   # Django 應用程式目錄
│   ├── accounts/           # 使用者帳號與驗證模組
│   │   ├── models/         # 使用者模型定義 (自訂 User)
│   │   ├── views.py        # 帳號相關 API 視圖
│   │   └── admin.py        # 管理介面設定
│   └── chat/               # 聊天功能模組
│       ├── models/         # 聊天相關模型 (Session, Message)
│       ├── views.py        # 聊天與 Google 登入回傳 API
│       ├── serializers.py  # DRF 資料序列化
│       ├── admin.py        # 聊天紀錄管理介面
│       └── services/       # 服務層
│           └── dify.py     # Dify API 整合服務 (Streaming)
├── config/                 # 專案配置設定
│   ├── settings/           # 分層設定檔 (Base, Development, Production)
│   ├── urls.py             # 根路由設定
│   ├── wsgi.py             # WSGI 入口
│   └── asgi.py             # ASGI 入口
├── manage.py               # Django 管理腳本
├── pyproject.toml          # 專案依賴與工具設定 (使用 uv 管理)
├── uv.lock                 # uv 依賴鎖定檔
└── README.md               # 專案說明文件
```

---

## 系統設計 (System Design)

### 1. 使用者認證系統 (Authentication)
*   **自訂使用者模型**: 擴展了 Django 內建的 `AbstractUser`，支援頭像、電話與個人簡介。
*   **Google SSO**: 整合 `django-allauth` 提供 Google 帳號快速登入。
*   **JWT 認證**: 使用 `rest_framework_simplejwt` 進行無狀態的身分驗證，登入後核發 Access Token 與 Refresh Token。

### 2. 聊天管理系統 (Chat Management)
*   **對話 Session**: 每一個對話獨立為一個 `ChatSession`，並與 `dify_conversation_id` 綁定，確保留存 Dify 端的對話上下文。
*   **訊息紀錄**: `ChatMessage` 模型紀錄了每一筆對話的內容、角色（User/AI/System）與時間戳記，實現後端對話歷史備份。

### 3. Dify 整合與代理 (Proxy)
*   **後端代理架構**: 前端不再直接與 Dify 通訊，而是透過 Django 後端的 `ChatStreamView` 進行轉發，確保護金鑰 (API Key) 安全性。
*   **串流轉發**: 後端使用 `StreamingHttpResponse` 將 Dify 的回應即時推送到前端，同時在傳輸完成後自動將完整的對話內容存入資料庫。
*   **上下文管理**: 透過 `dify_conversation_id` 維持 Dify 端的對話連貫性。

---

## 重要檔案用途說明

| 檔案路徑 | 用途描述 |
| :--- | :--- |
| `apps/accounts/models/user.py` | 定義自訂使用者欄位 (phone, avatar, bio) 與行為。 |
| `apps/chat/models/session.py` | 管理聊天室對話，紀錄所屬使用者及對應的 Dify 會話 ID。 |
| `apps/chat/models/message.py` | 儲存每一條對話訊息的詳細內容與角色。 |
| `apps/chat/views.py` | 包含 `ChatStreamView` (代理串流) 與 `ChatSessionViewSet` 等 API。 |
| `apps/chat/services/dify.py` | 實作對 Dify API 的封裝，支援串流發送與回應解析。 |
| `config/settings/base.py` | 專案基礎設定，包含 App 註冊、CORS 允許來源等。 |
| `pyproject.toml` | 專案依賴清單，透過 `uv` 管理開發與生產環境所需套件。 |

---

## 開發指南

### 環境準備
本專案建議使用 [uv](https://github.com/astral-sh/uv) 進行依賴管理。

### 啟動服務
1.  安裝依賴: `uv sync`
2.  執行資料庫遷移: `python manage.py migrate`
3.  啟動開發伺服器: `python manage.py runserver`

