<template>
  <!-- 搜尋結果 -->
  <div>
    <!-- 載入中 -->
    <div v-if="isLoading" class="text-center">
      <p class="text-slate-600">正在搜尋中，請稍候...</p>
    </div>

    <!-- 錯誤訊息 -->
    <div
      v-else-if="error"
      class="rounded-lg bg-red-100 p-4 text-center text-red-700"
    >
      <p>搜尋時發生錯誤: {{ error }}</p>
    </div>

    <!-- 搜尋結果 -->
    <div v-else-if="results.length > 0" class="space-y-6">
      <h2 class="text-xl font-semibold text-slate-700">
        搜尋結果 ({{ results.length }})
      </h2>
      <div
        v-for="result in results"
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
      <p class="text-slate-600">請輸入關鍵字以開始搜尋，或嘗試不同的關鍵字。</p>
    </div>
  </div>
</template>
<script setup lang="ts">
import type { SearchResult } from '@/types/bookmark'

interface Props {
  results: SearchResult[]
  isLoading: boolean
  error: string | null
}

defineProps<Props>()
</script>