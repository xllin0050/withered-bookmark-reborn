import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { SearchRequest, SearchResult } from '@/types/bookmark';
import { bookmarkApi } from '@/services/api';

export const useSearchStore = defineStore('search', () => {
  // State
  const results = ref<SearchResult[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // Actions
  async function performSearch(request: SearchRequest) {
    isLoading.value = true;
    error.value = null;
    results.value = []; // 清空上次結果

    try {
      const response = await bookmarkApi.searchBookmarks(request);
      results.value = response;
    } catch (e: any) {
      error.value = e.message || '發生未知的搜尋錯誤';
    } finally {
      isLoading.value = false;
    }
  }

  return {
    results,
    isLoading,
    error,
    performSearch,
  };
});
