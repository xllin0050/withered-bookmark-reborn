# Withered Bookmark Reborn 枯枝逢生

> 讓沉睡的書籤透過智能語義搜尋重獲新生

## 🎉 **專案簡介**

**Withered Bookmark Reborn** 是一個**企業級智能書籤管理系統**，採用先進的 TF-IDF 語義搜尋技術，解決傳統書籤管理的核心痛點：**收藏後即遺忘**。

### ✨ **已實現的核心功能** 
- 🎯 **智能語義搜尋**：TF-IDF 向量化 + 餘弦相似度，支援中英文混合搜尋
- 🧠 **自動內容分析**：網頁內容抓取、jieba 中文分詞、關鍵字提取、摘要生成
- ⚡ **高性能系統**：相似度快取、批量向量計算、虛擬滾動優化
- 📊 **企業級監控**：性能指標追蹤、健康檢查端點、詳細日誌記錄
- 🎨 **現代化界面**：Vue 3 + TypeScript + TailwindCSS v4，響應式設計

### 🏗️ **技術架構**
- **後端**: FastAPI + SQLAlchemy + scikit-learn + jieba + aiohttp + BeautifulSoup
- **前端**: Vue 3 + TypeScript + Vite + Pinia + TailwindCSS v4
- **包管理**: uv (Python) + justfile (統一開發環境)
- **資料庫**: SQLite (支援 TF-IDF 向量存儲)
- **瀏覽器擴展**: Chrome Extension Manifest V3 (基礎結構完成)

## 🚀 **快速開始** 

### 🛠️ **環境需求**
- **Python 3.8+** (建議 3.11+)
- **[uv](https://github.com/astral-sh/uv)** - 現代高速 Python 包管理器
- **Node.js 16+** (建議 18+)  
- **[just](https://github.com/casey/just)** - 命令執行工具 (可選，但強烈建議)

### ⚡ **一鍵啟動** (推薦)

```bash
# 安裝所有依賴 (後端 + 前端)
just install

# 同時啟動後端 (port 8000) 和前端 (port 3008) 開發伺服器
just dev
```

**🎉 啟動後即可使用完整的智能書籤管理系統！**

- **前端界面**: http://localhost:3008
- **後端 API**: http://localhost:8000  
- **API 文檔**: http://localhost:8000/docs
- **健康檢查**: http://localhost:8000/api/v1/search/health

### 🔧 **其他便捷命令**

```bash
# 單獨操作
just backend     # 僅啟動後端服務
just frontend    # 僅啟動前端服務
just test-backend # 執行後端測試
just clean       # 清理緩存檔案

# 手動安裝 (不使用 just)
cd backend && uv pip install -e ".[dev]"
cd frontend && npm install
```

### 📋 **手動啟動方式** (可選)

```bash
# 1. 後端 FastAPI 服務 (port 8000)
cd backend
uv venv && uv pip install -e ".[dev]"
uv run uvicorn app.main:app --reload --port 8000

# 2. 前端 Vue 應用 (port 3008) 
cd frontend  
npm install && npm run dev
```

## 📁 **專案結構**

```
withered-bookmark-reborn/
├── backend/           # 🐍 FastAPI 後端服務
│   ├── app/
│   │   ├── api/      # RESTful API 路由
│   │   ├── models/   # 資料庫模型 & Pydantic schemas  
│   │   └── services/ # 核心服務 (內容增強、TF-IDF 向量化)
│   └── tests/        # 後端測試
├── frontend/          # 🎨 Vue 3 前端應用
│   ├── src/
│   │   ├── components/ # 可重用組件
│   │   ├── pages/     # 頁面組件
│   │   ├── stores/    # Pinia 狀態管理
│   │   └── services/  # API 服務層
│   └── public/       # 靜態資源
├── extension/         # 🔌 Chrome 擴展程序 (基礎結構)
├── docs/             # 📚 專案文檔與進度追蹤  
├── shared/           # 🔄 共用 TypeScript 類型定義
└── justfile          # 🛠️ 統一開發命令
```

## 🎯 **核心功能演示**

### 📊 **智能語義搜尋**
- **TF-IDF 向量化**: 自動將書籤內容轉換為數值向量
- **餘弦相似度**: 計算搜尋查詢與書籤的語義相似度  
- **混合評分**: 語義相似度 (70%) + 關鍵字匹配 (30%)
- **智能快取**: 避免重複計算，大幅提升搜尋速度

### 🧠 **自動內容分析**  
- **網頁抓取**: 自動提取標題、描述、主要內容
- **中文分詞**: 使用 jieba 進行精準的中文文本處理
- **關鍵字提取**: TF-IDF 算法自動識別重要詞彙
- **摘要生成**: 基於句子重要性評分的自動摘要

### ⚡ **高性能優化**
- **批量向量計算**: sklearn 向量化操作，高效處理大量書籤
- **相似度快取**: TTL 機制，自動清理過期快取
- **虛擬滾動**: 前端優化，流暢展示大量書籤
- **健康監控**: 實時系統狀態監控和性能指標

## 📈 **開發進度** ✅ **核心功能已完成**

- ✅ **Phase 1: 基礎架構** (100% 完成)
- ✅ **Phase 2: 智能功能** (100% 完成) 
- ⏸️ **Phase 3: 瀏覽器整合** (基礎完成，進階功能暫緩)
- 🔄 **Phase 4: 系統優化** (90% 完成)

**🎉 當前狀況**: 核心智能書籤管理系統已達企業級品質，可立即投入使用！

## 🔗 **API 端點**

### 📚 書籤管理
- `GET /api/v1/bookmarks` - 獲取書籤列表
- `POST /api/v1/bookmarks` - 新增書籤 (自動內容豐富化)
- `PUT /api/v1/bookmarks/{id}` - 更新書籤
- `DELETE /api/v1/bookmarks/{id}` - 刪除書籤

### 🔍 智能搜尋  
- `POST /api/v1/search/` - 語義搜尋 (混合評分)
- `GET /api/v1/search/health` - 系統健康檢查
- `GET /api/v1/search/vectorizer/stats` - 向量化器統計

### 🛠️ 系統管理
- `POST /api/v1/bookmarks/batch-vectorize` - 批量向量化
- `POST /api/v1/bookmarks/retrain-vectorizer` - 重新訓練向量化器

## 🤝 **貢獻指南**

歡迎提交 Issue 和 Pull Request！專案採用現代化開發流程。

## 📄 **授權條款**

MIT License - 詳見 [LICENSE](LICENSE) 檔案
