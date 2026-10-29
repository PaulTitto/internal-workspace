<!-- frontend/src/components/modals/ConfirmModal.vue -->
<!-- Modal Konfirmasi Kustom pengganti window.confirm browser (menghilangkan popup "localhost says") -->
<template>
  <div
    class="fixed inset-0 bg-[#080E2F]/65 backdrop-blur-xs flex items-center justify-center p-4 z-50 transition-opacity"
    @click.self="$emit('cancel')"
    @keydown.esc="$emit('cancel')"
  >
    <div
      class="bg-white rounded-xl w-full max-w-md p-6 space-y-4 shadow-2xl border border-[#DFE1E6] transform transition-all animate-in fade-in zoom-in-95 duration-150"
      role="dialog"
      aria-modal="true"
    >
      <div class="flex items-start gap-3">
        <!-- Icon Warning / Danger / Info -->
        <div
          class="w-10 h-10 rounded-full flex items-center justify-center shrink-0"
          :class="{
            'bg-[#FFEBE6] text-[#DE350B]': variant === 'danger',
            'bg-[#FFF0B3] text-[#172B4D]': variant === 'warning',
            'bg-[#EEF2FF] text-[#1226AA]': variant === 'info',
          }"
        >
          <svg
            v-if="variant === 'danger' || variant === 'warning'"
            width="22"
            height="22"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
            <line x1="12" y1="9" x2="12" y2="13" />
            <line x1="12" y1="17" x2="12.01" y2="17" />
          </svg>
          <svg
            v-else
            width="22"
            height="22"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="16" x2="12" y2="12" />
            <line x1="12" y1="8" x2="12.01" y2="8" />
          </svg>
        </div>

        <div class="min-w-0 flex-1">
          <h3 class="text-base font-bold text-[#172B4D] leading-tight">
            {{ title }}
          </h3>
          <p class="text-xs text-[#5E6C84] mt-1.5 leading-relaxed whitespace-pre-line">
            {{ message }}
          </p>
        </div>

        <button
          @click="$emit('cancel')"
          class="text-gray-400 hover:text-gray-600 p-1 rounded hover:bg-gray-100 transition-colors"
          title="Tutup"
        >
          ✕
        </button>
      </div>

      <!-- Action Buttons (Ya & No) -->
      <div class="flex items-center justify-end gap-2 pt-3 border-t border-[#EBECF0]">
        <button
          type="button"
          @click="$emit('cancel')"
          :disabled="busy"
          class="px-4 py-2 rounded text-xs font-semibold text-[#42526E] bg-[#FAFBFC] border border-[#DFE1E6] hover:bg-[#EBECF0] active:bg-[#DFE1E6] transition-colors disabled:opacity-50 cursor-pointer"
        >
          {{ cancelText }}
        </button>
        <button
          type="button"
          @click="$emit('confirm')"
          :disabled="busy"
          class="px-4 py-2 rounded text-xs font-semibold text-white shadow-xs transition-colors disabled:opacity-50 flex items-center gap-1.5 cursor-pointer"
          :class="{
            'bg-[#DE350B] hover:bg-[#BF2600] active:bg-[#9E2000]': variant === 'danger',
            'bg-[#FFAB00] text-[#172B4D] hover:bg-[#FF9900] active:bg-[#E68A00]': variant === 'warning',
            'bg-[#1226AA] hover:bg-[#0E1F8C] active:bg-[#0A1560]': variant === 'info',
          }"
        >
          <span v-if="busy" class="inline-block w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
          {{ busy ? 'Memproses...' : confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: 'Konfirmasi Tindakan' },
  message: { type: String, required: true },
  confirmText: { type: String, default: 'Ya, Hapus' },
  cancelText: { type: String, default: 'Tidak, Batal' },
  variant: { type: String, default: 'danger' }, // 'danger' | 'warning' | 'info'
  busy: { type: Boolean, default: false },
});

defineEmits(['confirm', 'cancel']);
</script>
