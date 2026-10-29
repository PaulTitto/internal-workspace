<!-- frontend/src/components/modals/JoinTeamModal.vue -->
<!-- Modal 'Join Team via Invite Code': masukkan kode INVITE-XXX-1234 dari Admin tim -->
<template>
  <div class="fixed inset-0 bg-[#080E2F]/65 backdrop-blur-xs flex items-center justify-center p-4 z-50" @click.self="$emit('close')">
    <div class="bg-white rounded-xl w-full max-w-md p-6 space-y-4 shadow-2xl border border-[#D0D7E2]">
      <div class="flex items-center justify-between border-b pb-3">
        <h2 class="text-base font-bold text-[#172B4D]">Join Team via Invite Code</h2>
        <button @click="$emit('close')" class="text-sm text-gray-500 hover:text-gray-800">✕</button>
      </div>

      <p class="text-xs text-[#6B778C]">
        Masukkan kode invite yang dibagikan Admin tim (contoh format:
        <span class="font-mono">INVITE-FIN-8899</span>). Anda akan bergabung dengan role yang
        ditentukan Admin (biasanya Developer).
      </p>

      <input
        v-model="inviteCode"
        placeholder="INVITE-FIN-8899"
        class="w-full text-sm font-mono uppercase border border-[#DFE1E6] rounded px-3 py-2 outline-none focus:border-[#1226AA]"
        @keyup.enter="submit"
      />

      <div v-if="error" class="text-xs text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">{{ error }}</div>

      <div class="flex justify-end space-x-2">
        <button @click="$emit('close')" class="px-4 py-2 rounded bg-gray-100 text-xs font-semibold text-[#42526E]">Cancel</button>
        <button
          @click="submit"
          :disabled="busy"
          class="px-4 py-2 rounded-lg bg-[#1226AA] hover:bg-[#0E1F8C] text-white text-xs font-semibold disabled:opacity-60 shadow-xs transition-colors"
        >
          {{ busy ? 'Joining...' : 'Join Team' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { JiraApiService } from '../../services/jiraApi';

const emit = defineEmits(['close', 'joined']);
const inviteCode = ref('');
const busy = ref(false);
const error = ref('');

async function submit() {
  error.value = '';
  if (!inviteCode.value.trim()) {
    error.value = 'Invite code wajib diisi.';
    return;
  }
  busy.value = true;
  try {
    const res = await JiraApiService.joinTeam(inviteCode.value.trim().toUpperCase());
    emit('joined', res.team);
  } catch (err) {
    error.value = err?.response?.data?.error || 'Gagal join tim. Periksa kode invite.';
  } finally {
    busy.value = false;
  }
}
</script>
