<!-- frontend/src/components/modals/CreateTeamModal.vue -->
<!-- Modal '+ Create New Team': Team Name, Key Prefix, Description -->
<template>
  <div class="fixed inset-0 bg-[#080E2F]/65 backdrop-blur-xs flex items-center justify-center p-4 z-50" @click.self="onClose">
    <div class="bg-white rounded-xl w-full max-w-md p-6 space-y-4 shadow-2xl border border-[#D0D7E2]">
      <div class="flex items-center justify-between border-b pb-3">
        <h2 class="text-base font-bold text-[#172B4D]">
          {{ created ? '🎉 Team Created!' : 'Create New Team' }}
        </h2>
        <button @click="onClose" class="text-sm text-gray-500 hover:text-gray-800">✕</button>
      </div>

      <!-- Success state — show invite code -->
      <template v-if="created">
        <p class="text-sm text-[#42526E]">
          Team <strong>{{ created.name }}</strong> has been created. Share the invite code below so teammates can join:
        </p>
        <div class="bg-[#F4F5F7] rounded-lg border border-[#DFE1E6] p-4 space-y-2">
          <p class="text-[11px] font-semibold text-[#6B778C] uppercase tracking-wide">Default Invite Code (7 days)</p>
          <div class="flex items-center gap-2">
            <code class="flex-1 font-mono text-sm font-bold text-[#1226AA] bg-white border border-[#DFE1E6] rounded px-3 py-2 select-all">
              {{ created.defaultInviteCode }}
            </code>
            <button
              @click="copyCode"
              class="shrink-0 text-xs font-semibold px-3 py-2 rounded-lg bg-[#1226AA] text-white hover:bg-[#0E1F8C]"
            >{{ copied ? '✓ Copied!' : 'Copy' }}</button>
          </div>
          <p class="text-[11px] text-[#6B778C]">Members can join via Tab "Team Members" → Join via Invite Code.</p>
        </div>
        <div class="flex justify-end">
          <button
            @click="onClose"
            class="px-4 py-2 rounded-lg bg-[#1226AA] text-white text-xs font-semibold hover:bg-[#0E1F8C]"
          >Continue →</button>
        </div>
      </template>

      <!-- Form state -->
      <template v-else>
        <div class="space-y-1">
          <label class="text-xs font-semibold text-[#42526E]">Team Name</label>
          <input
            v-model="form.name"
            placeholder="Finance Team"
            class="w-full text-sm border border-[#DFE1E6] rounded px-3 py-2 outline-none focus:border-[#1226AA]"
          />
        </div>

        <div class="space-y-1">
          <label class="text-xs font-semibold text-[#42526E]">Key Prefix</label>
          <input
            v-model="form.key"
            placeholder="FIN"
            maxlength="10"
            class="w-full text-sm font-mono uppercase border border-[#DFE1E6] rounded px-3 py-2 outline-none focus:border-[#1226AA]"
          />
          <p class="text-[11px] text-[#6B778C]">2–10 huruf kapital. Issue key akan jadi FIN-101, FIN-102, dst.</p>
        </div>

        <div class="space-y-1">
          <label class="text-xs font-semibold text-[#42526E]">Description</label>
          <textarea
            v-model="form.description"
            rows="3"
            placeholder="Apa fokus tim ini?"
            class="w-full text-sm border border-[#DFE1E6] rounded px-3 py-2 outline-none focus:border-[#1226AA]"
          ></textarea>
        </div>

        <div class="text-[11px] bg-[#F4F5F7] rounded p-3 text-[#42526E]">
          Setelah dibuat: Anda otomatis jadi <b>Admin</b> tim ini, dan
          <b>Sprint 1–4</b> dibuat otomatis (Sprint 1 langsung aktif).
        </div>

        <div v-if="error" class="text-xs text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">{{ error }}</div>

        <div class="flex justify-end space-x-2">
          <button @click="onClose" class="px-4 py-2 rounded bg-gray-100 text-xs font-semibold text-[#42526E]">Cancel</button>
          <button
            @click="submit"
            :disabled="busy"
            class="px-4 py-2 rounded-lg bg-[#1226AA] hover:bg-[#0E1F8C] text-white text-xs font-semibold disabled:opacity-60 shadow-xs transition-colors"
          >
            {{ busy ? 'Creating...' : 'Create Team' }}
          </button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { JiraApiService } from '../../services/jiraApi';

const emit = defineEmits(['close', 'created']);
const form = reactive({ name: '', key: '', description: '' });
const busy = ref(false);
const error = ref('');
const created = ref(null);
const copied = ref(false);

async function submit() {
  error.value = '';
  if (!form.name.trim() || !form.key.trim()) {
    error.value = 'Team Name dan Key Prefix wajib diisi.';
    return;
  }
  busy.value = true;
  try {
    const team = await JiraApiService.createTeam({ ...form, key: form.key.toUpperCase() });
    created.value = team; // show success + invite code
    emit('created', team);
  } catch (err) {
    error.value = err?.response?.data?.error || 'Gagal membuat tim.';
  } finally {
    busy.value = false;
  }
}

function onClose() {
  emit('close');
}

async function copyCode() {
  try {
    await navigator.clipboard.writeText(created.value.defaultInviteCode);
    copied.value = true;
    setTimeout(() => { copied.value = false; }, 2000);
  } catch {
    // fallback — silent
  }
}
</script>
