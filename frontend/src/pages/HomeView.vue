<template>
  <div class="flex min-h-screen flex-col items-center">
    <!-- 導航欄 -->
    <TheHeader>
      <template #actions>
        <RouterLink to="/search" class="btn-secondary"> 搜尋 </RouterLink>
        <RouterLink to="/bookmarks" class="btn-primary"> 我的書籤 </RouterLink>
      </template>
    </TheHeader>

    <!-- 主要內容 -->
    <main class="flex max-w-4xl flex-grow flex-col px-4 py-12 sm:px-6 lg:px-8">
      <!-- Hero Section -->
      <div class="mb-12 text-center">
        <h2 class="mb-8 text-2xl font-bold sm:text-4xl">
          讓沉睡的書籤重新發揮價值
        </h2>
        <p class="mb-8 text-base text-gray-600">
          在你搜尋時自動推薦相關的已收藏內容，<br />智能書籤助手讓知識重新流動
        </p>
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
      <div class="card mb-12">
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
      <div class="flex justify-center gap-4">
        <button
          v-if="!selectedFile"
          class="bg-viridian-green-500 rounded-lg px-4 py-2 font-medium text-white transition-colors hover:bg-yellow-400 hover:text-gray-500"
          @click="openModal"
        >
          新增書籤
        </button>
        <div class="flex flex-col sm:flex-row items-center">
          <div class="file-upload">
            <input
              type="file"
              ref="fileInput"
              accept=".html,.json"
              class="hidden"
              id="customFileInput"
              @change="onFileChange"
            />
            <label
              for="customFileInput"
              class="btn-shape bg-viridian-green-500 text-white cursor-pointer"
            >
              匯入書籤
            </label>
            <span v-if="selectedFile" class="text-sm px-4">{{
              selectedFile.name
            }}</span>
          </div>
          <button
            v-if="selectedFile"
            class="btn-shape bg-amber-400 text-white mt-4 sm:mt-0"
            @click="uploadFile"
          >
            開始上傳
          </button>
        </div>
      </div>
    </main>
    <AddNewBookmarkModal :show="isModalOpen" @close="closeModal" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useBookmarkStore } from '@/stores/bookmark'
import { storeToRefs } from 'pinia'
import AddNewBookmarkModal from '@/components/AddNewBookmarkModal.vue'
import TheHeader from '@/components/base/TheHeader.vue'
import { animate, utils, createSpring } from 'animejs'

const bookmarkStore = useBookmarkStore()
const { bookmarkCount } = storeToRefs(bookmarkStore)

const isModalOpen = ref(false)

const openModal = () => {
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
}

const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)

const onFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0]
  } else {
    selectedFile.value = null
  }
}

const uploadFile = async () => {
  if (selectedFile.value) {
    await bookmarkStore.uploadBookmarksFile(selectedFile.value)
    selectedFile.value = null
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}
function TitleAnimation() {
  animate('h2', {
    scale: [
      { to: 1.1, ease: 'inOut(3)', duration: 200 },
      { to: 1, ease: createSpring({ stiffness: 300 }) }
    ],
    loop: true,
    loopDelay: 250
  })
}

onMounted(() => {
  TitleAnimation()
})
</script>
