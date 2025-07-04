<template>
  <div>
    <!-- 導航欄 -->
    <nav class="bg-si border-b shadow-sm">
      <div class="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        <div class="flex h-16 justify-between">
          <div class="flex items-center">
            <h1 class="text-xl font-bold text-gray-900">枯枝逢生</h1>
          </div>
          <div class="flex items-center space-x-4">
            <RouterLink to="/search" class="btn-secondary"> 搜尋 </RouterLink>
            <RouterLink to="/" class="btn-primary"> 首頁 </RouterLink>
          </div>
        </div>
      </div>
    </nav>
    <h1 class="text-center">Bookmarks</h1>
    <div v-if="bookmarkStore.isLoading">Loading...</div>
    <div v-else-if="bookmarkStore.error">Error: {{ bookmarkStore.error }}</div>
    <div v-else>
      <ul class="mx-auto max-w-4xl">
        <li
          v-for="bookmark in bookmarkStore.bookmarks"
          :key="bookmark.id"
          class="border border-b-0 last:border-b"
        >
          <div class="p-4">
            <h3 class="text-lg font-semibold">{{ bookmark.title }}</h3>
            <p class="mt-2 text-sm text-gray-600">{{ bookmark.description }}</p>
            <div class="mt-2 flex space-x-2">
              <a class="btn-shape block" :href="bookmark.url" target="_blank"
                >link</a
              >
              <button
                class="btn-shape text-green-600"
                @click="updateBookmark(bookmark)"
              >
                Update
              </button>
              <button
                class="btn-shape text-red-600"
                @click="deleteBookmark(bookmark.id)"
              >
                Delete
              </button>
            </div>
            <div class="mt-4 flex space-x-2">
              <div v-for="keyword in bookmark.keywords" :key="keyword">
                <span class="rounded bg-gray-200 px-2 py-1">{{ keyword }}</span>
              </div>
            </div>
          </div>
        </li>
      </ul>
    </div>
    <UpdateBookmarkModal
      :show="updateModalShow"
      :bookmark="selectedBookmark"
      @close="handleModalClose"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useBookmarkStore } from "@/stores/bookmark";
import type { Bookmark } from "@/types/bookmark";
import UpdateBookmarkModal from "@/components/UpdateBookmarkModal.vue";

const bookmarkStore = useBookmarkStore();

const updateModalShow = ref(false);
const selectedBookmark = ref<Bookmark | null>(null);

const deleteBookmark = (id: number) => {
  bookmarkStore.deleteBookmarkData(id);
};

const updateBookmark = (bookmark: Bookmark) => {
  selectedBookmark.value = bookmark;
  updateModalShow.value = true;
};

const handleModalClose = () => {
  updateModalShow.value = false;
  selectedBookmark.value = null;
};

onMounted(() => {
  if (bookmarkStore.bookmarks.length === 0) {
    bookmarkStore.fetchBookmarkData();
  }
});
</script>
