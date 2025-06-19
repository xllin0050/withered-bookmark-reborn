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

export interface SearchResult {
  bookmark: Bookmark;
  relevance_score: number;
  matched_keywords: string[];
}

export interface SearchRequest {
  query: string;
  limit?: number;
}

export interface AnalyzeUrlResponse {
  title: string;
  content: string;
  keywords: string[];
  summary: string;
}
