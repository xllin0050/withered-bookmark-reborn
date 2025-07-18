<template>
  <div>
    <!-- 導航欄 -->
    <TheHeader>
      <template #actions>
        <RouterLink to="/search" class="btn-secondary"> 搜尋 </RouterLink>
        <RouterLink to="/" class="btn-primary"> 首頁 </RouterLink>
      </template>
    </TheHeader>

    <SearchBar
      v-model="searchQuery"
      :is-loading="searchStore.isLoading"
      :show-clear-button="showSearchResults"
      :total-bookmarks="bookmarkStore.bookmarks.length"
      class="mx-auto my-4 max-w-4xl text-center"
      @search="handleSearch"
      @clear="clearSearch"
    />

    <SearchResults
      v-if="showSearchResults"
      :results="searchStore.results"
      :is-loading="searchStore.isLoading"
      :error="searchStore.error"
      class="mx-auto mt-12 max-w-4xl"
    />

    <BookmarkList
      v-if="showAllBookmarks"
      :bookmarks="bookmarkStore.bookmarks"
      :is-loading="bookmarkStore.isLoading"
      :error="bookmarkStore.error"
      class="mx-auto mt-12 max-w-4xl"
      @update="updateBookmark"
      @delete="deleteBookmark"
    />

    <UpdateBookmarkModal
      :show="updateModalShow"
      :bookmark="selectedBookmark"
      @close="handleModalClose"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useBookmarkStore } from '@/stores/bookmark'
import { useBookmarkSearch } from '@/composables/useBookmarkSearch'
import { useBookmarkModal } from '@/composables/useBookmarkModal'

// 元件引入
import TheHeader from '@/components/base/TheHeader.vue'
import SearchBar from '@/components/SearchBar.vue'
import SearchResults from '@/components/SearchResults.vue'
import BookmarkList from '@/components/BookmarkList.vue'
import UpdateBookmarkModal from '@/components/UpdateBookmarkModal.vue'

const bookmarkStore = useBookmarkStore()

const {
  searchQuery,
  searchStore,
  showSearchResults,
  showAllBookmarks,
  handleSearch,
  clearSearch
} = useBookmarkSearch()

const {
  updateModalShow,
  selectedBookmark,
  updateBookmark,
  handleModalClose
} = useBookmarkModal()

const deleteBookmark = (id: number) => {
  bookmarkStore.deleteBookmarkData(id)
}

onMounted(() => {
  if (bookmarkStore.bookmarks.length === 0) {
    bookmarkStore.fetchBookmarkData()
  }
})
</script>


