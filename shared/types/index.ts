// 共用的 TypeScript 類型定義
// 可以在前端和擴展程序中使用

export interface Bookmark {
  id: number;
  url: string;
  title: string;
  description?: string;
  content?: string;
  keywords?: string[];
  created_at: string;
  updated_at: string;
  access_count: number;
  last_accessed?: string;
}

export interface BookmarkCreate {
  url: string;
  title: string;
  description?: string;
}

export interface BookmarkUpdate {
  title?: string;
  description?: string;
}

export interface SearchResult {
  bookmark: Bookmark;
  relevance_score: number;
  matched_keywords: string[];
}

export interface SearchRequest {
  query: string;
  limit?: number;
}

export interface AnalyzeUrlRequest {
  url: string;
}

export interface AnalyzeUrlResponse {
  title: string;
  content: string;
  keywords: string[];
  summary: string;
}

// 擴展程序相關類型
export interface ExtensionMessage {
  type: 'SAVE_BOOKMARK' | 'SEARCH_RECOMMENDATIONS' | 'GET_BOOKMARKS';
  data?: any;
}

export interface RecommendationCard {
  bookmark: Bookmark;
  relevance_score: number;
  position: 'top' | 'sidebar' | 'inline';
}

// API 響應類型
export interface ApiResponse<T> {
  data: T;
  status: 'success' | 'error';
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  has_next: boolean;
  has_prev: boolean;
}
