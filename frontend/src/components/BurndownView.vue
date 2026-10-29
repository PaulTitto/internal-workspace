<!-- frontend/src/components/BurndownView.vue -->
<!-- Burndown Reports: chart SVG ideal-line vs sisa SP aktual, dihitung dari
     tanggal sprint (startDate/endDate) + distribusi updated_at issue DONE. -->
<template>
  <div class="flex-1 overflow-y-auto p-6 bg-white">
    <h2 class="text-lg font-bold text-[#172B4D] mb-1">Burndown Report</h2>
    <select v-model="sprintId" class="text-xs border border-[#DFE1E6] rounded px-2 py-1.5 mb-4">
      <option v-for="s in sprints" :key="s.id" :value="s.id">{{ s.name }} — {{ s.state }}</option>
    </select>

    <div v-if="!chart" class="text-sm text-[#6B778C]">
      Sprint ini belum punya rentang tanggal (startDate/endDate). Mulai sprint lewat
      <span class="font-semibold">▶ Start Sprint</span> di board untuk mengaktifkan burndown.
    </div>
    <div v-else class="space-y-3 max-w-3xl">
      <svg :viewBox="`0 0 640 260`" class="w-full border border-[#EBECF0] rounded bg-[#FAFBFC]">
        <!-- grid -->
        <line v-for="g in 5" :key="g" x1="40" :y1="20 + (g - 1) * 44" x2="620" :y2="20 + (g - 1) * 44" stroke="#EBECF0" />
        <!-- ideal line -->
        <polyline :points="chart.idealPoints" fill="none" stroke="#97A0AF" stroke-dasharray="4 4" stroke-width="1.5" />
        <!-- actual line -->
        <polyline :points="chart.actualPoints" fill="none" stroke="#1226AA" stroke-width="2.5" />
        <circle v-for="(p, i) in chart.actualDots" :key="i" :cx="p.x" :cy="p.y" r="3.5" fill="#1226AA" />
        <!-- labels -->
        <text x="8" y="24" font-size="10" fill="#6B778C">{{ chart.maxSp }} SP</text>
        <text x="8" y="248" font-size="10" fill="#6B778C">0</text>
        <text x="560" y="248" font-size="10" fill="#6B778C">{{ chart.endLabel }}</text>
        <text x="44" y="248" font-size="10" fill="#6B778C">{{ chart.startLabel }}</text>
      </svg>
      <div class="flex items-center gap-4 text-xs text-[#42526E]">
        <span class="flex items-center gap-1"><span class="inline-block w-6 h-0.5 bg-[#97A0AF]"></span> Ideal</span>
        <span class="flex items-center gap-1"><span class="inline-block w-6 h-0.5 bg-[#1226AA]"></span> Sisa SP aktual</span>
        <span>Total: <b>{{ chart.maxSp }} SP</b> • Selesai: <b>{{ chart.doneSp }} SP</b></span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';

const props = defineProps({
  sprints: { type: Array, default: () => [] },
  issues: { type: Array, default: () => [] },
});

const activeSprint = props.sprints.find((s) => s.state === 'active') || props.sprints[0];
const sprintId = ref(activeSprint?.id ?? null);
watch(() => props.sprints, (list) => {
  if (!sprintId.value && list.length) sprintId.value = list[0].id;
});

const chart = computed(() => {
  const sprint = props.sprints.find((s) => s.id === sprintId.value);
  if (!sprint?.startDate || !sprint?.endDate) return null;
  const start = new Date(sprint.startDate);
  const end = new Date(sprint.endDate);
  const days = Math.max(1, Math.round((end - start) / 86400000));

  const issues = props.issues.filter((i) => i.sprintId === sprint.id);
  const maxSp = issues.reduce((s, i) => s + (i.storyPoints || 0), 0);
  if (!maxSp) return null;

  // Sisa SP per hari: issue DONE dianggap selesai pada updated_at-nya
  const doneByDay = {};
  let doneSp = 0;
  for (const i of issues) {
    if (i.status === 'DONE') {
      doneSp += i.storyPoints || 0;
      const d = i.updatedAt ? new Date(i.updatedAt.replace(' ', 'T')) : end;
      const day = Math.min(days, Math.max(0, Math.round((d - start) / 86400000)));
      doneByDay[day] = (doneByDay[day] || 0) + (i.storyPoints || 0);
    }
  }

  const W = 580, H = 220, x0 = 40, y0 = 20;
  const x = (day) => x0 + (day / days) * W;
  const y = (sp) => y0 + (1 - sp / maxSp) * H;

  const idealPoints = [0, days].map((d) => `${x(d)},${y(maxSp * (1 - d / days))}`).join(' ');
  let remaining = maxSp;
  const actualDots = [{ x: x(0), y: y(remaining) }];
  for (let d = 1; d <= days; d++) {
    remaining -= doneByDay[d] || 0;
    actualDots.push({ x: x(d), y: y(remaining) });
  }
  const actualPoints = actualDots.map((p) => `${p.x},${p.y}`).join(' ');

  const fmt = (d) => d.toISOString().slice(5, 10);
  return {
    idealPoints, actualPoints, actualDots, maxSp, doneSp,
    startLabel: fmt(start), endLabel: fmt(end),
  };
});
</script>
