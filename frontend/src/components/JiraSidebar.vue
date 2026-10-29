<!-- frontend/src/components/JiraSidebar.vue -->
<!-- Sidebar tim aktif ala Jira: ringkasan tim, daftar sprint (1..4) dengan badge
     state + hitungan issue, navigasi views, dan share board link. -->
<template>
  <aside
    class="w-64 bg-[#FAFBFC] border-r border-[#DFE1E6] p-3 flex flex-col justify-between overflow-y-auto"
  >
    <nav class="space-y-1">
      <!-- Ringkasan tim aktif -->
      <div
        v-if="team"
        class="bg-white border border-[#DFE1E6] rounded-lg p-3 mb-4"
      >
        <div class="flex items-center gap-2">
          <div
            class="w-8 h-8 rounded-lg bg-[#1226AA] text-white flex items-center justify-center text-[10px] font-bold shadow-xs"
          >
            {{ team.key }}
          </div>
          <div class="min-w-0">
            <div class="text-xs font-bold text-[#172B4D] truncate">
              {{ team.name }}
            </div>
            <div class="text-[10px] text-[#6B778C]">
              {{ sprints.length }} Sprints di Tim Ini
            </div>
          </div>
        </div>
        <div
          v-if="canManage"
          class="mt-2.5 pt-2 border-t border-[#EBECF0] flex items-center gap-1.5"
        >
          <button
            @click="$emit('edit-team', team)"
            class="flex-1 text-[11px] font-semibold px-2 py-1 rounded border border-[#DFE1E6] bg-white hover:bg-[#F4F5F7] text-[#172B4D] flex items-center justify-center gap-1"
            title="Edit info tim"
          >
            ✎ Edit Tim
          </button>
          <button
            @click="$emit('delete-team', team)"
            class="text-[11px] font-semibold px-2 py-1 rounded border border-[#FFAB00] bg-white hover:bg-[#FFFAE6] text-[#BF2600] flex items-center justify-center gap-1"
            title="Hapus tim ini"
          >
            🗑
          </button>
        </div>
        <button
          @click="$emit('switch-team')"
          class="mt-2 w-full text-[11px] font-semibold px-2 py-1.5 rounded border border-[#DFE1E6] bg-white hover:bg-[#F4F5F7] text-[#42526E]"
        >
          ⇄ Ganti Tim / Workspace
        </button>
      </div>

      <!-- Daftar sprint -->
      <div v-if="sprints.length" class="mb-4">
        <div
          class="px-3 pt-2 pb-1 text-[10px] font-bold uppercase tracking-wide text-[#97A0AF] flex items-center justify-between"
        >
          <span>Sprint Tim (1 s/d {{ sprints.length }})</span>
          <button
            v-if="canManage"
            @click="$emit('create-sprint')"
            class="text-[#1226AA] hover:underline normal-case"
          >
            + Buat Sprint
          </button>
        </div>
        <button
          v-for="s in sprints"
          :key="s.id"
          @click="$emit('select-sprint', s.id)"
          class="w-full flex items-center justify-between px-3 py-1.5 rounded text-xs transition-colors"
          :class="
            String(selectedSprintId) === String(s.id)
              ? 'bg-[#EEF2FF] text-[#1226AA] font-semibold border border-[#C7D2FE]'
              : 'text-[#42526E] hover:bg-[#EBECF0]'
          "
        >
          <span class="flex items-center gap-1.5 truncate">
            <span
              class="w-1.5 h-1.5 rounded-full shrink-0"
              :class="{
                'bg-[#36B37E]': s.state === 'active',
                'bg-[#6554C0]': s.state === 'future',
                'bg-[#97A0AF]': s.state === 'done',
              }"
            ></span>
            <span class="truncate">{{ s.name }}</span>
          </span>
          <span
            class="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded-full shrink-0"
            :class="{
              'bg-[#E3FCEF] text-[#006644]': s.state === 'active',
              'bg-[#EAE6FF] text-[#403294]': s.state === 'future',
              'bg-[#EBECF0] text-[#6B778C]': s.state === 'done',
            }"
          >
            {{
              s.state === "active"
                ? "ACTIVE"
                : s.state === "future"
                ? "PLANNED"
                : "CLOSED"
            }}
          </span>
        </button>
      </div>

      <!-- Navigasi views -->
      <div
        class="px-3 pt-2 pb-1 text-[10px] font-bold uppercase tracking-wide text-[#97A0AF]"
      >
        Frontend Views (Vue 3)
      </div>
      <button
        v-for="v in views"
        :key="v.id"
        @click="$emit('switch-view', v.id)"
        class="w-full flex items-center justify-between px-3 py-2 rounded text-sm"
        :class="
          activeView === v.id
            ? 'bg-[#EEF2FF] text-[#1226AA] font-semibold'
            : 'text-[#42526E] hover:bg-[#EBECF0]'
        "
      >
        <span class="flex items-center gap-2">
          <span>{{ v.icon }}</span> {{ v.label }}
        </span>
        <span v-if="v.count != null" class="text-xs">{{ v.count }}</span>
      </button>
    </nav>

    <div class="pt-4">
      <button
        @click="$emit('share-board')"
        class="w-full flex items-center justify-center gap-1.5 text-[11px] font-semibold px-2 py-1.5 rounded border border-[#C7D2FE] bg-white hover:bg-[#EEF2FF] text-[#1226AA] transition-colors"
      >
        <svg
          width="11"
          height="11"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <circle cx="18" cy="5" r="3" />
          <circle cx="6" cy="12" r="3" />
          <circle cx="18" cy="19" r="3" />
          <line x1="8.59" y1="13.51" x2="15.42" y2="17.49" />
          <line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
        </svg>
        Share Board (Read-Only)
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  activeView: String,
  team: { type: Object, default: null },
  sprints: { type: Array, default: () => [] },
  selectedSprintId: { type: [Number, String], default: null },
  canManage: { type: Boolean, default: false },
  issuesCount: { type: Number, default: 0 },
  membersCount: { type: Number, default: 0 },
  backlogCount: { type: Number, default: 0 },
});

defineEmits([
  "switch-view",
  "switch-team",
  "select-sprint",
  "create-sprint",
  "edit-team",
  "delete-team",
  "share-board",
]);

const views = computed(() => [
  {
    id: "board",
    icon: "📋",
    label: "Active Sprint Board",
    count: props.issuesCount,
  },
  {
    id: "all-sprints",
    icon: "📁",
    label: "Semua Sprint & Backlog",
    count: null,
  },
  {
    id: "jql",
    icon: "🔍",
    label: "Issues & JQL Filter",
    count: props.issuesCount,
  },
  { id: "burndown", icon: "📈", label: "Burndown Reports", count: null },
  {
    id: "members",
    icon: "👥",
    label: "Team Members",
    count: props.membersCount,
  },
]);
</script>
