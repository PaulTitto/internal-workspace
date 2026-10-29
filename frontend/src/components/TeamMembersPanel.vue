<!-- frontend/src/components/TeamMembersPanel.vue -->
<!-- Admin Panel: daftar Team Members + generate Invite Code (hanya Admin) -->
<template>
  <div class="flex-1 overflow-y-auto p-6 bg-[#F4F5F7]">
    <div class="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 class="text-xl font-bold text-[#172B4D]">Team Members — {{ team.name }}</h1>
        <p class="text-xs text-[#6B778C] mt-1">
          <span class="font-mono bg-[#EEF2FF] text-[#1226AA] border border-[#C7D2FE] px-2 py-0.5 rounded">{{ team.key }}</span>
          {{ members.length }} anggota
        </p>
      </div>

      <!-- Daftar anggota -->
      <div class="bg-white rounded-lg border border-[#DFE1E6] divide-y divide-[#EBECF0]">
        <div v-for="m in members" :key="m.id" class="flex items-center justify-between px-4 py-3">
          <div class="flex items-center space-x-3">
            <div class="w-8 h-8 rounded-full bg-[#1226AA] text-white flex items-center justify-center text-xs font-bold shadow-xs">
              {{ initials(m.user?.name) }}
            </div>
            <div>
              <div class="text-sm font-semibold text-[#172B4D]">{{ m.user?.name || m.userOid }}</div>
              <div class="text-xs text-[#6B778C] font-mono">{{ m.user?.email }}</div>
            </div>
          </div>
          <span
            class="text-[10px] font-bold uppercase px-2 py-1 rounded-full"
            :class="{
              'bg-[#EEF2FF] text-[#1226AA] border border-[#C7D2FE]': m.role === 'Admin',
              'bg-[#E3FCEF] text-[#006644]': m.role === 'Developer',
              'bg-[#EBECF0] text-[#42526E]': m.role === 'Viewer',
            }"
          >
            {{ m.role }}
          </span>
        </div>
      </div>

      <!-- Invite management: hanya Admin (case-insensitive) -->
      <div v-if="isAdmin" class="bg-white rounded-lg border border-[#DFE1E6] p-5 space-y-4">
        <h2 class="text-sm font-bold text-[#172B4D]">Invite Colleagues</h2>

        <!-- Kode invite utama: Copy + Regenerate -->
        <div v-if="primaryInvite" class="flex items-center justify-between bg-[#EEF2FF] border border-[#C7D2FE] rounded-lg px-4 py-3">
          <div>
            <div class="text-[10px] uppercase font-bold text-[#1226AA] tracking-wide">Kode Invite Tim</div>
            <div class="font-mono text-lg font-bold text-[#172B4D]">{{ primaryInvite.inviteCode }}</div>
            <div class="text-[11px] text-[#42526E]">
              role {{ primaryInvite.role }} • {{ primaryInvite.expired ? 'kedaluwarsa' : `berlaku s/d ${primaryInvite.expiresAt}` }}
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="copyCode(primaryInvite.inviteCode)"
              class="text-xs font-semibold px-3 py-1.5 rounded-lg bg-white border border-[#C7D2FE] hover:bg-[#F4F5F7] text-[#1226AA]"
            >{{ copied ? '✓ Tersalin' : 'Copy Code' }}</button>
            <button
              @click="generateInvite"
              :disabled="busy"
              class="text-xs font-semibold px-3 py-1.5 rounded-lg bg-[#1226AA] text-white hover:bg-[#0E1F8C] disabled:opacity-60 shadow-xs"
            >{{ busy ? '...' : 'Regenerate' }}</button>
          </div>
        </div>

        <div class="flex flex-wrap items-end gap-3">
          <div class="space-y-1">
            <label class="text-xs font-semibold text-[#42526E]">Role</label>
            <select v-model="inviteRole" class="text-sm border border-[#DFE1E6] rounded px-2 py-2">
              <option>Developer</option>
              <option>Viewer</option>
            </select>
          </div>
          <div class="space-y-1">
            <label class="text-xs font-semibold text-[#42526E]">Berlaku (hari)</label>
            <input v-model.number="inviteTtl" type="number" min="1" max="30"
              class="w-24 text-sm border border-[#DFE1E6] rounded px-2 py-2" />
          </div>
          <button
            @click="generateInvite"
            :disabled="busy"
            class="px-4 py-2 rounded border border-[#DFE1E6] hover:bg-[#F4F5F7] text-xs font-semibold disabled:opacity-60"
          >
            {{ busy ? 'Generating...' : '+ Generate Kode Tambahan' }}
          </button>
        </div>

        <div v-if="error" class="text-xs text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">{{ error }}</div>

        <!-- Kode invite aktif lainnya -->
        <div v-if="otherInvites.length" class="space-y-2">
          <div class="text-xs font-semibold text-[#42526E]">Kode invite aktif lainnya:</div>
          <div
            v-for="inv in otherInvites"
            :key="inv.id"
            class="flex items-center justify-between bg-[#F4F5F7] rounded px-3 py-2"
          >
            <div class="flex items-center space-x-3">
              <span class="font-mono text-sm font-bold text-[#172B4D]">{{ inv.inviteCode }}</span>
              <span class="text-[10px] uppercase font-semibold px-2 py-0.5 rounded-full bg-white text-[#42526E]">
                {{ inv.role }}
              </span>
            </div>
            <span class="text-[11px]" :class="inv.expired ? 'text-red-500' : 'text-[#6B778C]'">
              {{ inv.expired ? 'kedaluwarsa' : `berlaku s/d ${inv.expiresAt}` }}
            </span>
          </div>
        </div>
        <p v-if="!invites.length" class="text-xs text-[#6B778C]">Belum ada kode invite aktif — klik Regenerate di atas.</p>
      </div>

      <!-- Team Settings (Danger Zone / Edit): hanya Admin -->
      <div v-if="isAdmin" class="bg-white rounded-lg border border-[#DFE1E6] p-5 space-y-3">
        <h2 class="text-sm font-bold text-[#172B4D]">Team Settings & Danger Zone</h2>
        <p class="text-xs text-[#6B778C]">Kelola identitas tim atau hapus tim secara permanen beserta semua sprint dan issue di dalamnya.</p>
        <div class="flex items-center gap-2 pt-1 flex-wrap">
          <button
            @click="$emit('edit-team', team)"
            class="text-xs font-semibold px-3 py-1.5 rounded border border-[#DFE1E6] bg-white hover:bg-[#F4F5F7] text-[#172B4D] flex items-center gap-1 shadow-xs"
          >
            ✎ Edit Detail Tim
          </button>
          <button
            @click="$emit('delete-team', team)"
            class="text-xs font-semibold px-3 py-1.5 rounded border border-[#FFAB00] bg-white hover:bg-[#FFFAE6] text-[#BF2600] flex items-center gap-1 shadow-xs"
          >
            🗑 Hapus Tim Ini
          </button>
        </div>
      </div>

      <p v-else class="text-xs text-[#6B778C]">
        Hanya Admin tim yang dapat membuat kode invite atau mengelola tim.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { JiraApiService } from '../services/jiraApi';

