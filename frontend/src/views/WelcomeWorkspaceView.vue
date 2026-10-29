<!-- frontend/src/views/WelcomeWorkspaceView.vue -->
<!-- EMPTY STATE / Onboarding pertama kali: user SSO belum tergabung di team_memberships mana pun -->
<template>
  <div class="flex-1 min-h-screen bg-[#F4F5F7] flex items-center justify-center p-6">
    <div class="max-w-xl w-full bg-white rounded-xl border border-[#DFE1E6] shadow-lg p-10 text-center space-y-6">
      <!-- Ilustrasi workspace kosong -->
      <div class="mx-auto w-24 h-24 rounded-full bg-[#EEF2FF] border border-[#C7D2FE] flex items-center justify-center">
        <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#1226AA" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2" />
          <path d="M3 9h18" />
          <path d="M9 21V9" />
        </svg>
      </div>

      <div class="space-y-2">
        <h1 class="text-2xl font-bold text-[#0E1C68]">
          Selamat datang, {{ userName }}! 👋
        </h1>
        <p class="text-sm text-[#6B778C] leading-relaxed">
          Workspace SRKK Anda saat ini masih <span class="font-semibold text-[#0E1C68]">kosong</span> —
          Anda belum tergabung di tim mana pun. Buat tim baru untuk memulai sprint pertama,
          atau join ke tim yang sudah ada memakai kode invite dari Admin tim.
        </p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <button
          @click="$emit('create-team')"
          class="p-4 rounded-xl bg-[#1226AA] hover:bg-[#0E1F8C] text-white text-left space-y-1 shadow-md hover:shadow-lg transition-all"
        >
          <div class="text-sm font-bold">+ Create New Team</div>
          <div class="text-xs text-blue-200">Jadi Admin, dapat 4 sprint otomatis</div>
        </button>
        <button
          @click="$emit('join-team')"
          class="p-4 rounded-xl bg-white border border-[#DFE1E6] hover:border-[#1226AA] text-left space-y-1 hover:shadow-md transition-all"
        >
          <div class="text-sm font-bold text-[#172B4D]">Join Team via Invite Code</div>
          <div class="text-xs text-[#6B778C]">Masuk sebagai Developer/Member</div>
        </button>
      </div>

      <p class="text-xs text-[#97A0AF]">
      Login sebagai <span class="font-mono">{{ userEmail }}</span>
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({ user: { type: Object, default: null } });
defineEmits(['create-team', 'join-team']);

const userName = computed(() => props.user?.name?.split(' ')[0] || 'there');
const userEmail = computed(() => props.user?.email || '');
</script>
