<template>
  <div>
    <h1>Bookmarks</h1>
        <div v-if="bookmarkStore.isLoading">Loading...</div>
    <div v-else-if="bookmarkStore.error">Error: {{ bookmarkStore.error }}</div>
    <ul v-else>
      <li v-for="bookmark in bookmarkStore.bookmarks" :key="bookmark.id">
        <a :href="bookmark.url" target="_blank">{{ bookmark.title }}</a>
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