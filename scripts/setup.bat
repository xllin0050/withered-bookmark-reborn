@echo off
REM 枯枝逢生 - 快速環境設定腳本 (使用 uv)

echo 🌱 快速設定枯枝逢生開發環境...

REM 檢查是否在正確的目錄
if not exist "README.md" (
    echo ❌ 請在專案根目錄執行此腳本
    exit /b 1
)

REM 檢查 uv 是否已安裝
uv --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 uv，正在安裝...
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo ✅ uv 安裝完成，請重新開啟終端並再次執行此腳本
    pause
    exit /b 0
)

echo 🐍 設定 Python 後端環境...
cd backend

REM 建立虛擬環境
if not exist ".venv" (
    echo 📦 建立虛擬環境...
    uv venv
)

REM 安裝依賴
echo 📚 安裝 Python 依賴...
uv pip install -e .

cd ..

echo 🎨 設定前端環境...
cd frontend

REM 檢查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Node.js，請先安裝 Node.js 16+
    echo 💡 下載地址: https://nodejs.org/
    pause
    exit /b 1
)

REM 安裝前端依賴
if not exist "node_modules" (
    echo 📦 安裝 Node.js 依賴...
    npm install
)

cd ..

echo ✅ 環境設定完成！
echo.
echo 🚀 現在可以執行 scripts\dev.bat 啟動開發環境
echo 📖 或查看 docs\setup.md 了解更多詳情
echo.
pause
