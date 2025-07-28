<template>
  <div class="flex min-h-screen flex-col items-center">
    <!-- 導航欄 -->
    <TheHeader>
      <template #actions>
        <RouterLink to="/bookmarks" class="btn-primary"> 我的書籤 </RouterLink>
      </template>
    </TheHeader>

    <!-- 主要內容 -->
    <main class="flex max-w-4xl flex-grow flex-col px-4 py-12 sm:px-6 lg:px-8">
      <!-- Hero Section -->
      <div class="mb-12 text-center">
        <h2 class="py-8 text-2xl font-bold sm:text-4xl">
          <span>讓</span><span>沉</span><span>睡</span><span>的</span
          ><span>書</span><span>籤</span><br class="block sm:hidden" /><span
            >重</span
          ><span>新</span><span>發</span><span>揮</span><span>價</span
          ><span>值</span>
        </h2>
        <p class="mb-8 text-base text-gray-600">
          在你搜尋時自動推薦相關的已收藏內容，<br
            class="block sm:hidden"
          />智能書籤助手讓知識重新流動
        </p>
      </div>

      <!-- 功能特色 -->
      <div class="introduce-card mb-12 grid gap-8 md:grid-cols-3">
        <div class="card text-center">
          <div class="emoji mb-4 text-3xl">🔍</div>
          <h3 class="mb-2 text-lg font-semibold">智能搜尋增強</h3>
          <p class="text-sm text-gray-600">自動推薦相關的已收藏內容</p>
        </div>
        <div class="card text-center">
          <div class="emoji mb-4 text-3xl">🧠</div>
          <h3 class="mb-2 text-lg font-semibold">語義分析</h3>
          <p class="text-sm text-gray-600">提取關鍵字，理解內容本質</p>
        </div>
        <div class="card text-center">
          <div class="emoji mb-4 text-3xl">⚡</div>
          <h3 class="mb-2 text-lg font-semibold">一鍵收藏</h3>
          <p class="text-sm text-gray-600">讓收藏變得簡單快速</p>
        </div>
      </div>

      <!-- 統計資訊 -->
      <div class="analyze-card card mb-12">
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

      <!-- 操作按鈕 -->
      <div class="flex items-center justify-center gap-4">
        <button
          v-if="!selectedFile"
          class="bg-viridian-green-500 rounded-lg px-4 py-2 font-medium text-white transition-colors hover:bg-yellow-400 hover:text-gray-500"
          @click="openModal"
        >
          新增書籤
        </button>
        <div class="flex flex-col items-center sm:flex-row">
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
              class="block btn-shape bg-viridian-green-500 cursor-pointer text-white hover:bg-yellow-400 hover:text-gray-500"
            >
              匯入書籤
            </label>
            <span v-if="selectedFile" class="px-4 text-sm">{{
              selectedFile.name
            }}</span>
          </div>
          <button
            v-if="selectedFile"
            class="btn-shape mt-4 bg-amber-400 text-white sm:mt-0"
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
import { animate, createSpring } from 'animejs'

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

function CardAnimation() {
  animate('.card', {
    translateY: {
      from: 16,
      duration: 500,
      delay: (_, i) => i * 100
    }
  })
}

function EmojiAnimation() {
  animate('.emoji', {
    translateY: [
      { to: 8, ease: 'inOut(3)', duration: 200, delay: (_, i) => i * 300 },
      { to: 0, ease: createSpring({ stiffness: 300 }) }
    ],
    loop: true,
    loopDelay: 700
  })
}

function TitleAnimation() {
  animate('h2 span', {
    rotate: {
      from: '-1turn'
    },
    delay: (_, i) => i * 50,
    ease: 'inOutCirc',
    loopDelay: 250
  })
}

onMounted(() => {
  EmojiAnimation()
  TitleAnimation()
  CardAnimation()
})
</script>
<style scoped>
h2 span {
  display: inline-block;
  padding: 0 0.25rem;
}
</style>
