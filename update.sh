#!/bin/bash
# update.sh - 安全的更新部署腳本

set -e  # 遇到錯誤立即停止

PROJECT_DIR="/home/$(whoami)/withered-bookmark-reborn"
SERVICE_NAME="withered-bookmark"
BACKUP_DIR="$PROJECT_DIR/backup"

echo "🔄 開始更新 Withered Bookmark Reborn..."

# 1. 檢查當前目錄
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ 專案目錄不存在: $PROJECT_DIR"
    exit 1
fi

cd $PROJECT_DIR

# 2. 創建備份目錄
mkdir -p $BACKUP_DIR

# 3. 備份資料庫
if [ -f "backend/bookmarks.db" ]; then
    BACKUP_FILE="$BACKUP_DIR/bookmarks-$(date +%Y%m%d_%H%M%S).db"
    cp backend/bookmarks.db "$BACKUP_FILE"
    echo "✅ 資料庫已備份至: $BACKUP_FILE"
else
    echo "⚠️  未找到資料庫檔案，跳過備份"
fi

# 4. 檢查當前服務狀態
echo "📊 檢查當前服務狀態..."
if systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ 服務運行正常"
    RESTART_NEEDED=true
else
    echo "⚠️  服務未運行"
    RESTART_NEEDED=false
fi

# 5. 檢查 Git 狀態
echo "📦 檢查 Git 狀態..."
git status --porcelain

if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  有未提交的本地變更，將暫存這些變更"
    git stash push -m "更新前的本地變更 $(date)"
fi

# 6. 獲取更新資訊
echo "🔍 檢查可用更新..."
git fetch origin

CURRENT_COMMIT=$(git rev-parse HEAD)
REMOTE_COMMIT=$(git rev-parse origin/main)

if [ "$CURRENT_COMMIT" = "$REMOTE_COMMIT" ]; then
    echo "✅ 已是最新版本，無需更新"
    exit 0
fi

echo "📋 即將更新的變更："
git log --oneline $CURRENT_COMMIT..$REMOTE_COMMIT

# 7. 詢問確認
read -p "是否繼續更新？[y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 更新已取消"
    exit 1
fi

# 8. 執行更新
echo "📥 拉取最新程式碼..."
git pull origin main

# 9. 執行部署
echo "🚀 執行部署..."
./deploy.sh

# 10. 測試部署
echo "🧪 測試部署..."
sleep 5

# 簡單的健康檢查
if curl -s -f http://localhost:8000/health > /dev/null; then
    echo "✅ 健康檢查通過"
else
    echo "❌ 健康檢查失敗"
    
    # 提供回滾選項
    read -p "是否回滾到上一版本？[y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔄 回滾到上一版本..."
        git reset --hard $CURRENT_COMMIT
        ./deploy.sh
        echo "✅ 已回滾"
    fi
    exit 1
fi

# 11. 清理舊備份（保留最近10個）
echo "🧹 清理舊備份..."
cd $BACKUP_DIR
ls -t bookmarks-*.db 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null || true
cd $PROJECT_DIR

echo ""
echo "🎉 更新完成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 更新摘要："
echo "   🔸 從: $(git rev-parse --short $CURRENT_COMMIT)"
echo "   🔸 到: $(git rev-parse --short HEAD)"
echo "   🔸 資料庫備份: $BACKUP_FILE"
echo ""
echo "🔍 查看變更："
echo "   git log --oneline $CURRENT_COMMIT..HEAD"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
