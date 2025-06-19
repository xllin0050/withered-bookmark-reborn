import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Bookmark } from '@/types/bookmark'

export const useBookmarkStore = defineStore('bookmark', () => {
  // State
  const bookmarks = ref<Bookmark[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const bookmarkCount = computed(() => bookmarks.value.length)
  const recentBookmarks = computed(() => 
    bookmarks.value
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 10)
  )

  // Actions
  function addBookmark(bookmark: Bookmark) {
    bookmarks.value.unshift(bookmark)
  }

  function removeBookmark(id: number) {
    const index = bookmarks.value.findIndex(b => b.id === id)
    if (index > -1) {
      bookmarks.value.splice(index, 1)
    }
  }

  function updateBookmark(id: number, updates: Partial<Bookmark>) {
    const bookmark = bookmarks.value.find(b => b.id === id)
    if (bookmark) {
      Object.assign(bookmark, updates)
    }
  }

  function setBookmarks(newBookmarks: Bookmark[]) {
    bookmarks.value = newBookmarks
  }

  function setLoading(loading: boolean) {
    isLoading.value = loading
  }

  function setError(newError: string | null) {
    error.value = newError
  }

  return {
    // State
    bookmarks,
    isLoading,
    error,
    // Getters
    bookmarkCount,
    recentBookmarks,
    // Actions
    addBookmark,
    removeBookmark,
    updateBookmark,
    setBookmarks,
    setLoading,
    setError
  }
})
