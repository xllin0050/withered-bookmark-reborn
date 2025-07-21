# 🐍 枯枝逢生 - 智能書籤助手後端

**企業級智能書籤管理系統後端服務**，採用現代 Python 技術棧和先進的 TF-IDF 語義搜尋引擎。

## ✨ **功能特色**

- 🎯 **TF-IDF 語義搜尋引擎**: 餘弦相似度計算，支援中英文混合搜尋
- 🧠 **智能內容分析**: 網頁抓取、jieba 中文分詞、關鍵字提取、自動摘要
- ⚡ **高性能優化**: 相似度快取、批量向量計算、健康監控
- 📊 **企業級監控**: 性能指標追蹤、健康檢查端點、詳細日誌
- 🛡️ **穩健架構**: 錯誤處理、graceful degradation、背景任務處理

## 🏗️ **技術棧**

- **框架**: FastAPI (現代異步 Web 框架)
- **資料庫**: SQLAlchemy + SQLite (支援 TF-IDF 向量存儲)
- **Web伺服器**: Uvicorn (ASGI 服務器)
- **資料驗證**: Pydantic v2 (型別安全的資料驗證)
- **中文處理**: jieba (中文分詞和關鍵字提取)
- **機器學習**: scikit-learn (TF-IDF 向量化和相似度計算)
- **網頁抓取**: aiohttp + BeautifulSoup (異步內容抓取)
- **包管理**: uv (現代 Python 包管理器)

## 🚀 **安裝與執行**

### ⚡ **使用 justfile (強烈建議)**

```bash
# 從專案根目錄執行
just install       # 自動安裝後端和前端依賴
just backend       # 僅啟動後端服務 (port 8000)
just dev          # 同時啟動後端和前端 (推薦)
```

### 🔧 **手動方式** (進階用戶)

```bash
# 進入後端目錄
cd backend

# 建立虛擬環境並安裝依賴  
uv venv
uv pip install -e ".[dev]"

# 啟動開發伺服器
uv run uvicorn app.main:app --reload --port 8000
```

## 📡 **API 服務端點**

啟動後可訪問：
- **API 根路徑**: http://localhost:8000
- **API 文檔 (Swagger)**: http://localhost:8000/docs
- **ReDoc 文檔**: http://localhost:8000/redoc  
- **健康檢查**: http://localhost:8000/api/v1/search/health

## 🏗️ **專案架構**

```
backend/
├── app/
│   ├── main.py              # FastAPI 應用入口
│   ├── api/                 # RESTful API 路由
│   │   ├── bookmarks.py    # 書籤 CRUD + 批量操作
│   │   └── search.py       # 智能搜尋 + 系統監控
│   ├── models/             # 資料模型
│   │   ├── database.py     # SQLAlchemy 資料庫模型
│   │   └── schemas.py      # Pydantic 資料驗證模型
│   └── services/           # 核心業務邏輯
│       ├── content_enricher.py    # 內容增強服務
│       ├── tfidf_vectorizer.py    # TF-IDF 向量化引擎
│       └── bookmark_importer.py   # HTML 書籤匯入
└── tests/                  # 單元測試
```

## 🔬 **核心服務模組**

### 📊 **TF-IDF 向量化引擎** (`tfidf_vectorizer.py`)
- **向量化**: 文本轉換為稀疏 TF-IDF 向量 (JSON 格式)
- **相似度計算**: 餘弦相似度，支援智能快取
- **批量處理**: sklearn 向量化操作，高效處理大量資料
- **快取管理**: TTL、自動清理、使用統計

### 🧠 **內容增強服務** (`content_enricher.py`)
- **網頁抓取**: aiohttp + BeautifulSoup 異步內容提取
- **中文分詞**: jieba 精準中文文本處理
- **關鍵字提取**: TF-IDF 算法自動識別重要詞彙  
- **摘要生成**: 句子重要性評分的自動摘要

## ⚙️ **開發工具**

本專案採用現代 Python 開發最佳實踐：

- **uv**: 極速 Python 包管理器 (比 pip 快 10-100 倍)
- **FastAPI**: 高性能異步 Web 框架，自動生成 OpenAPI 文檔
- **Pydantic v2**: 型別安全的資料驗證，優秀的開發體驗
- **SQLAlchemy**: 現代 Python ORM，支援異步操作
- **pytest**: 專業級單元測試框架

### 🧪 **測試執行**

```bash
# 執行後端測試
just test-backend

# 或手動執行
cd backend && uv run pytest
```

## 📄 **授權**

MIT License
