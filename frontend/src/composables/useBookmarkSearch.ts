import { ref, computed } from 'vue'
import { useSearchStore } from '@/stores/search'

export function useBookmarkSearch() {
  const searchStore = useSearchStore()
  const searchQuery = ref('')

  // 計算屬性：判斷是否顯示搜尋結果
  const showSearchResults = computed(() => {
    return (
      searchQuery.value.trim() !== '' ||
      searchStore.results.length > 0 ||
      searchStore.isLoading ||
      !!searchStore.error
    )
  })

  // 計算屬性：判斷是否顯示全部書籤
  const showAllBookmarks = computed(() => {
    return !showSearchResults.value
  })

  const handleSearch = () => {
    if (!searchQuery.value.trim()) return
    searchStore.performSearch({ query: searchQuery.value, limit: 20 })
  }

  const clearSearch = () => {
    searchQuery.value = ''
    searchStore.clearSearch()
  }

  return {
    searchQuery,
    searchStore,
    showSearchResults,
    showAllBookmarks,
    handleSearch,
    clearSearch
  }
}
