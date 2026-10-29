<!-- frontend/src/components/modals/CreateIssueModal.vue -->
<!-- Modal '+ Create Issue' di dalam konteks tim aktif: key FIN-xxx dibuat otomatis oleh backend -->
<template>
  <div class="fixed inset-0 bg-[#080E2F]/65 backdrop-blur-xs flex items-center justify-center p-4 z-50" @click.self="$emit('close')">
    <div class="bg-white rounded-xl w-full max-w-md p-6 space-y-4 shadow-2xl border border-[#D0D7E2]">
      <div class="flex items-center justify-between border-b pb-3">
        <h2 class="text-base font-bold text-[#172B4D]">
          Create Issue <span class="font-mono text-xs text-[#1226AA]">di {{ team?.key }}</span>
        </h2>
        <button @click="$emit('close')" class="text-sm text-gray-500 hover:text-gray-800">✕</button>
      </div>

      <div class="space-y-1">
        <label class="text-xs font-semibold text-[#42526E]">Summary</label>
        <input
          v-model="form.summary"
          placeholder="Ringkasan singkat issue"
          class="w-full text-sm border border-[#DFE1E6] rounded px-3 py-2 outline-none focus:border-[#1226AA]"
        />
      </div>

      <div class="grid grid-cols-3 gap-3">
        <div class="space-y-1">
          <label class="text-xs font-semibold text-[#42526E]">Type</label>
          <select v-model="form.type" class="w-full text-sm border border-[#DFE1E6] rounded px-2 py-2">
            <option>Story</option>
            <option>Task</option>
            <option>Bug</option>
            <option>Epic</option>
          </select>
        </div>
        <div class="space-y-1">
          <label class="text-xs font-semibold text-[#42526E]">Priority</label>
          <select v-model="form.priority" class="w-full text-sm border border-[#DFE1E6] rounded px-2 py-2">
            <option>Highest</option>
            <option>High</option>
            <option>Medium</option>
            <option>Low</option>
          </select>
        </div>
        <div class="space-y-1">
          <label class="text-xs font-semibold text-[#42526E]">Story Points</label>
          <input v-model.number="form.storyPoints" type="number" min="1" max="21"
            class="w-full text-sm border border-[#DFE1E6] rounded px-2 py-2" />
        </div>
      </div>

      <div class="space-y-1">
        <label class="text-xs font-semibold text-[#42526E]">Sprint</label>
        <select v-model="form.sprintId" class="w-full text-sm border border-[#DFE1E6] rounded px-2 py-2">
          <option :value="null">Backlog (tanpa sprint)</option>
          <option v-for="s in sprints" :key="s.id" :value="s.id">
            {{ s.name }} ({{ s.state }})
          </option>
        </select>
      </div>

      <div class="space-y-1">
        <label class="text-xs font-semibold text-[#42526E]">Description</label>
        <textarea v-model="form.description" rows="3"
          class="w-full text-sm border border-[#DFE1E6] rounded px-3 py-2 outline-none focus:border-[#1226AA]"></textarea>
      </div>

      <div v-if="error" class="text-xs text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">{{ error }}</div>

      <div class="flex justify-end space-x-2">
        <button @click="$emit('close')" class="px-4 py-2 rounded bg-gray-100 text-xs font-semibold text-[#42526E] hover:bg-gray-200">Cancel</button>
        <button
          @click="submit"
          :disabled="busy"
          class="px-4 py-2 rounded-lg bg-[#1226AA] hover:bg-[#0E1F8C] text-white text-xs font-semibold disabled:opacity-60 shadow-xs transition-colors"
        >
          {{ busy ? 'Creating...' : 'Create' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { JiraApiService } from '../../services/jiraApi';

const props = defineProps({
  team: { type: Object, required: true },
  sprints: { type: Array, default: () => [] },
});
const emit = defineEmits(['close', 'created']);

const form = reactive({
  summary: '',
  type: 'Story',
  priority: 'Medium',
  storyPoints: 3,
  sprintId: props.sprints.find((s) => s.state === 'active')?.id ?? null,
  description: '',
});
const busy = ref(false);
const error = ref('');

async function submit() {
  if (busy.value) return;
  error.value = '';
  if (!form.summary.trim()) {
    error.value = 'Summary wajib diisi.';
    return;
  }
  busy.value = true;
  try {
    const issue = await JiraApiService.createIssue(props.team.id, {
      summary: form.summary.trim(),
      type: form.type,
      priority: form.priority,
      storyPoints: form.storyPoints,
      sprintId: form.sprintId,
      description: form.description.trim(),
    });
    emit('created', issue);
    emit('close');
  } catch (err) {
    error.value = err?.response?.data?.error || 'Gagal membuat issue.';
  } finally {
    busy.value = false;
  }
}
</script>
