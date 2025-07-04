import axios from 'axios'
import type { Bookmark, BookmarkCreate, SearchRequest, SearchResult, AnalyzeUrlResponse } from '@/types/bookmark'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 請求攔截器
api.interceptors.request.use(
  (config) => {
    // 可以在這裡添加認證 token
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

  // 搜尋書籤
  async searchBookmarks(searchRequest: SearchRequest): Promise<SearchResult[]> {
    return api.post('/search', searchRequest)
  },

  // 分析 URL
  async analyzeUrl(url: string): Promise<AnalyzeUrlResponse> {
    return api.post('/search/analyze-url', { url })
  },

  // 豐富化書籤內容
  async enrichBookmark(id: number): Promise<void> {
    return api.post(`/bookmarks/${id}/enrich`)
  },

  // 增加更好的錯誤處理
  async handleError(error: any) {
    if (error.response) {
      // 處理 422 驗證錯誤
      if (error.response.status === 422 && error.response.data.detail) {
        const errorDetails = error.response.data.detail
        if (Array.isArray(errorDetails)) {
          return Promise.reject(new Error(errorDetails.map(d => d.msg).join('\n')))
        }
      }
      // 處理其他錯誤
      return Promise.reject(new Error(error.response.data.detail || 'An error occurred'))
    }
    return Promise.reject(error)
  }

}

export default api
