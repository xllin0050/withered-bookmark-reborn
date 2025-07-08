<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-200 pb-20">
    <!-- 導航欄 -->
    <TheHeader>
      <template #actions>
        <RouterLink to="/bookmarks" class="ml-3 px-3 py-1.5 rounded-md bg-slate-100 text-slate-700 font-medium border border-slate-200 hover:bg-indigo-600 hover:text-white hover:shadow transition-colors">我的書籤</RouterLink>
        <RouterLink to="/" class="ml-3 px-3 py-1.5 rounded-md bg-slate-100 text-slate-700 font-medium border border-slate-200 hover:bg-indigo-600 hover:text-white hover:shadow transition-colors">首頁</RouterLink>
      </template>
    </TheHeader>

    <!-- 搜尋區域 -->
    <main class="max-w-3xl mx-auto mt-12">
      <div class="bg-white rounded-2xl shadow-xl p-8 flex flex-col items-center">
        <h1 class="text-2xl sm:text-3xl font-bold text-slate-700 mb-8 tracking-wide text-center">🔍 搜尋書籤</h1>
        <form class="w-full flex gap-3 justify-center" @submit.prevent="handleSearch">
          <input
            v-model="searchQuery"
            type="text"
            class="flex-1 px-4 py-3 border border-slate-300 rounded-lg text-base focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 bg-slate-50 transition"
            placeholder="請輸入關鍵字..."
          />
          <button
            type="submit"
            :disabled="searchStore.isLoading"
            class="px-6 h-12 bg-gradient-to-r from-indigo-500 to-sky-400 text-white rounded-lg font-semibold shadow hover:from-indigo-700 hover:to-sky-600 focus:outline-none focus:ring-2 focus:ring-indigo-300 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="!searchStore.isLoading">搜尋</span>
            <span v-else>搜尋中...</span>
          </button>
        </form>
      </div>

      <!-- 結果區域 -->
      <div class="mt-12">
        <!-- 載入中 -->
        <div v-if="searchStore.isLoading" class="text-center">
          <p class="text-slate-600">正在搜尋中，請稍候...</p>
        </div>

        <!-- 錯誤訊息 -->
        <div v-else-if="searchStore.error" class="text-center bg-red-100 text-red-700 p-4 rounded-lg">
          <p>搜尋時發生錯誤: {{ searchStore.error }}</p>
        </div>

        <!-- 搜尋結果 -->
        <div v-else-if="searchStore.results.length > 0" class="space-y-6">
           <h2 class="text-xl font-semibold text-slate-700">搜尋結果 ({{ searchStore.results.length }})</h2>
          <div v-for="result in searchStore.results" :key="result.bookmark.id" class="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow border border-slate-200">
            <a :href="result.bookmark.url" target="_blank" class="text-xl font-bold text-indigo-600 hover:underline">{{ result.bookmark.title }}</a>
            <p class="text-sm text-slate-500 mt-1 truncate">{{ result.bookmark.url }}</p>
            <p class="text-slate-700 mt-3">{{ result.bookmark.description }}</p>
            <div v-if="result.matched_keywords.length > 0" class="mt-4 flex flex-wrap gap-2">
              <span v-for="keyword in result.matched_keywords" :key="keyword" class="px-2 py-1 bg-sky-100 text-sky-800 text-xs font-medium rounded-full">{{ keyword }}</span>
            </div>
          </div>
        </div>

        <!-- 初始或無結果提示 -->
        <div v-else class="text-center">
          <p class="text-slate-600">請輸入關鍵字以開始搜尋，或嘗試不同的關鍵字。</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { RouterLink } from 'vue-router';
import TheHeader from '@/components/base/TheHeader.vue';
import { useSearchStore } from '@/stores/search';

const searchQuery = ref('');
const searchStore = useSearchStore();

const handleSearch = () => {
  if (!searchQuery.value.trim()) return;
  searchStore.performSearch({ query: searchQuery.value, limit: 20 });
};
</script>
