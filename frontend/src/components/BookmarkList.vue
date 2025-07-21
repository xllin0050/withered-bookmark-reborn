<template>
  <!-- 全部書籤 -->
  <div>
    <div v-if="isLoading">Loading...</div>
    <div v-else-if="error">Error: {{ error }}</div>
    <div v-else>
      <RecycleScroller
        ref="scroller"
        class="scroller"
        :items="bookmarks"
        :item-size="100"
        key-field="id"
        :buffer="200"
      >
        <template #default="props">
          <div class="bg-viridian-green-100 h-24 group overflow-hidden">
            <a
              :href="props.item.url"
              target="_blank"
              class="relative block h-full w-full p-4"
            >
              <h3 class="text-lg text-viridian-green-700 font-semibold">{{ props.item.title }}</h3>
              <p class="mt-2 text-sm text-gray-600">
                {{ props.item.description }}
              </p>
              <div
                class="absolute top-1/2 right-0 hidden -translate-y-1/2 p-2 group-hover:block"
              >
                <button
                  class="btn-shape bg-viridian-green-300 hover:bg-viridian-green-400 text-viridian-green-50 mr-2 shadow-xl"
                  @click.prevent="$emit('update', props.item)"
                >
                  Update
                </button>
                <button
                  class="btn-shape bg-amber-300 hover:bg-amber-400 text-viridian-green-50 shadow-xl"
                  @click.prevent="$emit('delete', props.item.id)"
                >
                  Delete
                </button>
              </div>
            </a>
          </div>
        </template>
      </RecycleScroller>
    </div>
  </div>
</template>
<script setup lang="ts">
import { RecycleScroller } from 'vue-virtual-scroller'
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css'
import type { Bookmark } from '@/types/bookmark'

interface Props {
  bookmarks: Bookmark[]
  isLoading: boolean
  error: string | null
}

interface Emits {
  (e: 'update', bookmark: Bookmark): void
  (e: 'delete', id: number): void
}

defineProps<Props>()
defineEmits<Emits>()
</script>

<style scoped>
.scroller {
  width: 100%;
  height: calc(100vh - 300px);
}
</style>
