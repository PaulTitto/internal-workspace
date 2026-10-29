<!-- frontend/src/components/JqlFilterView.vue -->
<!-- Issues & JQL Filter: pencarian/filter semua issue tim (client-side, sintaks
     filter sederhana ala JQL: type = Bug AND priority = High). -->
<template>
  <div class="flex-1 overflow-y-auto p-6 bg-white">
    <h2 class="text-lg font-bold text-[#172B4D] mb-3">Issues & JQL Filter</h2>

    <div class="flex items-center gap-2 mb-4 flex-wrap">
      <input
        v-model="query"
        placeholder='contoh: type = Bug AND priority = High  (atau teks bebas)'
        class="flex-1 min-w-[280px] font-mono text-xs border border-[#DFE1E6] rounded px-3 py-2 focus:outline-none focus:border-[#1226AA]"
      />
      <span class="text-xs text-[#6B778C]">{{ results.length }} hasil</span>
    </div>

    <div class="bg-white border border-[#DFE1E6] rounded divide-y divide-[#EBECF0]">
      <button
        v-for="i in results"
        :key="i.key"
        @click="$emit('select-issue', i)"
        class="w-full flex items-center justify-between px-4 py-2 text-xs hover:bg-[#F4F5F7] text-left"
      >
        <span class="flex items-center gap-2 min-w-0">
          <span class="font-mono font-semibold text-[#1226AA]">{{ i.key }}</span>
          <span class="text-[#172B4D] truncate">{{ i.summary }}</span>
        </span>
        <span class="flex items-center gap-2 shrink-0">
          <span class="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-[#EBECF0] text-[#42526E]">{{ i.status }}</span>
          <span class="text-[10px] px-1.5 py-0.5 rounded"
            :class="{
              'bg-[#FFEBE6] text-[#BF2600]': i.priority === 'Highest' || i.priority === 'High',
              'bg-[#FFFAE6] text-[#974F0C]': i.priority === 'Medium',
              'bg-[#E3FCEF] text-[#006644]': i.priority === 'Low' || i.priority === 'Lowest',
            }">{{ i.priority }}</span>
        </span>
      </button>
      <p v-if="!results.length" class="px-4 py-3 text-xs text-[#97A0AF] italic">
        Tidak ada issue yang cocok dengan filter.
      </p>
    </div>

    <p class="text-[10px] text-[#97A0AF] mt-3">
      Operator didukung: <span class="font-mono">=</span>, <span class="font-mono">AND</span>, <span class="font-mono">OR</span>.
      Field: <span class="font-mono">type, status, priority, assignee</span>. Tanpa operator = cari di summary/key.
    </p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({ issues: { type: Array, default: () => [] } });
defineEmits(['select-issue']);

const query = ref('');

const results = computed(() => {
  const q = query.value.trim();
  if (!q) return props.issues;
  // Sintaks sederhana: field = value (AND | OR) ...
  if (/=/i.test(q)) {
    const orParts = q.split(/\s+OR\s+/i);
    const match = (issue, part) =>
      part.split(/\s+AND\s+/i).every((clause) => {
        const m = clause.trim().match(/^(\w+)\s*=\s*(\S+)$/i);
        if (!m) return true;
        const field = m[1].toLowerCase();
        const value = m[2].replace(/['"]/g, '');
        const target = {
          type: issue.type, status: issue.status,
          priority: issue.priority,
          assignee: issue.assigneeOid || '',
        }[field];
        return target ? String(target).toLowerCase() === value.toLowerCase() : false;
      });
    return props.issues.filter((i) => orParts.some((p) => match(i, p)));
  }
  // teks bebas
  const lower = q.toLowerCase();
  return props.issues.filter((i) =>
    i.summary.toLowerCase().includes(lower) || i.key.toLowerCase().includes(lower));
});
</script>
