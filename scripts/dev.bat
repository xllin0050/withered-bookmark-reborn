@echo off
REM 枯枝逢生 - Windows 開發環境啟動腳本 (使用 uv)

echo 🌱 啟動枯枝逢生開發環境...

REM 檢查是否在正確的目錄
if not exist "README.md" (
    echo ❌ 請在專案根目錄執行此腳本
    exit /b 1
)

REM 檢查 uv 是否已安裝
uv --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 uv，請先安裝 uv
    echo 💡 安裝方法: https://github.com/astral-sh/uv
    pause
    exit /b 1
)

REM 啟動後端
echo 🚀 啟動後端服務 (Port 8000)...
cd backend

REM 檢查是否已有虛擬環境
if not exist ".venv" (
    echo 📦 建立 Python 虛擬環境...
    uv venv
)

REM 安裝依賴
echo 📚 安裝 Python 依賴...
uv pip install -e .

REM 在新視窗啟動後端服務
start "Backend Server" cmd /k "uv run uvicorn app.main:app --reload --port 8000"

cd ..

REM 啟動前端
echo 🎨 啟動前端服務 (Port 3000)...
cd frontend

REM 檢查 node_modules
if not exist "node_modules" (
    echo 📦 安裝 Node.js 依賴...
    npm install
)

REM 在新視窗啟動前端服務
start "Frontend Server" cmd /k "npm run dev"

cd ..

echo ✅ 開發環境啟動完成！
echo 📱 前端: http://localhost:3000
echo 🔧 後端 API: http://localhost:8000
echo 📖 API 文檔: http://localhost:8000/docs
echo.
echo 關閉視窗可停止對應服務
pause
