<template>
  <div>
    <!-- 導航欄 -->
    <nav class="bg-si shadow-sm border-b">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-bold text-gray-900">枯枝逢生</h1>
          </div>
          <div class="flex items-center space-x-4">
            <RouterLink to="/search" class="btn-secondary"> 搜尋 </RouterLink>
            <RouterLink to="/" class="btn-primary">
              首頁
            </RouterLink>
          </div>
        </div>
      </div>
    </nav>
    <h1 class="text-center">Bookmarks</h1>
    <div v-if="bookmarkStore.isLoading">Loading...</div>
    <div v-else-if="bookmarkStore.error">Error: {{ bookmarkStore.error }}</div>
    <ul v-else class="max-w-4xl mx-auto">
      <li v-for="bookmark in bookmarkStore.bookmarks" :key="bookmark.id" class="border">
        <div>
          <h3>{{ bookmark.title }}</h3>
          <p>{{ bookmark.description }}</p>
          <a :href="bookmark.url" target="_blank">link</a>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useBookmarkStore } from '@/stores/bookmark';

const bookmarkStore = useBookmarkStore();

onMounted(() => {
  // Fetch bookmarks only if the list is empty to avoid redundant API calls
  if (bookmarkStore.bookmarks.length === 0) {
    bookmarkStore.fetchBookmarks();
  }
});
</script>