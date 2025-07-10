<template>
  <div>
    <!-- 導航欄 -->
    <TheHeader>
      <template #actions>
        <RouterLink to="/search" class="btn-secondary"> 搜尋 </RouterLink>
        <RouterLink to="/" class="btn-primary"> 首頁 </RouterLink>
      </template>
    </TheHeader>
    <h1 class="text-center">Bookmarks</h1>
    <div class="mx-auto my-4 max-w-4xl text-center">
      <input
        type="file"
        ref="fileInput"
        @change="onFileChange"
        accept=".html,.json"
        class="mb-2"
      />
      <button
        @click="uploadFile"
        class="btn-primary"
        :disabled="!selectedFile || bookmarkStore.isLoading"
      >
        上傳書籤檔
      </button>
    </div>
    <div v-if="bookmarkStore.isLoading">Loading...</div>
    <div v-else-if="bookmarkStore.error">Error: {{ bookmarkStore.error }}</div>
    <div v-else>
      <DynamicScroller
        class="scroller mx-auto max-w-4xl"
        :items="bookmarkStore.bookmarks"
        :min-item-size="200"
        key-field="id"
        v-slot="{ item }"
      >
        <template v-slot="{ item, index, active }">
          <DynamicScrollerItem
            :item-size="200"
            :item-data="item"
            :active="true"
            :key-field="'id'"
          >
            <div class="bg-si border-er hover:border-yi h-45">
              <a :href="item.url" target="_blank" class="block p-4">
                <h3 class="text-lg font-semibold">{{ item.title }}</h3>
                <p class="mt-2 text-sm text-gray-600">{{ item.description }}</p>
                <div class="mt-2 flex justify-end space-x-2">
                  <button
                    class="btn-shape bg-er text-si"
                    @click.prevent="updateBookmark(item)"
                  >
                    Update
                  </button>
                  <button
                    class="btn-shape bg-amber-400 text-red-600"
                    @click.prevent="deleteBookmark(item.id)"
                  >
                    Delete
                  </button>
                </div>
              </a>
            </div>
          </DynamicScrollerItem>
        </template>
      </DynamicScroller>
    </div>
    <UpdateBookmarkModal
      :show="updateModalShow"
      :bookmark="selectedBookmark"
      @close="handleModalClose"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { useBookmarkStore } from "@/stores/bookmark";
import type { Bookmark } from "@/types/bookmark";
import UpdateBookmarkModal from "@/components/UpdateBookmarkModal.vue";
import TheHeader from "@/components/base/TheHeader.vue";

const bookmarkStore = useBookmarkStore();

const updateModalShow = ref(false);
const selectedBookmark = ref<Bookmark | null>(null);

const fileInput = ref<HTMLInputElement | null>(null);
const selectedFile = ref<File | null>(null);

const onFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0];
  } else {
    selectedFile.value = null;
  }
};

const uploadFile = async () => {
  if (selectedFile.value) {
    await bookmarkStore.uploadBookmarksFile(selectedFile.value);
    selectedFile.value = null;
    if (fileInput.value) {
      fileInput.value.value = "";
    }
  }
};

const deleteBookmark = (id: number) => {
  bookmarkStore.deleteBookmarkData(id);
};

const updateBookmark = (bookmark: Bookmark) => {
  selectedBookmark.value = bookmark;
  updateModalShow.value = true;
};

const handleModalClose = () => {
  updateModalShow.value = false;
  selectedBookmark.value = null;
};

onMounted(() => {
  if (bookmarkStore.bookmarks.length === 0) {
    bookmarkStore.fetchBookmarkData();
  }
});
</script>

<style scoped>
.scroller {
  height: calc(100vh - 200px); /* 給予一個明確的高度，否則無法顯示 */
}
</style>
