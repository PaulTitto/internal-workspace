<!-- frontend/src/components/AllSprintsView.vue -->
<!-- Semua Sprint & Backlog: issue dikelompokkan per sprint + kolom backlog, lengkap dengan kontrol sprint (Add/Edit/Delete/Start/Complete). -->
<template>
  <div class="flex-1 overflow-y-auto p-6 bg-white">
    <div class="flex items-center justify-between mb-4 flex-wrap gap-2">
      <div>
        <h2 class="text-lg font-bold text-[#172B4D]">Semua Sprint & Backlog — {{ team?.name }}</h2>
        <p class="text-xs text-[#6B778C]">Kelola seluruh siklus sprint, backlog, dan distribusi issue tim.</p>
      </div>

      <button
        v-if="canManage"
        @click="$emit('create-sprint')"
        class="text-xs font-semibold px-3 py-1.5 rounded-lg bg-[#1226AA] text-white hover:bg-[#0E1F8C] flex items-center gap-1 shadow-xs transition-colors"
      >
        <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
          <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        + Buat Sprint Baru
      </button>
    </div>

    <div v-if="!sprints.length && !backlog.length" class="text-sm text-[#6B778C] py-8 text-center bg-[#FAFBFC] border border-[#EBECF0] rounded-lg">
      Belum ada sprint maupun backlog issue. Buat sprint baru atau tambahkan issue.
    </div>

    <div v-for="s in sprints" :key="s.id" class="mb-6 bg-white border border-[#DFE1E6] rounded-lg overflow-hidden shadow-sm">
      <!-- Sprint Header -->
      <div class="bg-[#F4F5F7] px-4 py-3 flex items-center justify-between flex-wrap gap-2 border-b border-[#EBECF0]">
        <div class="flex items-center gap-2 flex-wrap">
          <h3 class="text-sm font-bold text-[#172B4D]">{{ s.name }}</h3>
          <span
            class="text-[9px] font-bold uppercase px-2 py-0.5 rounded-full"
            :class="{
              'bg-[#E3FCEF] text-[#006644]': s.state === 'active',
              'bg-[#EAE6FF] text-[#403294]': s.state === 'future',
              'bg-[#EBECF0] text-[#6B778C]': s.state === 'done',
            }"
          >{{ s.state }}</span>
          <span class="text-[11px] text-[#6B778C]">
            {{ issuesOf(s.id).length }} issue • {{ spOf(issuesOf(s.id)) }} SP
          </span>
          <span v-if="s.startDate || s.endDate" class="text-[10px] text-[#6B778C] bg-white border border-[#DFE1E6] px-2 py-0.5 rounded">
            📅 {{ s.startDate || '—' }} s/d {{ s.endDate || '—' }}
          </span>
        </div>

        <!-- Action buttons per sprint -->
        <div v-if="canManage" class="flex items-center gap-1.5 flex-wrap">
          <button
            v-if="s.state === 'future'"
            @click="$emit('start-sprint', s.id)"
            class="text-[11px] font-semibold px-2 py-1 rounded border border-[#36B37E] text-[#006644] bg-white hover:bg-[#E3FCEF]"
          >▶ Start Sprint</button>
          <button
            v-if="s.state === 'active'"
            @click="$emit('complete-sprint', s.id)"
            class="text-[11px] font-semibold px-2 py-1 rounded border border-[#DFE1E6] text-[#172B4D] bg-white hover:bg-[#EBECF0]"
          >✓ Complete Sprint</button>
          <button
            @click="$emit('edit-sprint', s)"
            class="text-[11px] font-semibold px-2 py-1 rounded border border-[#DFE1E6] text-[#172B4D] bg-white hover:bg-[#EBECF0] flex items-center gap-1"
          >✎ Edit</button>
          <button
            @click="$emit('delete-sprint', s.id)"
            class="text-[11px] font-semibold px-2 py-1 rounded border border-[#FFAB00] text-[#BF2600] bg-white hover:bg-[#FFFAE6]"
          >🗑 Hapus</button>
        </div>
      </div>

      <div v-if="s.goal" class="px-4 py-2 bg-[#FAFBFC] border-b border-[#EBECF0] text-xs text-[#5E6C84] italic">
        🎯 <strong>Goal:</strong> {{ s.goal }}
      </div>

      <!-- Issues in Sprint -->
      <div class="divide-y divide-[#EBECF0]">
        <div
          v-for="i in issuesOf(s.id)"
          :key="i.key"
          @click="$emit('select-issue', i)"
          class="flex items-center justify-between px-4 py-2.5 text-xs hover:bg-[#FAFBFC] cursor-pointer group"
        >
          <span class="flex items-center gap-2 min-w-0">
            <span class="font-mono font-semibold text-[#1226AA] shrink-0">{{ i.key }}</span>
            <span class="text-[#172B4D] truncate">{{ i.summary }}</span>
          </span>
          <span class="flex items-center gap-2 shrink-0">
            <span class="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-[#EBECF0] text-[#42526E]">{{ i.status }}</span>
            <span class="font-mono text-[10px] bg-[#DFE1E6] px-1.5 py-0.5 rounded">{{ i.storyPoints }} SP</span>
            <button
              v-if="canManage"
              @click.stop="$emit('delete-issue', i.key)"
              class="opacity-0 group-hover:opacity-100 transition-opacity text-[#97A0AF] hover:text-[#BF2600] p-1 rounded hover:bg-[#FFEBE6]"
              title="Hapus issue"
            >
              🗑
            </button>
          </span>
        </div>
        <p v-if="!issuesOf(s.id).length" class="px-4 py-3 text-xs text-[#97A0AF] italic">Tidak ada issue di sprint ini.</p>
      </div>
    </div>

    <!-- Backlog Section -->
    <div class="bg-white border border-[#DFE1E6] rounded-lg overflow-hidden shadow-sm">
      <div class="bg-[#F4F5F7] px-4 py-3 flex items-center justify-between border-b border-[#EBECF0]">
        <div class="flex items-center gap-2">
          <h3 class="text-sm font-bold text-[#172B4D]">Backlog</h3>
          <span class="text-[11px] text-[#6B778C]">{{ backlog.length }} issue • {{ spOf(backlog) }} SP</span>
        </div>
      </div>
      <div class="divide-y divide-[#EBECF0]">
        <div
          v-for="i in backlog"
          :key="i.key"
          @click="$emit('select-issue', i)"
          class="flex items-center justify-between px-4 py-2.5 text-xs hover:bg-[#FAFBFC] cursor-pointer group"
        >
          <span class="flex items-center gap-2 min-w-0">
            <span class="font-mono font-semibold text-[#1226AA] shrink-0">{{ i.key }}</span>
            <span class="text-[#172B4D] truncate">{{ i.summary }}</span>
          </span>
          <span class="flex items-center gap-2 shrink-0">
            <span class="font-mono text-[10px] bg-[#DFE1E6] px-1.5 py-0.5 rounded">{{ i.storyPoints }} SP</span>
            <button
              v-if="canManage"
              @click.stop="$emit('delete-issue', i.key)"
              class="opacity-0 group-hover:opacity-100 transition-opacity text-[#97A0AF] hover:text-[#BF2600] p-1 rounded hover:bg-[#FFEBE6]"
              title="Hapus issue"
            >
              🗑
            </button>
          </span>
        </div>
        <p v-if="!backlog.length" class="px-4 py-3 text-xs text-[#97A0AF] italic">Backlog kosong.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  team: { type: Object, default: null },
  sprints: { type: Array, default: () => [] },
  issues: { type: Array, default: () => [] },
  canManage: { type: Boolean, default: false },
});

defineEmits([
  'create-sprint',
  'edit-sprint',
  'start-sprint',
  'complete-sprint',
  'delete-sprint',
  'select-issue',
  'delete-issue',
]);

const issuesOf = (sprintId) => props.issues.filter((i) => i.sprintId === sprintId);
const backlog = computed(() => props.issues.filter((i) => !i.sprintId));
const spOf = (list) => list.reduce((s, i) => s + (i.storyPoints || 0), 0);
</script>
