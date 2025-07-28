#!/bin/bash
# deploy.sh - Withered Bookmark 部署腳本

set -e  # 遇到錯誤立即停止

PROJECT_DIR="/home/$(whoami)/withered-bookmark-reborn"
SERVICE_NAME="withered-bookmark"
DOMAIN="your-domain.com"  # 修改為你的域名或 IP

echo "🚀 開始部署 Withered Bookmark Reborn..."

# 1. 檢查並創建專案目錄
if [ ! -d "$PROJECT_DIR" ]; then
    echo "📁 克隆專案..."
    cd /home/$(whoami)
    git clone https://github.com/your-username/withered-bookmark-reborn.git
    cd $PROJECT_DIR
else
    echo "📦 更新程式碼..."
    cd $PROJECT_DIR
    git pull origin main
fi

# 2. 安裝依賴
echo "🔧 安裝依賴..."
just install

# 3. 設置前端環境變數
echo "🌐 設置前端環境變數..."
cat > frontend/.env.production << EOF
VITE_API_BASE_URL=/api/v1
VITE_APP_TITLE=Withered Bookmark Reborn
VITE_APP_DEBUG=false
EOF

# 4. 建置前端
echo "🏗️ 建置前端..."
cd frontend
# 確保使用生產環境配置
NODE_ENV=production npm run build
cd ..

# 5. 設置環境變數（可選）
if [ ! -f "backend/.env" ]; then
    echo "⚙️ 創建環境配置..."
    cat > backend/.env << EOF
# 生產環境配置
DATABASE_URL=sqlite:///./bookmarks.db
CORS_ORIGINS=["https://${DOMAIN}", "chrome-extension://*"]
LOG_LEVEL=INFO
EOF
fi

# 6. 初始化資料庫
echo "🗄️ 初始化資料庫..."
cd backend
uv run python -c "from app.models.database import create_tables; create_tables()"
cd ..

# 7. 設置 systemd 服務
if [ ! -f "/etc/systemd/system/${SERVICE_NAME}.service" ]; then
    echo "⚙️ 設置 systemd 服務..."
    sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=Withered Bookmark FastAPI Server
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=${PROJECT_DIR}/backend
Environment=PATH=/home/$(whoami)/.local/bin:/usr/bin:/bin
ExecStart=/home/$(whoami)/.local/bin/uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

# 資源限制
MemoryMax=1G
MemoryHigh=800M

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable $SERVICE_NAME
fi

# 8. 更新 Caddyfile
echo "🌐 設置 Caddy 配置..."
CADDY_CONFIG="/etc/caddy/Caddyfile"

# 備份現有配置
if [ -f "$CADDY_CONFIG" ]; then
    sudo cp "$CADDY_CONFIG" "${CADDY_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
fi

# 檢查是否已有此專案的配置
if ! sudo grep -q "withered-bookmark" "$CADDY_CONFIG" 2>/dev/null; then
    echo "添加 Withered Bookmark 配置到 Caddyfile..."
    
    sudo tee -a "$CADDY_CONFIG" > /dev/null <<EOF

# Withered Bookmark Reborn
${DOMAIN} {
    # API 路由代理到後端
    handle_path /api/* {
        reverse_proxy localhost:8000
    }
    
    # 健康檢查和根路徑
    handle /health {
        reverse_proxy localhost:8000
    }
    
    # 前端靜態檔案
    handle {
        root * ${PROJECT_DIR}/frontend/dist
        try_files {path} /index.html
        file_server
        
        @static {
            path *.js *.css *.png *.jpg *.jpeg *.gif *.ico *.svg *.woff *.woff2
        }
        header @static Cache-Control "public, max-age=31536000, immutable"
    }
    
    # 自動 HTTPS + 壓縮
    encode gzip
}
EOF
fi

# 9. 重啟服務
echo "🔄 重啟服務..."
sudo systemctl restart $SERVICE_NAME
sudo systemctl reload caddy

# 10. 等待服務啟動
echo "⏳ 等待服務啟動..."
sleep 5

# 11. 檢查服務狀態
echo "✅ 檢查服務狀態..."

if systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ 後端服務運行正常"
    
    # 測試 API 健康檢查
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ API 健康檢查通過"
    else
        echo "⚠️  API 健康檢查失敗"
    fi
else
    echo "❌ 後端服務啟動失敗"
    sudo systemctl status $SERVICE_NAME --no-pager
    exit 1
fi

if systemctl is-active --quiet caddy; then
    echo "✅ Caddy 運行正常"
else
    echo "❌ Caddy 啟動失敗"
    sudo systemctl status caddy --no-pager
    exit 1
fi

# 12. 設置測試腳本權限
chmod +x test-deployment.sh

# 13. 顯示部署信息
echo ""
echo "🎉 部署完成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 服務資訊："
echo "   🌐 前端: https://${DOMAIN}"
echo "   🔗 API:  https://${DOMAIN}/api/v1"
echo "   💓 健康: https://${DOMAIN}/health"
echo ""
echo "🗂️ 檔案位置："
echo "   📁 專案: ${PROJECT_DIR}"
echo "   🗄️ 資料庫: ${PROJECT_DIR}/backend/bookmarks.db"
echo "   ⚙️ 配置: ${CADDY_CONFIG}"
echo ""
echo "🔍 監控指令："
echo "   後端日誌: sudo journalctl -u $SERVICE_NAME -f"
echo "   Caddy日誌: sudo journalctl -u caddy -f"
echo "   服務狀態: sudo systemctl status $SERVICE_NAME"
echo ""
echo "🚀 管理指令："
echo "   重啟後端: sudo systemctl restart $SERVICE_NAME"
echo "   重載Caddy: sudo systemctl reload caddy"
echo "   更新部署: cd $PROJECT_DIR && ./deploy.sh"
echo "   測試部署: cd $PROJECT_DIR && ./test-deployment.sh ${DOMAIN}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
