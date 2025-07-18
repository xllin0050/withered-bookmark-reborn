<template>
  <div>
    <!-- 導航欄 -->
    <TheHeader>
      <template #actions>
        <RouterLink to="/search" class="btn-secondary"> 搜尋 </RouterLink>
        <RouterLink to="/" class="btn-primary"> 首頁 </RouterLink>
      </template>
    </TheHeader>

    <!-- 搜尋欄位 -->
    <div class="mx-auto my-4 max-w-4xl text-center">
      <form
        class="flex w-full justify-center gap-3"
        @submit.prevent="handleSearch"
      >
        <input
          v-model="searchQuery"
          type="text"
          class="flex-1 rounded-lg border border-slate-300 bg-slate-50 px-4 py-3 text-base transition focus:border-amber-500 focus:ring-2 focus:ring-indigo-200 focus:outline-none"
          placeholder="請輸入關鍵字..."
        />
        <button
          type="submit"
          :disabled="searchStore.isLoading"
          class="h-12 rounded-lg bg-gradient-to-r from-amber-400 to-orange-600 px-6 font-semibold text-white shadow transition hover:from-indigo-700 hover:to-orange-600 focus:ring-2 focus:ring-indigo-300 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
        >
          <span v-if="!searchStore.isLoading">搜尋</span>
          <span v-else>搜尋中...</span>
        </button>
      </form>
      <div class="mt-4">
      <button
        v-if="showSearchResults"
        @click="clearSearch"
        class="rounded-lg bg-slate-500 px-4 py-2 text-white transition hover:bg-slate-600 focus:ring-2 focus:ring-slate-300 focus:outline-none"
      >
        清除搜尋，顯示全部書籤
      </button>
      <p v-else class="text-slate-600 mt-2">
        目前顯示全部書籤 ({{ bookmarkStore.bookmarks.length }})
      </p>
    </div>
    </div>

    <!-- 搜尋結果 -->
    <div v-if="showSearchResults" class="mt-12">
      <!-- 載入中 -->
      <div v-if="searchStore.isLoading" class="text-center">
        <p class="text-slate-600">正在搜尋中，請稍候...</p>
      </div>

      <!-- 錯誤訊息 -->
      <div
        v-else-if="searchStore.error"
        class="rounded-lg bg-red-100 p-4 text-center text-red-700"
      >
        <p>搜尋時發生錯誤: {{ searchStore.error }}</p>
      </div>

      <!-- 搜尋結果 -->
      <div v-else-if="searchStore.results.length > 0" class="space-y-6">
        <h2 class="text-xl font-semibold text-slate-700">
          搜尋結果 ({{ searchStore.results.length }})
        </h2>
        <div
          v-for="result in searchStore.results"
          :key="result.bookmark.id"
          class="rounded-xl border border-slate-200 bg-white p-6 shadow-md transition-shadow hover:shadow-lg"
        >
          <a
            :href="result.bookmark.url"
            target="_blank"
            class="text-xl font-bold text-indigo-600 hover:underline"
            >{{ result.bookmark.title }}</a
          >
          <p class="mt-1 truncate text-sm text-slate-500">
            {{ result.bookmark.url }}
          </p>
          <p class="mt-3 text-slate-700">{{ result.bookmark.description }}</p>
          <div
            v-if="result.matched_keywords.length > 0"
            class="mt-4 flex flex-wrap gap-2"
          >
            <span
              v-for="keyword in result.matched_keywords"
              :key="keyword"
              class="rounded-full bg-sky-100 px-2 py-1 text-xs font-medium text-sky-800"
              >{{ keyword }}</span
            >
          </div>
        </div>
      </div>

      <!-- 初始或無結果提示 -->
      <div v-else class="text-center">
        <p class="text-slate-600">
          請輸入關鍵字以開始搜尋，或嘗試不同的關鍵字。
        </p>
      </div>
    </div>

    <!-- 全部書籤 -->
    <div v-if="showAllBookmarks">
      <div v-if="bookmarkStore.isLoading">Loading...</div>
      <div v-else-if="bookmarkStore.error">
        Error: {{ bookmarkStore.error }}
      </div>
      <div v-else>
        <RecycleScroller
          ref="scroller"
          class="scroller"
          :items="bookmarkStore.bookmarks"
          :item-size="100"
          key-field="id"
          :buffer="200"
        >
          <template #default="props">
            <div class="bg-si border-er hover:border-yi group h-24">
              <a
                :href="props.item.url"
                target="_blank"
                class="relative block h-full w-full p-4"
              >
                <h3 class="text-lg font-semibold">{{ props.item.title }}</h3>
                <p class="mt-2 text-sm text-gray-600">
                  {{ props.item.description }}
                </p>
                <div
                  class="absolute top-1/2 right-0 hidden -translate-y-1/2 p-2 group-hover:block"
                >
                  <button
                    class="btn-shape bg-er text-si mr-2"
                    @click.prevent="updateBookmark(props.item)"
                  >
                    Update
                  </button>
                  <button
                    class="btn-shape bg-amber-400 text-red-600"
                    @click.prevent="deleteBookmark(props.item.id)"
                  >
                    Delete
                  </button>
                </div>
              </a>
            </div>
          </template>
        </RecycleScroller>
      </div>
    </div>
    <UpdateBookmarkModal
      :show="updateModalShow"
      :bookmark="selectedBookmark"
      @close="handleModalClose"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useSearchStore } from '@/stores/search'
import { useBookmarkStore } from '@/stores/bookmark'
import type { Bookmark } from '@/types/bookmark'
import UpdateBookmarkModal from '@/components/UpdateBookmarkModal.vue'
import TheHeader from '@/components/base/TheHeader.vue'

const bookmarkStore = useBookmarkStore()

const updateModalShow = ref(false)
const selectedBookmark = ref<Bookmark | null>(null)

const searchQuery = ref('')
const searchStore = useSearchStore()

// 計算屬性：判斷是否顯示搜尋結果
const showSearchResults = computed(() => {
  return (
    searchQuery.value.trim() !== '' ||
    searchStore.results.length > 0 ||
    searchStore.isLoading ||
    searchStore.error
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

const deleteBookmark = (id: number) => {
  bookmarkStore.deleteBookmarkData(id)
}

const updateBookmark = (bookmark: Bookmark) => {
  selectedBookmark.value = bookmark
  updateModalShow.value = true
}

const handleModalClose = () => {
  updateModalShow.value = false
  selectedBookmark.value = null
}

onMounted(() => {
  if (bookmarkStore.bookmarks.length === 0) {
    bookmarkStore.fetchBookmarkData()
  }
})
</script>

<style scoped>
.scroller {
  width: 100%;
  height: calc(100vh - 300px);
}
</style>
