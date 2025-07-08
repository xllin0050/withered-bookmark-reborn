# justfile - Withered Bookmark Reborn 指令集

# 📦 安裝所有依賴
install:
    cd backend && uv venv && uv pip install -e ".[dev]"
    cd frontend && npm install
    # cd extension && npm install

# 🚀 啟動 FastAPI 伺服器
backend:
  cd backend && uv run -- uvicorn app.main:app --reload --port 8000

# 🌐 啟動前端開發伺服器
frontend:
  cd frontend && npm run dev

# 🧩 啟動 Chrome Extension 開發模式（可自行修改）
# extension:
#   cd extension && npm run dev

# 🧪 執行後端測試
test-backend:
  cd backend && uv run pytest

# 使用 xargs 實現並行執行
dev:
  echo "backend frontend" | xargs -n 1 -P 2 just

# 🧹 清除快取與輸出（視情況加入）
clean:
  rm -rf frontend/node_modules
  # rm -rf extension/node_modules
  find . -name '__pycache__' -exec rm -rf {} +
  find . -name '*.pyc' -delete