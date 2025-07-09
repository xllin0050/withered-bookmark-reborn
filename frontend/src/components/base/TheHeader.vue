<template>
  <nav class="bg-si shadow-sm">
    <div class="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
      <div class="flex h-16 justify-between">
        <div class="flex items-center">
          <RouterLink to="/" class="text-2xl font-bold">枯枝逢生</RouterLink>
        </div>
        <div class="flex items-center space-x-4">
          <slot name="actions"></slot>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { RouterLink } from "vue-router";
</script>
