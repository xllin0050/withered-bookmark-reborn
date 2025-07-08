<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-200">
    <!-- 導航欄 -->
    <TheHeader>
      <template #actions>
        <RouterLink to="/bookmarks" class="ml-3 px-3 py-1.5 rounded-md bg-slate-100 text-slate-700 font-medium border border-slate-200 hover:bg-indigo-600 hover:text-white hover:shadow transition-colors">我的書籤</RouterLink>
        <RouterLink to="/" class="ml-3 px-3 py-1.5 rounded-md bg-slate-100 text-slate-700 font-medium border border-slate-200 hover:bg-indigo-600 hover:text-white hover:shadow transition-colors">首頁</RouterLink>
      </template>
    </TheHeader>
    <main class="max-w-xl mx-auto bg-white rounded-2xl shadow-xl p-8 mt-12 flex flex-col items-center">
      <h1 class="text-2xl sm:text-3xl font-bold text-slate-700 mb-8 tracking-wide text-center">🔍 搜尋書籤</h1>
      <form class="w-full flex gap-3 justify-center" @submit.prevent>
        <input type="text" class="flex-1 px-4 py-3 border border-slate-300 rounded-lg text-base focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 bg-slate-50 transition" placeholder="請輸入關鍵字..." />
        <button class="px-6 h-12 bg-gradient-to-r from-indigo-500 to-sky-400 text-white rounded-lg font-semibold shadow hover:from-indigo-700 hover:to-sky-600 focus:outline-none focus:ring-2 focus:ring-indigo-300 transition">搜尋</button>
      </form>
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router';
import TheHeader from '@/components/base/TheHeader.vue';
</script>
