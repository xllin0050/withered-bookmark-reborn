import { ref } from 'vue'
import type { Bookmark } from '@/types/bookmark'

export function useBookmarkModal() {
  const updateModalShow = ref(false)
  const selectedBookmark = ref<Bookmark | null>(null)

  const updateBookmark = (bookmark: Bookmark) => {
    selectedBookmark.value = bookmark
    updateModalShow.value = true
  }

  const handleModalClose = () => {
    updateModalShow.value = false
    selectedBookmark.value = null
  }

  return {
    updateModalShow,
    selectedBookmark,
    updateBookmark,
    handleModalClose
  }
}
