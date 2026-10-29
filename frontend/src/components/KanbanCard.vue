<!-- frontend/src/components/KanbanCard.vue -->
<template>
  <div
    :draggable="draggable"
    @dragstart="onDragStart"
    :class="draggable ? 'cursor-grab' : 'cursor-pointer'"
    class="bg-white p-3 rounded border border-[#DFE1E6] shadow-2xs hover:shadow-md transition-all group relative"
  >
    <div class="flex items-start justify-between gap-1 mb-1.5">
      <div class="text-sm text-[#172B4D] font-medium leading-snug">{{ issue.summary }}</div>
      <button
        v-if="!readOnly"
        @click.stop="$emit('delete', issue.key)"
        class="opacity-0 group-hover:opacity-100 transition-opacity text-[#97A0AF] hover:text-[#BF2600] p-1 rounded hover:bg-[#FFEBE6] shrink-0"
        title="Hapus issue"
      >
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <polyline points="3 6 5 6 21 6"></polyline>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
        </svg>
      </button>
    </div>
    <div class="flex items-center justify-between text-xs text-[#5E6C84]">
      <span class="font-mono font-semibold text-[#1226AA]">{{ issue.key }}</span>
      <span class="bg-[#EBECF0] px-2 py-0.5 rounded-full font-semibold">{{ issue.storyPoints }} SP</span>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  issue: { type: Object, required: true },
  draggable: { type: Boolean, default: true },
  readOnly: { type: Boolean, default: false },
});
defineEmits(['delete']);

function onDragStart(e) {
  e.dataTransfer.setData('text/plain', props.issue.key);
}
</script>
