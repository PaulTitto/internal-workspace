<!-- frontend/src/components/LoadingScreen.vue -->
<template>
  <div class="flex-1 h-screen flex items-center justify-center bg-[#F4F5F7]">
    <div class="flex items-center space-x-3 text-[#6B778C]">
      <div class="w-5 h-5 border-2 border-[#1226AA] border-t-transparent rounded-full animate-spin"></div>
      <span class="text-sm">{{ label }}</span>
    </div>
  </div>
</template>

<script setup>
defineProps({ label: { type: String, default: 'Loading...' } });
</script>
