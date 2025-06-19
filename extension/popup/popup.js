// 彈窗功能邏輯
const API_BASE_URL = 'http://localhost:8000/api/v1';

document.addEventListener('DOMContentLoaded', function() {
  const saveButton = document.getElementById('save-bookmark');
  const dashboardButton = document.getElementById('open-dashboard');
  const statusMessage = document.getElementById('status-message');
  
  // 保存當前頁面為書籤
  saveButton.addEventListener('click', async function() {
    try {
      statusMessage.textContent = '正在保存...';
      statusMessage.className = 'status saving';
      
      // 獲取當前活動標籤頁
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      const bookmark = {
        url: tab.url,
        title: tab.title,
        description: ''
      };

      // 發送到後端 API
      const response = await fetch(`${API_BASE_URL}/bookmarks/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(bookmark)
      });

      if (response.ok) {
        statusMessage.textContent = '✅ 保存成功！';
        statusMessage.className = 'status success';
        
        // 2秒後恢復狀態
        setTimeout(() => {
          statusMessage.textContent = '準備就緒';
          statusMessage.className = 'status';
        }, 2000);
      } else {
        throw new Error('保存失敗');
      }
    } catch (error) {
      console.error('保存書籤時發生錯誤:', error);
      statusMessage.textContent = '❌ 保存失敗';
      statusMessage.className = 'status error';
      
      setTimeout(() => {
        statusMessage.textContent = '準備就緒';
        statusMessage.className = 'status';
      }, 3000);
    }
  });

  // 打開管理面板
  dashboardButton.addEventListener('click', function() {
    chrome.tabs.create({ url: 'http://localhost:3000' });
  });

  // 設定和說明連結
  document.getElementById('settings').addEventListener('click', function(e) {
    e.preventDefault();
    // TODO: 實現設定頁面
    alert('設定功能開發中...');
  });

  document.getElementById('help').addEventListener('click', function(e) {
    e.preventDefault();
    chrome.tabs.create({ url: 'https://github.com/your-repo/withered-bookmark-reborn' });
  });
});

// 檢查 API 連接狀態
async function checkApiStatus() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (response.ok) {
      document.getElementById('status-message').textContent = '準備就緒';
    } else {
      throw new Error('API 連接失敗');
    }
  } catch (error) {
    document.getElementById('status-message').textContent = '⚠️ 後端離線';
    document.getElementById('status-message').className = 'status warning';
  }
}

// 頁面載入時檢查 API 狀態
checkApiStatus();
