# 開發指南

## 開發服務

- **前端**: http://localhost:3000
- **後端 API**: http://localhost:8000
- **API 文檔**: http://localhost:8000/docs
- **Chrome 擴展程序**: 載入後在瀏覽器工具列顯示

## 專案結構詳解

```
withered-bookmark-reborn/
├── backend/                    # Python FastAPI 後端
│   ├── app/
│   │   ├── main.py            # FastAPI 應用程式進入點
│   │   ├── models/            # 資料庫模型和 Pydantic schemas
│   │   ├── api/               # API 路由
│   │   ├── services/          # 商業邏輯服務
│   │   └── utils/             # 工具函數
│   ├── requirements.txt       # Python 依賴
│   └── tests/                 # 測試文件
├── frontend/                   # Vue 3 + TypeScript 前端
│   ├── src/
│   │   ├── components/        # Vue 組件
│   │   ├── pages/             # 頁面組件
│   │   ├── stores/            # Pinia 狀態管理
│   │   ├── services/          # API 調用服務
│   │   ├── types/             # TypeScript 類型定義
│   │   └── router/            # Vue Router 路由配置
│   ├── package.json           # Node.js 依賴
│   └── vite.config.ts         # Vite 配置
├── extension/                  # Chrome 擴展程序
│   ├── manifest.json          # 擴展程序配置
│   ├── popup/                 # 彈窗界面
│   ├── content/               # 內容腳本
│   ├── background/            # 背景服務
│   └── assets/                # 圖標和資源
└── scripts/                   # 開發腳本
    ├── dev.sh                 # Linux/Mac 開發啟動腳本
    └── dev.bat                # Windows 開發啟動腳本
```

## 開發工作流

1. **Phase 1**: 基礎架構開發
   - 後端 API 和資料庫
   - 前端基礎界面
   - 基本的書籤 CRUD 功能

2. **Phase 2**: 智能功能開發
   - 網頁內容分析
   - 關鍵字提取和語義搜尋
   - 推薦演算法

3. **Phase 3**: 瀏覽器整合
   - Chrome 擴展程序開發
   - 搜尋頁面注入功能
   - 一鍵收藏功能

4. **Phase 4**: 優化和測試
   - 性能優化
   - 用戶體驗改善
   - 測試和 bug 修復

## 技術選型說明

- **後端**: FastAPI - 快速、現代的 Python Web 框架，使用 uv 管理依賴
- **前端**: Vue 3 + TypeScript - 漸進式框架，類型安全
- **狀態管理**: Pinia - Vue 3 官方推薦的狀態管理
- **API 查詢**: TanStack Query - 強大的數據獲取和快取
- **樣式**: Tailwind CSS - 實用優先的 CSS 框架
- **資料庫**: SQLite - 輕量級關聯式資料庫
- **擴展程序**: Manifest V3 - 最新的 Chrome 擴展程序標準
