<template>
  <div class="min-h-screen">
    <!-- 導航欄 -->
    <TheHeader>
      <template #actions>
        <RouterLink to="/bookmarks" class="btn-secondary">我的書籤</RouterLink>
        <RouterLink to="/" class="btn-primary">首頁</RouterLink>
      </template>
    </TheHeader>

    <!-- 搜尋區域 -->
    <main class="mx-auto mt-12 max-w-4xl">
      <div class="p-4">
        <div
          class="bg-si flex flex-col items-center rounded-2xl px-4 py-8 shadow-xl"
        >
          <h1
            class="mb-4 text-center text-2xl font-bold tracking-wide text-gray-700 sm:text-3xl"
          >
            🔍 搜尋書籤
          </h1>
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
        </div>
      </div>

      <!-- 結果區域 -->
      <div class="mt-12">
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
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { RouterLink } from "vue-router";
import TheHeader from "@/components/base/TheHeader.vue";
import { useSearchStore } from "@/stores/search";

const searchQuery = ref("");
const searchStore = useSearchStore();

const handleSearch = () => {
  if (!searchQuery.value.trim()) return;
  searchStore.performSearch({ query: searchQuery.value, limit: 20 });
};
</script>
