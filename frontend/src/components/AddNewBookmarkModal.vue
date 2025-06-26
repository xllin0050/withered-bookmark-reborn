<template>
  <div
    v-if="show"
    class="fixed inset-0 bg-black/70 z-50 flex justify-center items-center p-4"
    @click.self="closeModal"
  >
    <div class="bg-white rounded-lg shadow-xl w-full max-w-md">
      <div class="flex justify-between items-center p-4 border-b">
           <h3 class="text-xl font-bold text-gray-800">新增書籤</h3>
        <button
          @click="closeModal"
          class="text-gray-500 hover:text-gray-800 text-2xl font-bold"
          :disabled="isSubmitting"
        >
          &times;
        </button>
      </div>
      
      <form @submit.prevent="saveBookmark" class="p-6">
        <!-- URL 輸入 (必填) -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            網址 <span class="text-red-500">*</span>
          </label>
          <input
            type="url"
            v-model="formData.url"
            @blur="fetchUrlMetadata"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="https://example.com"
            :disabled="isSubmitting"
            required
          />
          <p v-if="errors.url" class="mt-1 text-sm text-red-600">{{ errors.url }}</p>
        </div>

        <!-- 標題輸入 (必填) -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            標題 <span class="text-red-500">*</span>
          </label>
          <input
            type="text"
            v-model="formData.title"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="書籤標題"
            :disabled="isSubmitting"
            required
          />
          <p v-if="errors.title" class="mt-1 text-sm text-red-600">{{ errors.title }}</p>
        </div>

        <!-- 描述輸入 (選填) -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            描述
          </label>
          <textarea
            v-model="formData.description"
            rows="3"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="簡短描述這個書籤..."
            :disabled="isSubmitting"
          ></textarea>
        </div>

        <!-- 載入狀態提示 -->
        <div v-if="isLoading" class="mb-4 p-3 bg-blue-50 rounded-md">
          <p class="text-sm text-blue-700 flex items-center">
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            正在獲取網頁資訊...
          </p>
        </div>

        <!-- 錯誤提示 -->
        <div v-if="errorMessage" class="mb-4 p-3 bg-red-50 rounded-md">
          <p class="text-sm text-red-700">{{ errorMessage }}</p>
        </div>

        <!-- 按鈕 -->
        <div class="flex justify-end space-x-3 pt-4 border-t">
          <button 
            type="button"
            @click="closeModal" 
            class="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
            :disabled="isSubmitting"
          >
            取消
          </button>
          <button 
            type="submit"
            :disabled="isSubmitting || !isFormValid"
            class="px-4 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center"
          >
            <svg v-if="isSubmitting" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ isSubmitting ? '儲存中...' : '儲存' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useBookmarkStore } from '@/stores/bookmark'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'saved'): void
}>()

const bookmarkStore = useBookmarkStore()

// 表單資料
const formData = ref({
  url: '',
  title: '',
  description: ''
})

// 狀態管理
const isLoading = ref(false)
const isSubmitting = ref(false)
const errorMessage = ref('')
const errors = ref({
  url: '',
  title: ''
})

// 表單驗證
const isFormValid = computed(() => {
  return formData.value.url && formData.value.title && !errors.value.url && !errors.value.title
})

// 驗證 URL
const validateUrl = (url: string): boolean => {
  if (!url) return false
  try {
    new URL(url.startsWith('http') ? url : `https://${url}`)
    return true
  } catch {
    return false
  }
}

// 當輸入 URL 後自動獲取網頁資訊
const fetchUrlMetadata = async () => {
  if (!formData.value.url) return
  
  const url = formData.value.url.trim()
  
  if (!validateUrl(url)) {
    errors.value.url = '請輸入有效的網址'
    return
  }
  
  errors.value.url = ''
  
  // 如果已經有標題，就不自動獲取
  if (formData.value.title) return
  
  isLoading.value = true
  
  try {
    // 從 URL 提取域名作為預設標題
    const urlObj = new URL(url.startsWith('http') ? url : `https://${url}`)
    formData.value.title = urlObj.hostname.replace(/^www\./, '')
    
    // 這裡可以添加獲取網頁標題和描述的邏輯
    // 例如：
    // const metadata = await bookmarkApi.getUrlMetadata(url)
    // if (metadata.title) formData.value.title = metadata.title
    // if (metadata.description) formData.value.description = metadata.description
  } catch (error) {
    console.error('Failed to fetch metadata:', error)
  } finally {
    isLoading.value = false
  }
}

// 儲存書籤
const saveBookmark = async () => {
  if (!isFormValid.value) return
  
  isSubmitting.value = true
  errorMessage.value = ''
  
  try {
    // 確保 URL 有正確的協議前綴
    let url = formData.value.url.trim()
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'https://' + url
    }
    
    await bookmarkStore.createBookmarkData({
      url,
      title: formData.value.title.trim(),
      description: formData.value.description?.trim() || ''
    })
    
    emit('saved')
    isSubmitting.value = false
    closeModal()
  } catch (error: any) {
    console.error('Save bookmark error:', error)
    if (error.response?.data?.detail) {
      if (Array.isArray(error.response.data.detail)) {
        errorMessage.value = error.response.data.detail.map((d: any) => d.msg).join('\n')
      } else {
        errorMessage.value = error.response.data.detail
      }
    } else {
      errorMessage.value = error.message || '儲存失敗，請稍後再試'
    }
  } finally {
    isSubmitting.value = false
  }
}

// 關閉彈窗
const closeModal = () => {
  if (isSubmitting.value) return
  
  // 重置表單
  formData.value = {
    url: '',
    title: '',
    description: ''
  }
  errors.value = {
    url: '',
    title: ''
  }
  errorMessage.value = ''
  
  emit('close')
}

// 監聽彈窗關閉
watch(() => props.show, (newVal) => {
  if (!newVal) {
    closeModal()
  }
})
</script>

<style scoped>
/* 移除預設的 input 和 textarea 樣式 */
input, textarea {
  /* @apply w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors; */
}

textarea {
  min-height: 80px;
  resize: vertical;
}

/* 禁用狀態的樣式 */
button:disabled {
  /* @apply opacity-50 cursor-not-allowed; */
}

/* 表單錯誤狀態 */
input:invalid, textarea:invalid {
  /* @apply border-red-500; */
}

/* 動畫效果 */
.fade-enter-active, .fade-leave-active {
  /* transition: opacity 0.2s ease; */
}

.fade-enter-from, .fade-leave-to {
  /* opacity: 0; */
}
</style>
