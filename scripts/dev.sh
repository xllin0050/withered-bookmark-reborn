#!/bin/bash

# 枯枝逢生 - 開發環境啟動腳本 (使用 uv)

echo "🌱 啟動枯枝逢生開發環境..."

# 檢查是否在正確的目錄
if [ ! -f "README.md" ]; then
    echo "❌ 請在專案根目錄執行此腳本"
    exit 1
fi

# 檢查 uv 是否已安裝
if ! command -v uv &> /dev/null; then
    echo "❌ 未找到 uv，請先安裝 uv"
    echo "💡 安裝方法: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# 啟動後端
echo "🚀 啟動後端服務 (Port 8000)..."
cd backend

# 檢查是否已有虛擬環境
if [ ! -d ".venv" ]; then
    echo "📦 建立 Python 虛擬環境..."
    uv venv
fi

# 安裝依賴
echo "📚 安裝 Python 依賴..."
uv pip install -e .

# 啟動後端服務
uv run uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

cd ..

# 啟動前端
echo "🎨 啟動前端服務 (Port 3000)..."
cd frontend

# 檢查 node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 安裝 Node.js 依賴..."
    npm install
fi

# 啟動前端服務
npm run dev &
FRONTEND_PID=$!

cd ..

echo "✅ 開發環境啟動完成！"
echo "📱 前端: http://localhost:3000"
echo "🔧 後端 API: http://localhost:8000"
echo "📖 API 文檔: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服務"

# 等待中斷信號
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
