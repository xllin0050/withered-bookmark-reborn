<template>
  <div class="flex min-h-screen flex-col">
    <!-- 導航欄 -->
    <TheHeader>
      <template #actions>
        <RouterLink to="/search" class="btn-secondary"> 搜尋 </RouterLink>
        <RouterLink to="/bookmarks" class="btn-primary"> 我的書籤 </RouterLink>
      </template>
    </TheHeader>

    <!-- 主要內容 -->
    <main
      class="mx-auto flex max-w-4xl flex-grow flex-col px-4 py-12 sm:px-6 lg:px-8"
    >
      <!-- Hero Section -->
      <div class="mb-12 flex-grow text-center">
        <h2 class="mb-8 text-2xl font-bold sm:text-4xl">
          讓沉睡的書籤重新發揮價值
        </h2>
        <p class="mb-8 text-base text-gray-600">
          在你搜尋時自動推薦相關的已收藏內容，<br />智能書籤助手讓知識重新流動
        </p>
        <div class="flex justify-center space-x-4">
          <button
            class="rounded-lg bg-orange-400 px-4 py-2 font-medium text-white transition-colors hover:bg-yellow-400 hover:text-gray-500"
            @click="openModal"
          >
            開始使用
          </button>
          <button
            class="rounded-lg bg-orange-300 px-4 py-2 font-medium text-white transition-colors hover:bg-yellow-300 hover:text-gray-500"
          >
            了解更多
          </button>
        </div>
      </div>

      <!-- 功能特色 -->
      <div class="mb-12 grid gap-8 md:grid-cols-3">
        <div class="card text-center">
          <div class="mb-4 text-3xl">🔍</div>
          <h3 class="mb-2 text-lg font-semibold">智能搜尋增強</h3>
          <p class="text-sm text-gray-600">自動推薦相關的已收藏內容</p>
        </div>
        <div class="card text-center">
          <div class="mb-4 text-3xl">🧠</div>
          <h3 class="mb-2 text-lg font-semibold">語義分析</h3>
          <p class="text-sm text-gray-600">提取關鍵字，理解內容本質</p>
        </div>
        <div class="card text-center">
          <div class="mb-4 text-3xl">⚡</div>
          <h3 class="mb-2 text-lg font-semibold">一鍵收藏</h3>
          <p class="text-sm text-gray-600">讓收藏變得簡單快速</p>
        </div>
      </div>

      <!-- 統計資訊 -->
      <div class="card">
        <h3 class="mb-4 text-lg font-semibold">快速統計</h3>
        <div class="grid grid-cols-2 gap-4 md:grid-cols-4">
          <div class="text-center">
            <div class="text-2xl font-bold text-green-600">
              {{ bookmarkCount }}
            </div>
            <div class="text-sm text-gray-500">總書籤數</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-green-600">0</div>
            <div class="text-sm text-gray-500">今日搜尋</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-green-600">0</div>
            <div class="text-sm text-gray-500">推薦命中</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-green-600">0</div>
            <div class="text-sm text-gray-500">重新發現</div>
          </div>
        </div>
      </div>
    </main>
    <AddNewBookmarkModal :show="isModalOpen" @close="closeModal" />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { RouterLink } from "vue-router";
import { useBookmarkStore } from "@/stores/bookmark";
import { storeToRefs } from "pinia";
import AddNewBookmarkModal from "@/components/AddNewBookmarkModal.vue";
import TheHeader from "@/components/base/TheHeader.vue";

const bookmarkStore = useBookmarkStore();
const { bookmarkCount } = storeToRefs(bookmarkStore);

const isModalOpen = ref(false);

const openModal = () => {
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
};
</script>
