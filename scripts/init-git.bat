@echo off
REM 枯枝逢生 - Git 倉庫初始化腳本 (使用 uv)

echo 🌱 初始化 Git 倉庫...

REM 確保在正確的目錄
cd /d "%~dp0\.."

REM 初始化 Git 倉庫
git init

REM 設定預設分支為 main
git branch -M main

REM 添加所有文件
git add .

REM 建立初始提交
git commit -m "🎉 Initial commit: 枯枝逢生 (Withered Bookmark Reborn)

✨ Features:
- 📁 Project structure setup with uv for Python management
- 🐍 Python FastAPI backend foundation with pyproject.toml
- 🖼️ Vue 3 + TypeScript frontend foundation  
- 🔧 Chrome extension manifest
- 📝 Documentation and setup guides
- 🛠️ Development scripts optimized for uv

📦 Tech Stack:
- Backend: Python (uv) + FastAPI + SQLAlchemy + SQLite
- Frontend: Vue 3 + TypeScript + Pinia + TailwindCSS
- Extension: Chrome Manifest V3
- Build: Vite + npm

🚀 Ready for Phase 1 development!"

echo ✅ Git 倉庫初始化完成！
echo 📝 建議接下來執行：
echo    git remote add origin ^<你的倉庫 URL^>
echo    git push -u origin main
pause
