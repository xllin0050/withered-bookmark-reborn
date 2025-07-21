<template>
  <div>
    <form
      class="flex w-full justify-center gap-3"
      @submit.prevent="$emit('search')"
    >
      <input
        :value="modelValue"
        @input="
          $emit('update:modelValue', ($event.target as HTMLInputElement).value)
        "
        type="text"
        class="flex-1 rounded-lg border border-slate-300 bg-slate-50 px-4 py-3 text-base transition focus:border-amber-500 focus:ring-2 focus:ring-indigo-200 focus:outline-none"
        placeholder="請輸入關鍵字..."
        :aria-label="'搜尋書籤'"
      />
      <button
        type="submit"
        :disabled="isLoading"
        class="from-viridian-green-300 to-viridian-green-500 h-12 rounded-lg bg-gradient-to-r px-6 font-semibold text-white shadow transition hover:from-amber-300 hover:to-amber-500 focus:ring-2 focus:ring-indigo-300 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50 disabled:shadow-none"
        :aria-label="isLoading ? '搜尋中' : '開始搜尋'"
      >
        <span v-if="!isLoading">搜尋</span>
        <span v-else>搜尋中...</span>
      </button>
    </form>

    <div class="mt-4">
      <button
        v-if="showClearButton"
        @click="$emit('clear')"
        class="rounded-lg bg-slate-500 px-4 py-2 text-white transition hover:bg-slate-600 focus:ring-2 focus:ring-slate-300 focus:outline-none"
        aria-label="清除搜尋結果"
      >
        清除搜尋，顯示全部書籤
      </button>
      <p v-else class="mt-2 text-slate-600">
        已經儲存 {{ totalBookmarks }} 個書籤
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  modelValue: string
  isLoading: boolean
  showClearButton: boolean
  totalBookmarks?: number
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'search'): void
  (e: 'clear'): void
}

defineProps<Props>()
defineEmits<Emits>()
</script>
