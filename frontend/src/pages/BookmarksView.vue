<template>
  <div>
    <!-- 導航欄 -->
    <TheHeader>
      <template #actions>
        <RouterLink to="/search" class="btn-secondary"> 搜尋 </RouterLink>
        <RouterLink to="/" class="btn-primary"> 首頁 </RouterLink>
      </template>
    </TheHeader>
    <h1 class="pt-4 text-center">Bookmarks</h1>
    <div class="mx-auto my-4 max-w-4xl text-center">
   
    </div>
    <div v-if="bookmarkStore.isLoading">Loading...</div>
    <div v-else-if="bookmarkStore.error">Error: {{ bookmarkStore.error }}</div>
    <div v-else>
      <RecycleScroller
        ref="scroller"
        class="scroller"
        :items="bookmarkStore.bookmarks"
        :item-size="100"
        key-field="id"
        :buffer="200"
      >
        <template #default="props">
          <div class="bg-si border-er hover:border-yi group h-24">
            <a
              :href="props.item.url"
              target="_blank"
              class="relative block h-full w-full p-4"
            >
              <h3 class="text-lg font-semibold">{{ props.item.title }}</h3>
              <p class="mt-2 text-sm text-gray-600">
                {{ props.item.description }}
              </p>
              <div
                class="absolute top-1/2 right-0 hidden -translate-y-1/2 p-2 group-hover:block"
              >
                <button
                  class="btn-shape bg-er text-si mr-2"
                  @click.prevent="updateBookmark(props.item)"
                >
                  Update
                </button>
                <button
                  class="btn-shape bg-amber-400 text-red-600"
                  @click.prevent="deleteBookmark(props.item.id)"
                >
                  Delete
                </button>
              </div>
            </a>
          </div>
        </template>
      </RecycleScroller>
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
  width: 100%;
  height: calc(100vh - 300px);
}
</style>
