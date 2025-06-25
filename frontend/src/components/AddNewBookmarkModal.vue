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
        >
          &times;
        </button>
      </div>
      <div class="p-6">
        <p class="text-gray-600 mb-2">在這裡新增你的書籤內容。</p>
        <form>
          <input
            type="text"
            placeholder="Title"
            v-model="newBookmark.title"
            class="input-field"
          />
          <input
            type="text"
            placeholder="URL"
            v-model="newBookmark.url"
            class="input-field"
          />
          <textarea
            placeholder="Description"
            v-model="newBookmark.description"
            class="input-field"
          ></textarea>
        </form>
        <div v-if="errorMessage" class="text-red-500 mb-2">
          {{ errorMessage }}
        </div>
      </div>
      <div class="p-4 bg-gray-50 rounded-b-lg flex justify-end space-x-3">
        <button @click="closeModal" class="btn-secondary">取消</button>
        <button @click="saveBookmark" class="btn-primary">儲存</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useBookmarkStore } from '@/stores/bookmark';

defineProps({
  show: {
    type: Boolean,
    required: true,
  },
})

const bookmarkStore = useBookmarkStore()

const emit = defineEmits(['close'])

const newBookmark = ref({
  title: '',
  url: '',
  description: '',
})

const errorMessage=ref<string | null>(null)

const closeModal = () => {
  errorMessage.value = null
  emit('close')
}

const saveBookmark = async () => {
  errorMessage.value = null

if (!newBookmark.value.url.trim()) {
  errorMessage.value = 'URL field cannot be empty.'
  return
}

try {
  await bookmarkStore.createBookmarkData(newBookmark.value)
  closeModal()
} catch (error: any) {
  if (error.response && error.response.status === 422 && error.response.data.detail) {
      const firstError = error.response.data.detail[0]
      errorMessage.value = `Error: ${firstError.msg}`
    } else {
      errorMessage.value = 'Could not save the bookmark. Please try again later.'
    }
}
}
</script>
<style scoped>
form input,
textarea {
  margin-bottom: 1em;
}

</style>
