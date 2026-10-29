<!-- frontend/src/components/modals/EditTeamModal.vue -->
<!-- Modal Edit Team: ubah nama tim, key prefix, dan deskripsi -->
<template>
  <div class="fixed inset-0 bg-[#080E2F]/65 backdrop-blur-xs flex items-center justify-center p-4 z-50" @click.self="$emit('close')">
    <div class="bg-white rounded-xl w-full max-w-md p-6 space-y-4 shadow-2xl border border-[#D0D7E2]">
      <div class="flex items-center justify-between border-b pb-3">
        <h2 class="text-base font-bold text-[#172B4D]">
          Edit Team Settings <span class="font-mono text-xs text-[#1226AA]">({{ team?.key }})</span>
        </h2>
        <button @click="$emit('close')" class="text-sm text-gray-500 hover:text-gray-800">✕</button>
      </div>

      <div class="space-y-1">
        <label class="text-xs font-semibold text-[#42526E]">Team Name</label>
        <input
          v-model="form.name"
          placeholder="Contoh: Engineering Team"
          class="w-full text-sm border border-[#DFE1E6] rounded px-3 py-2 outline-none focus:border-[#1226AA]"
        />
      </div>

      <div class="space-y-1">
        <label class="text-xs font-semibold text-[#42526E]">Key Prefix</label>
        <input
          v-model="form.key"
          placeholder="ENG"
          maxlength="10"
          class="w-full text-sm font-mono uppercase border border-[#DFE1E6] rounded px-3 py-2 outline-none focus:border-[#1226AA]"
        />
        <p class="text-[11px] text-[#6B778C]">2–10 huruf kapital. Format identifier issue baru.</p>
      </div>

      <div class="space-y-1">
        <label class="text-xs font-semibold text-[#42526E]">Description</label>
        <textarea
          v-model="form.description"
          rows="3"
          placeholder="Fokus atau deskripsi tanggung jawab tim..."
          class="w-full text-sm border border-[#DFE1E6] rounded px-3 py-2 outline-none focus:border-[#1226AA]"
        ></textarea>
      </div>

      <div v-if="error" class="text-xs text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">
        {{ error }}
      </div>

      <div class="flex justify-end space-x-2 pt-2 border-t">
        <button
          @click="$emit('close')"
          class="px-4 py-2 rounded bg-gray-100 text-xs font-medium text-[#42526E] hover:bg-gray-200"
        >
          Cancel
        </button>
        <button
          @click="submit"
          :disabled="busy"
          class="px-4 py-2 rounded-lg bg-[#1226AA] hover:bg-[#0E1F8C] text-white text-xs font-semibold disabled:opacity-60 shadow-xs transition-colors"
        >
          {{ busy ? 'Saving...' : 'Save Changes' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, watch } from 'vue';

const props = defineProps({
  team: { type: Object, required: true },
});
const emit = defineEmits(['close', 'saved']);

const form = reactive({
  name: props.team?.name || '',
  key: props.team?.key || '',
  description: props.team?.description || '',
});

watch(
  () => props.team,
  (t) => {
    if (t) {
      form.name = t.name || '';
      form.key = t.key || '';
      form.description = t.description || '';
    }
  },
  { immediate: true }
);

const busy = ref(false);
const error = ref('');

function submit() {
  if (!form.name.trim()) {
    error.value = 'Team name is required';
    return;
  }
  if (!form.key.trim()) {
    error.value = 'Team key is required';
    return;
  }
  error.value = '';
  busy.value = true;
  emit('saved', {
    id: props.team.id,
    name: form.name.trim(),
    key: form.key.trim().toUpperCase(),
    description: form.description.trim(),
  });
}
</script>
