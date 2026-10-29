<!-- frontend/src/components/ToastNotification.vue -->
<!-- Toast alert modern pengganti window.alert browser (menghilangkan popup "localhost says") -->
<template>
  <div class="fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-sm pointer-events-none">
    <transition-group
      enter-active-class="transform transition ease-out duration-300"
      enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-4"
      enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="pointer-events-auto flex items-start gap-3 p-3.5 rounded-lg shadow-lg border text-xs font-medium backdrop-blur-xs"
        :class="{
          'bg-white border-[#36B37E] text-[#006644] shadow-emerald-900/10': toast.type === 'success',
          'bg-white border-[#DE350B] text-[#BF2600] shadow-rose-900/10': toast.type === 'error',
          'bg-white border-[#1226AA] text-[#1226AA] shadow-blue-900/10': toast.type === 'info',
        }"
      >
        <!-- Icon -->
        <div class="shrink-0 mt-0.5">
          <svg v-if="toast.type === 'success'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#36B37E" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
          <svg v-else-if="toast.type === 'error'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#DE350B" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="15" y1="9" x2="9" y2="15"></line>
            <line x1="9" y1="9" x2="15" y2="15"></line>
          </svg>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#1226AA" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="16" x2="12" y2="12"></line>
            <line x1="12" y1="8" x2="12.01" y2="8"></line>
          </svg>
        </div>

        <div class="flex-1 text-[#172B4D]">
          <div v-if="toast.title" class="font-bold mb-0.5">{{ toast.title }}</div>
          <div class="text-[#42526E] leading-relaxed">{{ toast.message }}</div>
        </div>

        <button
          @click="$emit('dismiss', toast.id)"
          class="shrink-0 text-gray-400 hover:text-gray-600 p-0.5 rounded transition-colors"
        >
          ✕
        </button>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
defineProps({
  toasts: { type: Array, default: () => [] },
});
defineEmits(['dismiss']);
</script>
