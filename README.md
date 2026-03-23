# NTPU-GDG-Dify-ChatBot (NTPU LawHelper)

這是一個基於 Django 框架開發的聊天機器人後端 API 服務，主要用於整合 Dify 平台，提供使用者驗證、聊天對話管理及訊息紀錄儲存等功能。本系統目前服務於 NTPU LawHelper (北大法規問答小幫手)。

前後端已整合：React 前端與 Django 後端共享同一部署環境，無需分開部署。

上屆使用的聊天機器人前端專案 (Lovable): https://lovable.dev/projects/143b11e0-fb4c-47b9-b578-7c14f8113770

## 系統需求

- Python 3.12 或以上版本
- Node.js 16 或以上版本 (前端開發)
- PostgreSQL 或 SQLite (開發環境)
- Redis (快取與 Token 黑名單)

## 快速開始

### 1. 下載專案

```bash
git clone <repository>
cd NTPU-GDG-Dify-ChatBot
```

### 2. 啟動後端

```bash
# 安裝依賴 (建議使用 uv，或 pip)
uv pip install -r requirements.txt
# 或
pip install -r requirements.txt

# 設定環境變數
cp .env.example .env
# 請編輯 .env 填入必要配置 (例如 Dify API Key), 並確保 DJANGO_ENV=local

# 執行資料庫遷移
python manage.py migrate

# 建立超級使用者 (可選)
python manage.py createsuperuser

# 啟動開發伺服器
python manage.py runserver
```

後端服務器將運行在 http://localhost:8000。

### 3. 啟動前端 (新開終端機)

```bash
cd frontend/Dify-ChatBot-V2

# 安裝前端依賴
npm install

# 啟動前端開發伺服器
npm run dev
```

前端開發伺服器將運行在 http://localhost:8080，API 請求會自動代理至後端。

## 自動化測試

### 1. 準備測試環境

```bash
# 安裝測試相依套件
uv sync --dev

# 安裝瀏覽器相關系統依賴 (僅 Linux/WSL 需要)
sudo .venv/bin/playwright install-deps
```

### 2. 執行後端與 E2E 測試

```bash
# 執行所有測試
pytest

# 生成詳細的網頁版覆蓋率報告
pytest --cov=apps --cov-report=html

# 執行 E2E 測試並觀看瀏覽器操作畫面 (需圖形介面)
pytest tests/e2e/ --headed
```

### 3. 執行前端測試

```bash
cd frontend/Dify-ChatBot-V2
npm run test
```
