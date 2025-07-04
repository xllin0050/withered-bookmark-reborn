<template>
  <Modal :show="!!bookmark" @close="$emit('close')">
    <template #header>
      <div class="flex items-center justify-between">
        <h3 class="text-xl font-bold text-gray-800">更新書籤</h3>
        <button
          @click="$emit('close')"
          class="text-2xl font-bold text-gray-500 hover:text-gray-800"
          :disabled="loading"
        >
          &times;
        </button>
      </div>
    </template>

    <template #default>
      <form @submit.prevent="onUpdate">
        <div class="mb-4">
          <label class="mb-2 block text-sm font-medium text-gray-700"
            >標題</label
          >
          <input v-model="formData.title" required class="input-field" />
        </div>
        <div class="mb-6">
          <label class="mb-2 block text-sm font-medium text-gray-700"
            >描述</label
          >
          <textarea
            v-model="formData.description"
            class="input-field"
            rows="3"
          ></textarea>
        </div>

        <div v-if="error" class="mb-4 text-sm text-red-600">{{ error }}</div>

        <div class="flex justify-end space-x-4">
          <button type="button" @click="$emit('close')" class="btn-secondary">
            取消
          </button>
          <button type="submit" class="btn-primary" :disabled="loading">
            {{ loading ? "更新中..." : "更新" }}
          </button>
        </div>
      </form>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { useBookmarkStore } from "@/stores/bookmark";
import type { Bookmark } from "@/types/bookmark";
import Modal from "@/components/base/Modal.vue";

const props = defineProps<{
  show: boolean;
  bookmark: Bookmark | null;
}>();
const emit = defineEmits(["close"]);

const bookmarkStore = useBookmarkStore();
const loading = ref(false);
const error = ref<string | null>(null);

const formData = ref({
  title: "",
  description: "",
});

watch(
  () => props.bookmark,
  (newBookmark) => {
    if (newBookmark) {
      formData.value = {
        title: newBookmark.title,
        description: newBookmark.description || "",
      };
      error.value = null;
    }
  },
  { immediate: true },
);

const onUpdate = async () => {
  if (!props.bookmark) return;
  loading.value = true;
  error.value = null;
  try {
    await bookmarkStore.updateBookmarkData(props.bookmark.id, {
      title: formData.value.title,
      description: formData.value.description,
    });
    emit("close");
  } catch (e: any) {
    error.value = e?.message || "更新失敗";
  } finally {
    loading.value = false;
  }
};
</script>
