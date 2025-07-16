<template>
  <Transition name="modal">
    <div
      v-if="show"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      @click.self="$emit('close')"
    >
      <div
        class="modal-content flex w-full max-w-lg flex-col rounded-lg bg-white shadow-xl"
      >
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
  </Transition>
</template>

<script setup lang="ts">
defineProps<{
  show: boolean
}>()

defineEmits(['close'])
</script>
<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.5s ease;
}

.modal-enter-active .modal-content,
.modal-leave-active .modal-content {
  transition: all 0.5s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-content,
.modal-leave-to .modal-content {
  opacity: 0;
  transform: translateY(-20px);
}
</style>
