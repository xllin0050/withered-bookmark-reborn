// 內容腳本 - 在搜尋頁面中運行
// 檢測搜尋查詢並注入推薦卡片

class WitheredBookmarkContentScript {
  constructor() {
    this.apiBaseUrl = 'http://localhost:8000/api/v1';
    this.init();
  }

  async init() {
    console.log('枯枝逢生內容腳本已載入');
    
    // 檢測當前是否為搜尋頁面
    if (this.isSearchPage()) {
      const query = this.extractSearchQuery();
      
      if (query) {
        console.log('檢測到搜尋查詢:', query);
        await this.showRecommendations(query);
      }
    }
  }

  isSearchPage() {
    const url = window.location.href;
    return url.includes('google.com/search') || url.includes('baidu.com/s');
  }

  extractSearchQuery() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('q') || urlParams.get('wd') || '';
  }

  async showRecommendations(query) {
    try {
      // 向背景腳本請求推薦
      const response = await new Promise((resolve) => {
        chrome.runtime.sendMessage({
          type: 'GET_RECOMMENDATIONS',
          data: query
        }, resolve);
      });

      if (response.success && response.recommendations.length > 0) {
        this.injectRecommendationCard(response.recommendations);
      }
    } catch (error) {
      console.error('獲取推薦失敗:', error);
    }
  }

  injectRecommendationCard(recommendations) {
    // 檢查是否已經注入過
    if (document.getElementById('withered-bookmark-recommendations')) {
      return;
    }

    const card = this.createRecommendationCard(recommendations);
    
    // 找到合適的插入位置
    const insertTarget = this.findInsertionPoint();
    
    if (insertTarget) {
      insertTarget.insertAdjacentElement('afterend', card);
    }
  }

  createRecommendationCard(recommendations) {
    const card = document.createElement('div');
    card.id = 'withered-bookmark-recommendations';
    card.innerHTML = `
      <div style="
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 16px;
        margin: 16px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        font-family: Arial, sans-serif;
      ">
        <div style="
          display: flex;
          align-items: center;
          margin-bottom: 12px;
          color: #374151;
          font-size: 14px;
          font-weight: 600;
        ">
          <span style="margin-right: 8px;">🌱</span>
          枯枝逢生 - 你的相關收藏
        </div>
        <div id="recommendations-list">
          ${recommendations.map(rec => this.createRecommendationItem(rec)).join('')}
        </div>
        <div style="
          text-align: right;
          margin-top: 8px;
          font-size: 12px;
          color: #6b7280;
        ">
          <a href="http://localhost:3000" target="_blank" style="color: #3b82f6; text-decoration: none;">
            查看更多收藏 →
          </a>
        </div>
      </div>
    `;
    
    return card;
  }

  createRecommendationItem(recommendation) {
    const { bookmark, relevance_score } = recommendation;
    
    return `
      <div style="
        padding: 8px 0;
        border-bottom: 1px solid #f3f4f6;
        margin-bottom: 8px;
      ">
        <a href="${bookmark.url}" style="
          color: #1d4ed8;
          text-decoration: none;
          font-size: 14px;
          font-weight: 500;
        " target="_blank">
          ${bookmark.title}
        </a>
        <div style="
          color: #6b7280;
          font-size: 12px;
          margin-top: 4px;
        ">
          ${bookmark.description || ''}
          <span style="float: right;">
            相關度: ${Math.round(relevance_score * 100)}%
          </span>
        </div>
      </div>
    `;
  }

  findInsertionPoint() {
    // Google 搜尋結果頁面
    if (window.location.hostname.includes('google.com')) {
      return document.querySelector('#search') || document.querySelector('#res');
    }
    
    // 百度搜尋結果頁面
    if (window.location.hostname.includes('baidu.com')) {
      return document.querySelector('#content_left') || document.querySelector('#results');
    }
    
    return null;
  }
}

// 當頁面載入完成時初始化
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => new WitheredBookmarkContentScript());
} else {
  new WitheredBookmarkContentScript();
}
