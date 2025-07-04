<template>
  <div class="min-h-screen bg-yi">
    <!-- 導航欄 -->
    <TheHeader>
      <template #actions>
        <RouterLink to="/search" class="btn-secondary"> 搜尋 </RouterLink>
        <RouterLink to="/bookmarks" class="btn-primary">
          我的書籤
        </RouterLink>
      </template>
    </TheHeader>

    <!-- 主要內容 -->
    <main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <!-- Hero Section -->
      <div class="text-center mb-12">
        <h2 class="text-2xl sm:text-4xl font-bold text-si mb-4">
          讓沉睡的書籤重新發揮價值
        </h2>
        <p class="text-base text-san mb-8">
          在你搜尋時自動推薦相關的已收藏內容，智能書籤助手讓知識重新流動
        </p>
        <div class="flex justify-center space-x-4">
          <button class="btn-primary text-lg px-8 py-3" @click="openModal">
            開始使用
          </button>
          <button class="btn-secondary text-lg px-8 py-3">了解更多</button>
        </div>
      </div>

      <!-- 功能特色 -->
      <div class="grid md:grid-cols-3 gap-8 mb-12">
        <div class="card text-center">
          <div class="text-3xl mb-4">🔍</div>
          <h3 class="text-lg font-semibold mb-2">智能搜尋增強</h3>
          <p class="text-gray-600">自動推薦相關的已收藏內容</p>
        </div>
        <div class="card text-center">
          <div class="text-3xl mb-4">🧠</div>
          <h3 class="text-lg font-semibold mb-2">語義分析</h3>
          <p class="text-gray-600">提取關鍵字，理解內容本質</p>
        </div>
        <div class="card text-center">
          <div class="text-3xl mb-4">⚡</div>
          <h3 class="text-lg font-semibold mb-2">一鍵收藏</h3>
          <p class="text-gray-600">讓收藏變得簡單快速</p>
        </div>
      </div>

      <!-- 統計資訊 -->
      <div class="card">
        <h3 class="text-lg font-semibold mb-4">快速統計</h3>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
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
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useBookmarkStore } from '@/stores/bookmark'
import { storeToRefs } from 'pinia'
import AddNewBookmarkModal from '@/components/AddNewBookmarkModal.vue'
import TheHeader from '@/components/base/TheHeader.vue'

const bookmarkStore = useBookmarkStore()
const { bookmarkCount } = storeToRefs(bookmarkStore)

const isModalOpen = ref(false)

const openModal = () => {
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
}
</script>
