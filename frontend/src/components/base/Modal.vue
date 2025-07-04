<template>
  <div
    v-if="show"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
    @click.self="$emit('close')"
  >
    <div class="flex w-full max-w-lg flex-col rounded-lg bg-white shadow-xl">
      <!-- Header Slot -->
      <div v-if="$slots.header" class="border-b p-4">
        <slot name="header"></slot>
      </div>

      <!-- Body/Default Slot -->
      <div class="p-6">
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  show: boolean;
}>();

defineEmits(["close"]);
</script>
