import axios from 'axios'
import type { Bookmark, BookmarkCreate, SearchRequest, SearchResult, AnalyzeUrlResponse } from '@/types/bookmark'

// 生產環境使用相對路徑，開發環境使用完整 URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 增加超時時間，因為有機器學習處理
  headers: {
    'Content-Type': 'application/json',
  },
})

// 請求攔截器
api.interceptors.request.use(
  (config) => {
    if (import.meta.env.VITE_APP_DEBUG) {
      console.log(`API Request: ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`)
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 響應攔截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API Error:', error)
    return bookmarkApi.handleError(error)
  }
)

export const bookmarkApi = {
  // 獲取所有書籤
  async getBookmarks(skip = 0, limit = 100): Promise<Bookmark[]> {
    return api.get('/bookmarks', { params: { skip, limit } })
  },

  // 創建書籤
  async createBookmark(bookmark: BookmarkCreate): Promise<Bookmark> {
    return api.post('/bookmarks', bookmark)
  },

  // 獲取單個書籤
  async getBookmark(id: number): Promise<Bookmark> {
    return api.get(`/bookmarks/${id}`)
  },

  // 更新書籤
  async updateBookmark(id: number, updates: Partial<BookmarkCreate>): Promise<Bookmark> {
    return api.put(`/bookmarks/${id}`, updates)
  },

  // 刪除書籤
  async deleteBookmark(id: number): Promise<void> {
    return api.delete(`/bookmarks/${id}`)
  },

  // 搜尋書籤 - 修正路徑
  async searchBookmarks(searchRequest: SearchRequest): Promise<SearchResult[]> {
    return api.post('/search/', searchRequest) // 注意這裡的路徑
  },

  // 分析 URL - 修正路徑
  async analyzeUrl(url: string): Promise<AnalyzeUrlResponse> {
    return api.post('/search/analyze-url', { url })
  },

  // 豐富化書籤內容
  async enrichBookmark(id: number): Promise<void> {
    return api.post(`/bookmarks/${id}/enrich`)
  },

  // 上傳書籤檔案
  async uploadBookmarks(file: File): Promise<{ message: string; count: number }> {
    const formData = new FormData()
    formData.append('file', file)

    return api.post('/bookmarks/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000, // 檔案上傳需要更長時間
    })
  },

  // 批量向量化
  async batchVectorize(): Promise<{ message: string; total_bookmarks: number }> {
    return api.post('/bookmarks/batch-vectorize')
  },

  // 重新訓練向量化器
  async retrainVectorizer(): Promise<{ message: string; total_bookmarks: number }> {
    return api.post('/bookmarks/retrain-vectorizer')
  },

  // 獲取搜尋系統健康狀態
  async getSearchHealth(): Promise<any> {
    return api.get('/search/health')
  },

  // 獲取向量化器統計
  async getVectorizerStats(): Promise<any> {
    return api.get('/search/vectorizer/stats')
  },

  // 清空向量化器快取
  async clearVectorizerCache(): Promise<any> {
    return api.post('/search/vectorizer/clear-cache')
  },

  // 增強錯誤處理
  async handleError(error: any) {
    if (error.response) {
      // 處理不同的 HTTP 狀態碼
      switch (error.response.status) {
        case 422:
          // 驗證錯誤
          if (error.response.data.detail) {
            const errorDetails = error.response.data.detail
            if (Array.isArray(errorDetails)) {
              return Promise.reject(new Error(errorDetails.map(d => d.msg).join('\n')))
            }
          }
          break
        case 404:
          return Promise.reject(new Error('資源不存在'))
        case 500:
          return Promise.reject(new Error('伺服器內部錯誤'))
        case 503:
          return Promise.reject(new Error('服務暫時不可用'))
        default:
          break
      }
      return Promise.reject(new Error(error.response.data.detail || '發生未知錯誤'))
    } else if (error.request) {
      return Promise.reject(new Error('網路連線錯誤'))
    }
    return Promise.reject(error)
  }
}

export default api
