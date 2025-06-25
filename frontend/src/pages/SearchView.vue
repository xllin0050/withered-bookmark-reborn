<template>
  <div>
    <!-- 導航欄 -->
    <nav class="bg-si shadow-sm border-b">
        <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
            <div class="flex items-center">
                <h1 class="text-xl font-bold text-gray-900">枯枝逢生</h1>
            </div>
            <div class="flex items-center space-x-4">
                <RouterLink to="/search" class="btn-secondary"> 搜尋 </RouterLink>
                <RouterLink to="/" class="btn-primary">
                首頁
                </RouterLink>
            </div>
            </div>
        </div>
    </nav>
    <h1>Search</h1>
    <div class="max-w-4xl mx-auto">
        <input type="text" placeholder="Search..." v-model="searchQuery" />
    </div>
  </div>
</template>