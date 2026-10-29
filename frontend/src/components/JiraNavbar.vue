<!-- frontend/src/components/JiraNavbar.vue -->
<!-- Top navbar ala Jira Enterprise: brand, Semua Tim, tim aktif, sprint selector,
     + Sprint, + Create, AI Agent, search global, DB status, profil + Logout. -->
<template>
  <header
    class="h-14 bg-white border-b border-[#DFE1E6] px-4 flex items-center justify-between gap-3"
  >
    <div class="flex items-center space-x-3 min-w-0">
      <div class="flex items-center space-x-2 shrink-0">
        <div
          class="w-7 h-7 rounded-md bg-[#1226AA] flex items-center justify-center text-white text-xs font-black shadow-xs tracking-tight"
        >
          SRKK
        </div>
        <span
          class="font-extrabold text-sm text-[#1226AA] tracking-tight hidden sm:inline"
          >SRKK <span class="font-normal text-slate-500">Workspace</span></span
        >
      </div>

      <template v-if="activeTeam">
        <button
          @click="$emit('switch-team')"
          class="flex flex-col items-center px-2 py-1 rounded hover:bg-[#F4F5F7] text-[#42526E]"
          title="Semua Tim"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path
              d="M16 11c1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3 1.34 3 3 3zm-8 0c1.66 0 3-1.34 3-3S9.66 5 8 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"
            />
          </svg>
          <span class="text-[9px] font-semibold">Semua Tim</span>
        </button>
        <span class="text-[#DFE1E6]">/</span>

        <span class="text-sm font-semibold text-[#172B4D] truncate min-w-0">
          <span
            class="font-mono text-[10px] bg-[#EEF2FF] text-[#1226AA] border border-[#C7D2FE] px-1.5 py-0.5 rounded mr-1.5"
            >{{ activeTeam.key }}</span
          >
          <span class="hidden md:inline">{{ activeTeam.name }}</span>
        </span>

        <!-- Sprint selector -->
        <select
          v-if="sprints.length"
          :value="selectedSprintId ?? ''"
          @change="$emit('select-sprint', $event.target.value)"
          class="text-xs font-mono border border-[#DFE1E6] rounded px-2 py-1.5 text-[#172B4D] bg-white shrink-0"
        >
          <option value="backlog">BACKLOG</option>
          <option v-for="s in sprints" :key="s.id" :value="s.id">
            {{ activeTeam.key }} Sprint {{ s.sprintNumber
            }}{{ s.state === "active" ? " [ACTIVE]" : "" }}
          </option>
        </select>
      </template>
    </div>

    <div class="flex items-center gap-2 shrink-0">
      <template v-if="activeTeam">
        <button
          v-if="canManage"
          @click="$emit('create-sprint')"
          class="hidden lg:flex flex-col items-center px-2 py-0.5 rounded bg-[#E3FCEF] text-[#006644] hover:bg-[#79F2C0] text-[10px] font-bold leading-tight"
        >
          <span class="text-sm">+</span><span>Sprint</span>
        </button>
        <button
          v-if="canCreateIssue"
          @click="$emit('open-create')"
          class="bg-[#1226AA] hover:bg-[#0E1F8C] text-white text-xs font-semibold px-3 py-1.5 rounded shadow-xs transition-colors"
        >
          + Create
        </button>
        <button
          @click="$emit('open-agent')"
          class="bg-[#EAE6FF] hover:bg-[#DFD8FD] text-[#403294] text-xs font-semibold px-3 py-1.5 rounded flex items-center gap-1"
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
            <path
              d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h3a3 3 0 0 1 3 3v1h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v2a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3v-2H4a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1v-1a3 3 0 0 1 3-3h3V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2z"
            />
          </svg>
          AI Agent
        </button>
        <input
          :value="search"
          @input="$emit('update:search', $event.target.value)"
          placeholder="Cari tiket (PAY-101)..."
          class="hidden xl:block w-44 text-xs border border-[#DFE1E6] rounded px-3 py-1.5 focus:outline-none focus:border-[#1226AA]"
        />
      </template>

      <!-- DB Connected badge -->
      <!-- <span
        class="hidden md:flex items-center gap-1.5 text-[10px] font-semibold px-2 py-1 rounded-full"
        :class="dbMs != null ? 'bg-[#E3FCEF] text-[#006644]' : 'bg-[#FFEBE6] text-[#BF2600]'"
        :title="dbMs != null ? `Latensi API terakhir: ${dbMs}ms` : 'Menunggu request pertama'"
      >
        <span class="w-1.5 h-1.5 rounded-full" :class="dbMs != null ? 'bg-[#36B37E]' : 'bg-[#FF5630]'"></span>
        DB {{ dbMs != null ? 'Connected' : '...' }} <span v-if="dbMs != null" class="font-mono">({{ dbMs }}ms)</span>
      </span> -->

      <div
        class="w-7 h-7 rounded-full bg-[#1226AA] text-white flex items-center justify-center text-[10px] font-bold shadow-xs"
      >
        {{ initials(currentUser?.name) }}
      </div>
      <div class="hidden lg:block text-right leading-tight">
        <div class="font-semibold text-[#172B4D] text-xs">
          {{ currentUser?.name }}
        </div>
        <div class="font-mono text-[10px] text-[#6B778C]">
          {{ currentUser?.email }}
        </div>
      </div>
      <button
        @click="$emit('logout')"
        class="flex items-center gap-1 text-xs font-semibold px-2.5 py-1.5 rounded border border-[#DFE1E6] text-[#BF2600] hover:bg-[#FFEBE6] hover:border-[#BF2600]"
        title="Logout"
      >
        <svg
          width="13"
          height="13"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
          <polyline points="16 17 21 12 16 7" />
          <line x1="21" y1="12" x2="9" y2="12" />
        </svg>
        <span class="hidden sm:inline">Logout</span>
      </button>
    </div>
  </header>
</template>

<script setup>
import { msalInstance } from "../auth/msalAuth";
import { clearOAuthToken } from "../auth/oauthSession";

const emit = defineEmits([
  "open-create",
  "switch-team",
  "logout",
  "select-sprint",
  "create-sprint",
  "open-agent",
  "update:search",
]);

defineProps({
  currentUser: Object,
  activeTeam: { type: Object, default: null },
  sprints: { type: Array, default: () => [] },
  selectedSprintId: { type: [Number, String], default: null },
  canCreateIssue: { type: Boolean, default: false },
  canManage: { type: Boolean, default: false },
  search: { type: String, default: "" },
  dbMs: { type: Number, default: null },
});

function initials(name) {
  if (!name) return "?";
  return name
    .split(" ")
    .map((p) => p[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

async function handleLogout() {
  try {
    clearOAuthToken();
    const accounts = msalInstance.getAllAccounts();
    if (accounts.length > 0) {
      await msalInstance.logoutPopup({ account: accounts[0] });
    }
  } catch (err) {
    console.error("Logout error:", err);
  } finally {
    emit("logout");
  }
}
</script>
