# 枯枝逢生 - 智能書籤助手後端

這是一個智能書籤管理系統的後端服務，基於 FastAPI 框架開發。

## 功能特色

- 智能書籤分類和管理
- 網頁內容抓取和分析
- RESTful API 設計
- 高效能的資料庫操作

## 技術棧

- **框架**: FastAPI
- **資料庫**: SQLAlchemy
- **Web伺服器**: Uvicorn
- **資料驗證**: Pydantic
- **中文處理**: jieba
- **機器學習**: scikit-learn

## 安裝和執行

```bash
# 初始化虛擬環境
uv venv

# 啟動虛擬環境
.venv\Scripts\activate

# 安裝依賴
uv pip install -e .

# 啟動開發伺服器
uvicorn app.main:app --reload
```

## 開發

本專案使用現代 Python 開發工具：

- **uv**: 快速的 Python 包管理器
- **Black**: 程式碼格式化
- **isort**: import 排序
- **pytest**: 單元測試

## 授權

MIT License
