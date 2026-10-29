<!-- frontend/src/components/KanbanBoard.vue -->
<!-- Sprint board per tim. read-only untuk Viewer; empty state untuk tim baru. -->
<template>
  <div class="flex-1 overflow-x-auto p-6 bg-white flex flex-col">

    <!-- ── Top Action Bar: Create Issue + Sprint controls ───────────────── -->
    <div class="flex items-center justify-between mb-4 gap-3 flex-wrap">
      <!-- Kiri: Sprint selector + sprint actions -->
      <div class="flex items-center gap-2 flex-wrap">
        <template v-if="sprints.length">
          <select
            :value="selectedSprintId"
            @change="$emit('select-sprint', $event.target.value)"
            class="border border-[#DFE1E6] rounded px-2 py-1.5 text-sm text-[#172B4D] bg-white"
          >
            <option value="backlog">Backlog (tanpa sprint)</option>
            <option v-for="s in sprints" :key="s.id" :value="s.id">
              {{ s.name }} — {{ s.state.toUpperCase() }}
            </option>
          </select>
          <span
            class="text-[10px] font-bold px-2 py-0.5 rounded-full"
            :class="{
              'bg-[#E3FCEF] text-[#006644]': currentSprint?.state === 'active',
              'bg-[#EEF2FF] text-[#1226AA]': currentSprint?.state === 'future',
              'bg-[#F4F5F7] text-[#6B778C]': currentSprint?.state === 'done',
            }"
          >{{ currentSprint ? currentSprint.state.toUpperCase() : 'BACKLOG' }}</span>
          <span
            v-if="daysLeft !== null"
            class="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-[#EEF2FF] text-[#1226AA]"
          >{{ daysLeft }} hari tersisa</span>
        </template>
        <span v-else class="text-xs text-[#6B778C] italic">Belum ada sprint</span>

        <!-- Sprint management (Admin only) -->
        <template v-if="canManage">
          <button
            @click="$emit('create-sprint')"
            class="text-xs font-semibold px-3 py-1.5 rounded-lg bg-[#1226AA] text-white hover:bg-[#0E1F8C] flex items-center gap-1 shadow-xs transition-colors"
          >
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            Buat Sprint
          </button>
          <button
            v-if="currentSprint?.state === 'future'"
            @click="$emit('start-sprint', currentSprint.id)"
            class="text-xs font-semibold px-3 py-1.5 rounded border border-[#36B37E] text-[#006644] hover:bg-[#E3FCEF]"
          >▶ Start Sprint</button>
          <button
            v-if="currentSprint?.state === 'active'"
            @click="$emit('complete-sprint', currentSprint.id)"
            class="text-xs font-semibold px-3 py-1.5 rounded border border-[#DFE1E6] text-[#172B4D] hover:bg-[#F4F5F7]"
          >✓ Complete Sprint</button>
          <button
            v-if="currentSprint"
            @click="$emit('edit-sprint', currentSprint)"
            class="text-xs font-semibold px-3 py-1.5 rounded border border-[#DFE1E6] text-[#172B4D] hover:bg-[#F4F5F7] flex items-center gap-1"
          >✎ Edit Sprint</button>
          <button
            v-if="currentSprint"
            @click="$emit('delete-sprint', currentSprint.id)"
            class="text-xs font-semibold px-3 py-1.5 rounded border border-[#FFAB00] text-[#BF2600] hover:bg-[#FFFAE6]"
          >🗑 Hapus Sprint</button>
        </template>
      </div>

      <!-- Kanan: Create Issue button -->
      <div class="flex items-center gap-2">
        <button
          v-if="!readOnly"
          @click="$emit('open-create-issue')"
          class="flex items-center gap-1.5 text-xs font-semibold px-4 py-2 rounded-lg bg-[#1226AA] hover:bg-[#0E1F8C] text-white shadow-xs transition-colors"
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          Create Issue
        </button>
      </div>
    </div>

    <!-- ── Filter bar: search, avatar anggota, type, priority, only-mine ── -->
    <div class="flex items-center gap-2 mb-3 flex-wrap">
      <input
        v-model="filterText"
        placeholder="Filter kartu di board..."
        class="text-xs border border-[#DFE1E6] rounded px-3 py-1.5 w-48 focus:outline-none focus:border-[#1226AA]"
      />
      <div class="flex items-center -space-x-1.5">
        <button
          v-for="m in members"
          :key="m.userOid"
          @click="toggleAssignee(m.userOid)"
          :title="`${m.user?.name || m.userOid} (${m.user?.email || 'tanpa email'}) — filter assignee`"
          class="w-7 h-7 rounded-full text-[9px] font-bold flex items-center justify-center border-2 transition-all"
          :class="assigneeFilter === m.userOid
            ? 'border-[#1226AA] bg-[#1226AA] text-white z-10 scale-110'
            : 'border-white text-white'"
          :style="assigneeFilter !== m.userOid ? { backgroundColor: avatarColor(m.userOid) } : {}"
        >{{ initials(m.user?.name || m.userOid) }}</button>
      </div>
      <select v-model="typeFilter" class="text-xs border border-[#DFE1E6] rounded px-2 py-1.5">
        <option value="">Type: All</option>
        <option>Story</option><option>Task</option><option>Bug</option>
      </select>
      <select v-model="priorityFilter" class="text-xs border border-[#DFE1E6] rounded px-2 py-1.5">
        <option value="">Priority: All</option>
        <option>Highest</option><option>High</option><option>Medium</option><option>Low</option>
      </select>
      <label class="flex items-center gap-1.5 text-xs text-[#42526E] font-semibold">
        <input type="checkbox" v-model="onlyMine" class="accent-[#1226AA]" />
        Only My Issues
      </label>
      <button
        v-if="hasActiveFilters"
        @click="clearFilters"
        class="text-[10px] text-[#1226AA] hover:underline font-semibold"
      >Reset</button>
    </div>

    <!-- ── Progress / Stats Dashboard ───────────────────────────────────── -->
    <div
      v-if="issues.length > 0"
      class="mb-4 p-4 bg-[#F4F5F7] rounded-lg border border-[#DFE1E6]"
    >
      <div class="flex flex-wrap items-center gap-4 mb-3">
        <div class="flex items-center gap-1.5 text-xs font-semibold text-[#172B4D]">
          <span class="w-2.5 h-2.5 rounded-full bg-[#DFE1E6] inline-block"></span>
          Total: <span class="font-bold ml-0.5">{{ stats.total }}</span>
        </div>
        <div class="flex items-center gap-1.5 text-xs font-semibold text-[#1226AA]">
          <span class="w-2.5 h-2.5 rounded-full bg-[#1226AA] inline-block"></span>
          To Do: <span class="font-bold ml-0.5">{{ stats.todo }}</span>
        </div>
        <div class="flex items-center gap-1.5 text-xs font-semibold text-[#FF8B00]">
          <span class="w-2.5 h-2.5 rounded-full bg-[#FFAB00] inline-block"></span>
          In Progress: <span class="font-bold ml-0.5">{{ stats.inProgress }}</span>
        </div>
        <div class="flex items-center gap-1.5 text-xs font-semibold text-[#006644]">
          <span class="w-2.5 h-2.5 rounded-full bg-[#36B37E] inline-block"></span>
          Done: <span class="font-bold ml-0.5">{{ stats.done }}</span>
        </div>
        <div class="flex items-center gap-1.5 text-xs font-semibold text-[#42526E]">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
          SP: <span class="font-bold ml-0.5">{{ stats.doneSP }}/{{ stats.totalSP }}</span>
        </div>
      </div>
      <div>
        <div class="flex justify-between text-[11px] text-[#6B778C] mb-1">
          <span>Progress</span>
          <span class="font-semibold text-[#172B4D]">{{ stats.doneSP }}/{{ stats.totalSP }} SP ({{ stats.pct }}%)</span>
        </div>
        <div class="h-2.5 bg-[#DFE1E6] rounded-full overflow-hidden">
          <div
            class="h-full bg-[#1226AA] rounded-full transition-all duration-500"
            :style="{ width: stats.pct + '%' }"
          ></div>
        </div>
      </div>
    </div>

    <!-- ── Empty state ───────────────────────────────────────────────────── -->
    <div v-if="issues.length === 0" class="flex-1 flex items-center justify-center">
      <div class="text-center space-y-4">
        <div class="mx-auto w-16 h-16 rounded-full bg-[#F4F5F7] flex items-center justify-center">
          <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#97A0AF" stroke-width="1.6" stroke-linecap="round">
            <rect x="3" y="4" width="18" height="16" rx="2" />
            <path d="M3 10h18M9 10v10" />
          </svg>
        </div>
        <h3 class="text-base font-bold text-[#172B4D]">Belum ada issue di sprint ini</h3>
        <p class="text-xs text-[#6B778C] max-w-xs mx-auto">
          Klik tombol <strong>Create Issue</strong> di atas untuk mulai, atau buat Sprint baru terlebih dahulu.
        </p>
        <div class="flex items-center justify-center gap-3">
          <button
            v-if="!readOnly"
            @click="$emit('open-create-issue')"
            class="text-xs font-semibold px-4 py-2 rounded-lg bg-[#1226AA] hover:bg-[#0E1F8C] text-white shadow-xs transition-colors"
          >+ Create Issue</button>
          <button
            v-if="canManage"
            @click="$emit('create-sprint')"
            class="text-xs font-semibold px-4 py-2 rounded border border-[#DFE1E6] hover:bg-[#F4F5F7] text-[#172B4D]"
          >+ Buat Sprint</button>
        </div>
      </div>
    </div>

    <!-- ── Kanban columns ────────────────────────────────────────────────── -->
    <div v-else class="flex space-x-4 flex-1 min-w-[960px]">
      <div
        v-for="col in columns"
        :key="col"
        @dragover.prevent
        @drop="onDrop($event, col)"
        class="flex-1 bg-[#F4F5F7] rounded-md p-2.5 flex flex-col min-w-[200px]"
      >
        <!-- Column header: hitungan issue + total SP -->
        <div class="text-xs font-bold uppercase text-[#5E6C84] mb-3 px-1 flex justify-between items-center">
          <span>{{ col }} ({{ getIssuesByStatus(col).length }})</span>
          <span class="font-mono text-[10px] bg-[#DFE1E6] text-[#42526E] rounded px-1.5 py-0.5">{{ colSp(getIssuesByStatus(col)) }} SP</span>
        </div>

        <!-- Cards -->
        <div class="flex-1 overflow-y-auto space-y-2">
          <KanbanCard
            v-for="item in getIssuesByStatus(col)"
            :key="item.key"
            :issue="item"
            :draggable="!readOnly"
            :read-only="readOnly"
            @click="$emit('select-issue', item)"
            @delete="$emit('delete-issue', $event)"
          />
        </div>

        <!-- "+ Create issue" quick button di bawah tiap kolom (TO DO saja, Jira style) -->
        <button
          v-if="!readOnly && col === 'TO DO'"
          @click="$emit('open-create-issue')"
          class="mt-2 w-full text-left text-xs text-[#6B778C] hover:text-[#172B4D] hover:bg-[#EBECF0] rounded px-2 py-1.5 flex items-center gap-1 transition-colors"
        >
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          Create issue
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import KanbanCard from './KanbanCard.vue';

