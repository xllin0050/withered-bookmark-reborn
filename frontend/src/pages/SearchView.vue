<template>
  <div>
    <!-- 導航欄 -->
    <TheHeader>
      <template #actions>
        <RouterLink to="/bookmarks" class="btn-primary">
          我的書籤
        </RouterLink>
        <RouterLink to="/" class="btn-primary"> 首頁 </RouterLink>
      </template>
    </TheHeader>
    <main class="mx-auto max-w-4xl">
      <h1>Search</h1>
      <input type="text" />
      <button>Search</button>
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router';
import TheHeader from '@/components/base/TheHeader.vue';
</script>
