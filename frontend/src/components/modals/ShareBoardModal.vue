<!-- frontend/src/components/modals/ShareBoardModal.vue -->
<!-- Modal Share Board: link publik baca-saja tetap/langgeng (tidak berubah-ubah) dan langsung tersedia saat modal dibuka. -->
<template>
  <div class="fixed inset-0 bg-[#080E2F]/65 backdrop-blur-xs flex items-center justify-center p-4 z-50" @click.self="$emit('close')">
    <div class="bg-white rounded-xl shadow-2xl w-full max-w-md p-6 space-y-5 animate-in fade-in zoom-in-95 duration-150 border border-[#D0D7E2]">
      <!-- Header -->
      <div class="flex items-center justify-between border-b pb-3 border-[#EBECF0]">
        <h2 class="text-base font-bold text-[#172B4D] flex items-center gap-2">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1226AA" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="18" cy="5" r="3"/>
            <circle cx="6" cy="12" r="3"/>
            <circle cx="18" cy="19" r="3"/>
            <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/>
            <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>
          </svg>
          Share Board (Read-Only Link)
        </h2>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 text-lg leading-none p-1 rounded hover:bg-gray-100 transition-colors">
          ✕
        </button>
      </div>

      <p class="text-xs text-[#5E6C84] leading-relaxed">
        Link permanen (baca-saja) untuk membagikan papan tim ini ke siapa saja tanpa perlu login.
        <strong class="text-[#172B4D]">Link ini tetap dan tidak akan berubah-ubah.</strong>
      </p>

      <!-- Loading State -->
      <div v-if="loading" class="flex flex-col items-center justify-center py-6 space-y-2">
        <div class="w-6 h-6 border-2 border-[#1226AA] border-t-transparent rounded-full animate-spin"></div>
        <p class="text-xs text-[#6B778C]">Memuat link papan tim...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 text-xs rounded-lg p-3 space-y-2">
        <p>{{ error }}</p>
        <button
          @click="loadShareLink(false)"
          class="text-xs font-semibold underline text-red-800 hover:text-red-950"
        >
          Coba Muat Ulang
        </button>
      </div>

      <!-- Share URL Display (Langsung Muncul Otomatis) -->
      <div v-else class="space-y-3">
        <div class="space-y-1.5">
          <label class="text-[11px] font-bold uppercase tracking-wide text-[#6B778C]">
            Public Share Link
          </label>
          <div class="flex items-center gap-2 p-2 bg-[#F4F5F7] rounded-lg border border-[#DFE1E6] focus-within:border-[#1226AA] transition-colors">
            <input
              ref="inputRef"
              :value="shareUrl"
              readonly
              @click="$event.target.select()"
              class="flex-1 bg-transparent text-xs font-mono text-[#172B4D] outline-none select-all px-1.5 truncate"
            />
            <button
              @click="copyUrl"
              class="shrink-0 text-xs font-semibold px-3.5 py-1.5 rounded-lg transition-all flex items-center gap-1 shadow-xs cursor-pointer"
              :class="copied
                ? 'bg-[#36B37E] text-white'
                : 'bg-[#1226AA] text-white hover:bg-[#0E1F8C] active:bg-[#0A1560]'"
            >
              <svg v-if="copied" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
              <svg v-else width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
              {{ copied ? 'Tersalin!' : 'Copy Link' }}
            </button>
          </div>
        </div>

        <div class="flex items-center justify-between text-[11px] text-[#6B778C] pt-1">
          <span class="flex items-center gap-1 text-[#006644] font-medium">
            <span class="w-2 h-2 rounded-full bg-[#36B37E] inline-block"></span>
            Link Aktif & Tetap
          </span>
          <a
            :href="shareUrl"
            target="_blank"
            class="text-[#1226AA] hover:underline font-semibold flex items-center gap-1"
          >
            Buka di Tab Baru ↗
          </a>
        </div>

        <!-- Reset Confirmation (Tanpa window.confirm) -->
        <div v-if="!showRegenConfirm" class="pt-3 border-t border-[#EBECF0] flex items-center justify-between">
          <button
            @click="showRegenConfirm = true"
            :disabled="loading"
            class="text-[11px] text-[#6B778C] hover:text-[#DE350B] hover:underline transition-colors cursor-pointer"
          >
            ↻ Reset & Buat Link Baru
          </button>
          <span class="text-[10px] text-[#97A0AF]">
            Berlaku 1 tahun
          </span>
        </div>
        <div v-else class="pt-3 border-t border-[#EBECF0] bg-[#FFF0B3]/35 p-3 rounded-lg border border-[#FFE380] space-y-2">
          <p class="text-xs text-[#172B4D] font-medium leading-tight">
            Link lama tidak akan bisa diakses lagi jika di-reset. Buat link baru?
          </p>
          <div class="flex items-center gap-2 justify-end">
            <button
              @click="showRegenConfirm = false"
              class="px-2.5 py-1 text-xs font-semibold rounded bg-white border border-[#DFE1E6] hover:bg-[#F4F5F7] text-[#42526E]"
            >
              Tidak, Batal
            </button>
            <button
              @click="showRegenConfirm = false; loadShareLink(true)"
              class="px-2.5 py-1 text-xs font-semibold rounded bg-[#DE350B] text-white hover:bg-[#BF2600]"
            >
              Ya, Reset Link
            </button>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="pt-2 border-t border-[#EBECF0] flex justify-end">
        <button
          @click="$emit('close')"
          class="text-xs font-semibold px-4 py-2 rounded bg-gray-100 hover:bg-gray-200 text-[#42526E] transition-colors cursor-pointer"
        >
          Selesai
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { JiraApiService } from '../../services/jiraApi';

const props = defineProps({
  teamId: { type: Number, required: true },
});
defineEmits(['close']);

const loading = ref(true);
const error = ref('');
const shareUrl = ref('');
const expiresAt = ref('');
const copied = ref(false);
const showRegenConfirm = ref(false);
const inputRef = ref(null);

onMounted(() => {
  loadShareLink(false);
});

async function loadShareLink(regenerate = false) {
  loading.value = true;
  error.value = '';
  copied.value = false;
  try {
    const res = await JiraApiService.fetchTeamShareToken(props.teamId, regenerate);
    const origin = window.location.origin;
    shareUrl.value = `${origin}/share/${res.shareToken}`;
    expiresAt.value = res.expiresAt;
  } catch (err) {
    error.value = err?.response?.data?.error || 'Gagal memuat share link';
  } finally {
    loading.value = false;
  }
}

async function copyUrl() {
  if (!shareUrl.value) return;
  try {
    await navigator.clipboard.writeText(shareUrl.value);
    copied.value = true;
    setTimeout(() => { copied.value = false; }, 2500);
  } catch {
    if (inputRef.value) {
      inputRef.value.select();
      document.execCommand('copy');
      copied.value = true;
      setTimeout(() => { copied.value = false; }, 2500);
    }
  }
}
</script>
