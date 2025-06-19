// 背景服務 (Service Worker)
// 處理擴展程序的後台邏輯

// 安裝事件
chrome.runtime.onInstalled.addListener(() => {
  console.log('枯枝逢生擴展程序已安裝');
});

// 處理來自內容腳本的消息
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  switch (message.type) {
    case 'SAVE_BOOKMARK':
      handleSaveBookmark(message.data, sendResponse);
      return true; // 保持消息通道開放

    case 'GET_RECOMMENDATIONS':
      handleGetRecommendations(message.data, sendResponse);
      return true;

    default:
      console.log('未知消息類型:', message.type);
  }
});

// 保存書籤
async function handleSaveBookmark(bookmarkData, sendResponse) {
  try {
    const response = await fetch('http://localhost:8000/api/v1/bookmarks/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(bookmarkData)
    });

    if (response.ok) {
      const bookmark = await response.json();
      sendResponse({ success: true, bookmark });
    } else {
      throw new Error('API 請求失敗');
    }
  } catch (error) {
    console.error('保存書籤失敗:', error);
    sendResponse({ success: false, error: error.message });
  }
}

// 獲取推薦
async function handleGetRecommendations(query, sendResponse) {
  try {
    const response = await fetch('http://localhost:8000/api/v1/search/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query, limit: 5 })
    });

    if (response.ok) {
      const recommendations = await response.json();
      sendResponse({ success: true, recommendations });
    } else {
      throw new Error('API 請求失敗');
    }
  } catch (error) {
    console.error('獲取推薦失敗:', error);
    sendResponse({ success: false, error: error.message });
  }
}

// 標籤頁更新事件
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  // 當頁面完成載入且 URL 包含搜尋引擎時
  if (changeInfo.status === 'complete' && tab.url) {
    const isSearchPage = 
      tab.url.includes('google.com/search') ||
      tab.url.includes('baidu.com/s');
    
    if (isSearchPage) {
      // 注入內容腳本 (如果尚未注入)
      chrome.scripting.executeScript({
        target: { tabId: tabId },
        files: ['content/content.js']
      });
    }
  }
});
