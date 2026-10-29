<!-- frontend/src/views/TeamSelectorView.vue -->
<!-- Hub pemilihan tim: grid semua tim yang di-join user (dari team_memberships) -->
<template>
  <div class="flex-1 min-h-screen bg-[#F4F5F7] p-6 overflow-y-auto">
    <div class="max-w-5xl mx-auto space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-[#172B4D]">Teams Anda</h1>
          <p class="text-xs text-[#6B778C] mt-1">
            Login sebagai <span class="font-mono">{{ user?.email }}</span>
          </p>
        </div>
        <div class="flex space-x-2">
          <button
            @click="$emit('join-team')"
            class="text-xs font-semibold px-3 py-2 rounded-lg border border-[#DFE1E6] bg-white hover:border-[#1226AA] hover:text-[#1226AA] transition-colors"
          >
            Join via Invite Code
          </button>
          <button
            @click="$emit('create-team')"
            class="text-xs font-semibold px-3.5 py-2 rounded-lg bg-[#1226AA] hover:bg-[#0E1F8C] text-white shadow-xs transition-colors"
          >
            + Create New Team
          </button>
          <button
            @click="$emit('logout')"
            class="text-xs font-semibold px-3 py-2 rounded border border-[#DFE1E6] bg-white hover:bg-[#FFEBE6] hover:border-[#BF2600] text-[#BF2600]"
          >
            Logout
          </button>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div
          v-for="team in teams"
          :key="team.id"
          @click="$emit('select-team', team)"
          class="bg-white p-5 rounded-xl border border-[#DFE1E6] hover:border-[#1226AA] hover:shadow-md cursor-pointer transition-all"
        >
          <div class="flex items-center justify-between">
            <span class="text-xs font-mono font-bold px-2 py-0.5 rounded bg-[#EEF2FF] text-[#1226AA] border border-[#C7D2FE]">{{ team.key }}</span>
            <span class="text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full bg-[#EBECF0] text-[#42526E]">
              {{ roleOf(team) }}
            </span>
          </div>
          <h3 class="text-base font-bold text-[#172B4D] mt-2">{{ team.name }}</h3>
          <p class="text-xs text-[#6B778C] mt-1 line-clamp-2">{{ team.description || 'Tanpa deskripsi' }}</p>
          <div
            v-if="team.inviteCode"
            class="flex items-center justify-between mt-2 bg-[#F4F5F7] rounded px-2 py-1.5"
            @click.stop
          >
            <span class="font-mono text-[11px] font-bold text-[#172B4D]">{{ team.inviteCode }}</span>
            <button
              @click="copyInvite(team.inviteCode)"
              class="text-[10px] font-semibold px-2 py-0.5 rounded bg-white border border-[#DFE1E6] hover:bg-[#EEF2FF] hover:border-[#1226AA] text-[#1226AA] transition-colors"
            >{{ copied === team.inviteCode ? '✓' : 'Copy' }}</button>
          </div>
          <div class="flex items-center justify-between mt-3 pt-3 border-t border-[#EBECF0] text-[11px] text-[#5E6C84]">
            <div class="flex items-center space-x-2">
              <span>{{ team.memberCount }} members</span>
              <span>•</span>
              <span>{{ team.issueCount }} issues</span>
              <span v-if="team.activeSprint">• {{ team.activeSprint.name }}</span>
            </div>
            <div v-if="roleOf(team) === 'Admin'" class="flex items-center gap-1">
              <button
                @click.stop="$emit('edit-team', team)"
                class="text-[10px] font-semibold px-2 py-0.5 rounded border border-[#DFE1E6] bg-white hover:bg-[#F4F5F7] text-[#172B4D]"
              >✎ Edit</button>
              <button
                @click.stop="$emit('delete-team', team)"
                class="text-[10px] font-semibold px-2 py-0.5 rounded border border-[#FFAB00] bg-white hover:bg-[#FFFAE6] text-[#BF2600]"
              >🗑 Hapus</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({ user: Object, teams: { type: Array, default: () => [] } });
defineEmits(['select-team', 'create-team', 'join-team', 'edit-team', 'delete-team', 'logout']);

const copied = ref('');

function roleOf(team) {
  return team.yourRole || 'Member';
}

async function copyInvite(code) {
  try {
    await navigator.clipboard.writeText(code);
    copied.value = code;
    setTimeout(() => { copied.value = ''; }, 2000);
  } catch {
    /* clipboard diblokir — kode tetap terlihat */
  }
}
</script>
