#!/bin/bash
# test-deployment.sh - 部署後測試腳本

DOMAIN=${1:-"localhost"}
PROTOCOL="http"

if [ "$DOMAIN" != "localhost" ]; then
    PROTOCOL="https"
fi

BASE_URL="${PROTOCOL}://${DOMAIN}"

echo "🧪 測試部署的 Withered Bookmark 應用..."
echo "🌐 測試 URL: $BASE_URL"
echo ""

# 測試函數
test_endpoint() {
    local name=$1
    local url=$2
    local method=${3:-GET}
    local data=${4:-""}
    
    echo -n "測試 $name... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "%{http_code}" -o /tmp/test_response "$url")
    else
        response=$(curl -s -w "%{http_code}" -o /tmp/test_response -X "$method" -H "Content-Type: application/json" -d "$data" "$url")
    fi
    
    if [ "$response" = "200" ] || [ "$response" = "201" ]; then
        echo "✅ 通過 ($response)"
        return 0
    else
        echo "❌ 失敗 ($response)"
        echo "回應內容:"
        cat /tmp/test_response
        echo ""
        return 1
    fi
}

# 開始測試
echo "📋 基礎服務測試"
echo "─────────────────────"

# 1. 健康檢查
test_endpoint "健康檢查" "$BASE_URL/health"

# 2. 前端頁面
test_endpoint "前端頁面" "$BASE_URL/"

# 3. API 根路徑
test_endpoint "API 根路徑" "$BASE_URL/api/v1/"

echo ""
echo "📚 書籤 API 測試"
echo "─────────────────────"

# 4. 獲取書籤列表
test_endpoint "書籤列表" "$BASE_URL/api/v1/bookmarks"

# 5. 搜尋功能
test_endpoint "搜尋功能" "$BASE_URL/api/v1/search/" "POST" '{"query":"test","limit":5}'

echo ""
echo "🔍 搜尋系統測試"
echo "─────────────────────"

# 6. 搜尋系統健康檢查
test_endpoint "搜尋系統健康" "$BASE_URL/api/v1/search/health"

# 7. 向量化器統計
test_endpoint "向量化器統計" "$BASE_URL/api/v1/search/vectorizer/stats"

echo ""
echo "📊 測試總結"
echo "─────────────────────"

# 統計測試結果
total_tests=7
passed_tests=$(grep -c "✅ 通過" /tmp/test_results 2>/dev/null || echo "0")

# 重新執行測試並計算
{
    test_endpoint "健康檢查" "$BASE_URL/health" > /dev/null 2>&1 && echo "pass" || echo "fail"
    test_endpoint "前端頁面" "$BASE_URL/" > /dev/null 2>&1 && echo "pass" || echo "fail"
    test_endpoint "API 根路徑" "$BASE_URL/api/v1/" > /dev/null 2>&1 && echo "pass" || echo "fail"
    test_endpoint "書籤列表" "$BASE_URL/api/v1/bookmarks" > /dev/null 2>&1 && echo "pass" || echo "fail"
    test_endpoint "搜尋功能" "$BASE_URL/api/v1/search/" "POST" '{"query":"test","limit":5}' > /dev/null 2>&1 && echo "pass" || echo "fail"
    test_endpoint "搜尋系統健康" "$BASE_URL/api/v1/search/health" > /dev/null 2>&1 && echo "pass" || echo "fail"
    test_endpoint "向量化器統計" "$BASE_URL/api/v1/search/vectorizer/stats" > /dev/null 2>&1 && echo "pass" || echo "fail"
} > /tmp/test_results

passed_tests=$(grep -c "pass" /tmp/test_results)

echo "通過測試: $passed_tests/$total_tests"

if [ "$passed_tests" -eq "$total_tests" ]; then
    echo "🎉 所有測試通過！部署成功！"
    exit 0
else
    echo "⚠️  有 $((total_tests - passed_tests)) 個測試失敗"
    echo ""
    echo "🔧 故障排除建議："
    echo "1. 檢查服務狀態: sudo systemctl status withered-bookmark"
    echo "2. 查看後端日誌: sudo journalctl -u withered-bookmark -f"
    echo "3. 查看 Caddy 日誌: sudo journalctl -u caddy -f"
    echo "4. 檢查埠口使用: netstat -tlnp | grep :8000"
    exit 1
fi

# 清理臨時檔案
rm -f /tmp/test_response /tmp/test_results