const props = defineProps({
  issues: { type: Array, default: () => [] },
  readOnly: { type: Boolean, default: false },
  sprints: { type: Array, default: () => [] },
  selectedSprintId: { type: [Number, String], default: null },
  canManage: { type: Boolean, default: false },
  members: { type: Array, default: () => [] },
  currentUserOid: { type: String, default: '' },
});
const emit = defineEmits([
  'select-issue', 'status-change', 'select-sprint',
  'create-sprint', 'edit-sprint', 'start-sprint', 'complete-sprint', 'delete-sprint',
  'delete-issue', 'open-create-issue',
]);

const columns = ['TO DO', 'IN PROGRESS', 'IN REVIEW', 'DONE'];

const currentSprint = computed(() =>
  props.sprints.find((s) => s.id === Number(props.selectedSprintId)) || null);

// ---- Filter lokal (search / assignee / type / priority / only-mine) ----
const filterText = ref('');
const assigneeFilter = ref('');
const typeFilter = ref('');
const priorityFilter = ref('');
const onlyMine = ref(false);

const hasActiveFilters = computed(() =>
  filterText.value || assigneeFilter.value || typeFilter.value || priorityFilter.value || onlyMine.value);

function clearFilters() {
  filterText.value = '';
  assigneeFilter.value = '';
  typeFilter.value = '';
  priorityFilter.value = '';
  onlyMine.value = false;
}

