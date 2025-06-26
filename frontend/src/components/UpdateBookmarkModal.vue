<!-- EditBookmarkModal.vue -->
<template>
    <div v-if="show && bookmark" class="modal">
      <form @submit.prevent="updateBookmark">
        <input v-model="formData.title" required />
        <textarea v-model="formData.description"></textarea>
        <button type="submit">更新</button>
      </form>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, watch } from 'vue'
  import { useBookmarkStore } from '@/stores/bookmark'
import type { Bookmark } from '@/types/bookmark';
  
  const props = defineProps<{
    show: boolean
    bookmark: Bookmark | null
  }>()
  
  const formData = ref({
    title: '',
    description: ''
  })
  
  watch(() => props.bookmark, (newBookmark : Bookmark | null) => {
    if (newBookmark) {
      formData.value = {
        title: newBookmark.title,
        description: newBookmark.description||''
      }
    }
  })
  
  const updateBookmark = async () => {
    // 調用 store 的更新方法
  }
  </script>