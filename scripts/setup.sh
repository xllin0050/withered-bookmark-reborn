#!/bin/bash

# 枯枝逢生 - 快速環境設定腳本 (使用 uv)

echo "🌱 快速設定枯枝逢生開發環境..."

# 檢查是否在正確的目錄
if [ ! -f "README.md" ]; then
    echo "❌ 請在專案根目錄執行此腳本"
    exit 1
fi

# 檢查 uv 是否已安裝
if ! command -v uv &> /dev/null; then
    echo "❌ 未找到 uv，正在安裝..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
    echo "✅ uv 安裝完成"
fi

echo "🐍 設定 Python 後端環境..."
cd backend

# 建立虛擬環境
if [ ! -d ".venv" ]; then
    echo "📦 建立虛擬環境..."
    uv venv
fi

# 安裝依賴
echo "📚 安裝 Python 依賴..."
uv pip install -e .

cd ..

echo "🎨 設定前端環境..."
cd frontend

# 檢查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 未找到 Node.js，請先安裝 Node.js 16+"
    echo "💡 安裝方法:"
    echo "   macOS: brew install node"
    echo "   Ubuntu: sudo apt install nodejs npm"
    echo "   或訪問: https://nodejs.org/"
    exit 1
fi

# 安裝前端依賴
if [ ! -d "node_modules" ]; then
    echo "📦 安裝 Node.js 依賴..."
    npm install
fi

cd ..

echo "✅ 環境設定完成！"
echo ""
echo "🚀 現在可以執行 ./scripts/dev.sh 啟動開發環境"
echo "📖 或查看 docs/setup.md 了解更多詳情"
echo ""