function toggleAssignee(oid) {
  assigneeFilter.value = assigneeFilter.value === oid ? '' : oid;
}

function avatarColor(oid) {
  const palette = ['#1226AA', '#36B37E', '#6554C0', '#FF991F', '#BF2600', '#00B8D9'];
  let h = 0;
  for (const ch of String(oid)) h = (h * 31 + ch.charCodeAt(0)) % palette.length;
  return palette[h];
}

function initials(name) {
  if (!name) return '?';
  return name.split(' ').map((p) => p[0]).slice(0, 2).join('').toUpperCase();
}

const filteredIssues = computed(() => props.issues.filter((i) => {
  if (filterText.value) {
    const q = filterText.value.toLowerCase();
    if (!i.summary.toLowerCase().includes(q) && !String(i.key).toLowerCase().includes(q)) return false;
  }
  if (assigneeFilter.value && i.assigneeOid !== assigneeFilter.value) return false;
  if (onlyMine.value && i.assigneeOid !== props.currentUserOid) return false;
  if (typeFilter.value && i.type !== typeFilter.value) return false;
  if (priorityFilter.value && i.priority !== priorityFilter.value) return false;
  return true;
}));

const getIssuesByStatus = (status) => filteredIssues.value.filter((i) => i.status === status);
const colSp = (list) => list.reduce((sum, i) => sum + (i.storyPoints || 0), 0);