const props = defineProps({
  team: { type: Object, required: true },
  members: { type: Array, default: () => [] },
  myRole: { type: String, default: 'Viewer' },
});
const emit = defineEmits(['invites-refreshed', 'edit-team', 'delete-team']);

// Bug fix: perbandingan role harus case-insensitive DAN reaktif (computed,
// bukan const yang dievaluasi sekali saat setup).
const isAdmin = computed(() => (props.myRole || '').toUpperCase() === 'ADMIN');
const invites = ref(props.team.invites || []);
const inviteRole = ref('Developer');
const inviteTtl = ref(7);
const busy = ref(false);
const error = ref('');
const copied = ref(false);

const activeInvites = computed(() => invites.value.filter((i) => !i.expired));
const primaryInvite = computed(() => activeInvites.value[0] || null);
const otherInvites = computed(() => activeInvites.value.slice(1));

onMounted(async () => {
  if (!isAdmin.value) return;
  try {
    invites.value = await JiraApiService.fetchTeamInvites(props.team.id);
  } catch (err) {
    console.error('Gagal memuat invite:', err);
  }
});

async function copyCode(code) {
  try {
    await navigator.clipboard.writeText(code);
    copied.value = true;
    setTimeout(() => { copied.value = false; }, 2000);
  } catch {
    /* clipboard diblokir — kode tetap terlihat */
  }
}

async function generateInvite() {
  error.value = '';
  busy.value = true;
  try {
    const invite = await JiraApiService.createInvite(props.team.id, {
      role: inviteRole.value,
      expiresInDays: inviteTtl.value,
    });
    invites.value = [invite, ...invites.value];
    emit('invites-refreshed');
  } catch (err) {
    error.value = err?.response?.data?.error || 'Gagal membuat invite.';
  } finally {
    busy.value = false;
  }
}

function initials(name) {
  if (!name) return '?';
  return name.split(' ').map((p) => p[0]).slice(0, 2).join('').toUpperCase();
}
</script>
