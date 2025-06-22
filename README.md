# Withered Bookmark Reborn 枯枝逢生

> 讓沉睡的書籤在搜尋時主動重生

## 專案簡介

**Withered Bookmark Reborn** 是一個智能書籤助手，解決了傳統書籤管理的核心問題：收藏後就遺忘。

### 核心功能
- 🔍 **搜尋增強**：在Google搜尋時自動推薦相關的已收藏內容
- 🧠 **智能分析**：自動提取網頁關鍵字和摘要
- ⚡ **一鍵收藏**：瀏覽器插件快速保存有價值的網頁
- 🎯 **語義搜尋**：理解搜尋意圖，不限於關鍵字匹配

### 技術架構
- **後端**: Python (uv) + FastAPI + SQLite + scikit-learn
- **前端**: Vue + TypeScript + TailwindCSS
- **擴展程序**: Chrome Extension Manifest V3
- **部署**: 尚在規劃中

## 快速開始

### 環境需求
- Python 3.8+
- [uv](https://github.com/astral-sh/uv) - 現代 Python 包管理器
- Node.js 16+
- Chrome 瀏覽器


### 本地開發

#### 一鍵啟動

```bash
just install   # 安裝所有相依
just dev       # 啟動後端與前端開發伺服器
```

#### 手動啟動方式（可選）

```bash
# 1. 後端
cd backend
uv venv
uv pip install -e ".[dev]"
uv run -- uvicorn app.main:app --reload --port 8000

# 2. 前端
cd frontend
npm install
npm run dev

# 3. 擴展程序（尚未啟用）
# cd extension
# npm install
# npm run dev
# 或手動載入 Chrome 擴展：
# 在 Chrome 中打開 chrome://extensions/
# 開啟開發者模式，載入 extension 資料夾
```

## 專案結構
```
withered-bookmark-reborn/
├── backend/           # Python FastAPI 後端
├── frontend/          # Vue + TypeScript 前端  
├── extension/         # Chrome 擴展程序
├── docs/             # 專案文檔
├── scripts/          # 開發腳本
└── shared/           # 共用程式碼
```

## 開發進度

- [ ] Phase 1: 基礎架構 (Week 1-2)
- [ ] Phase 2: 智能功能 (Week 3-4) 
- [ ] Phase 3: 瀏覽器整合 (Week 5-6)
- [ ] Phase 4: 優化測試 (Week 7-8)

## 貢獻指南

歡迎提交 Issue 和 Pull Request！

## 授權條款

MIT License