// ---- Hari tersisa sprint aktif (dari endDate YYYY-MM-DD) ----
const daysLeft = computed(() => {
  if (!currentSprint.value?.endDate) return null;
  const end = new Date(currentSprint.value.endDate);
  const diff = Math.ceil((end - new Date()) / 86400000);
  return diff >= 0 ? diff : 0;
});

// ── Stats computed from current issues prop ──────────────────────────────
const stats = computed(() => {
  const all = props.issues;
  const total = all.length;
  const done = all.filter((i) => i.status === 'DONE').length;
  const inProgress = all.filter((i) => i.status === 'IN PROGRESS' || i.status === 'IN REVIEW').length;
  const todo = all.filter((i) => i.status === 'TO DO').length;
  const totalSP = all.reduce((s, i) => s + (i.storyPoints || 0), 0);
  const doneSP = all.filter((i) => i.status === 'DONE').reduce((s, i) => s + (i.storyPoints || 0), 0);
  const pct = totalSP > 0 ? Math.round((doneSP / totalSP) * 100) : 0;
  return { total, done, inProgress, todo, totalSP, doneSP, pct };
});

function onDrop(event, newStatus) {
  if (props.readOnly) return;
  const issueKey = event.dataTransfer.getData('text/plain');
  if (issueKey) {
    emit('status-change', { issueKey, newStatus });
  }
}
</script>
