<!-- frontend/src/components/modals/EditSprintModal.vue -->
<!-- Modal Edit Sprint: ubah nama, goal, tanggal mulai/selesai, dan status sprint -->
<template>
  <div class="fixed inset-0 bg-[#080E2F]/65 backdrop-blur-xs flex items-center justify-center p-4 z-50" @click.self="$emit('close')">
    <div class="bg-white rounded-xl w-full max-w-md p-6 space-y-4 shadow-2xl border border-[#D0D7E2]">
      <div class="flex items-center justify-between border-b pb-3">
        <h2 class="text-base font-bold text-[#172B4D]">
          Edit Sprint <span class="font-mono text-xs text-[#1226AA]">#{{ sprint?.sprintNumber }}</span>
        </h2>
        <button @click="$emit('close')" class="text-sm text-gray-500 hover:text-gray-800">✕</button>
      </div>

      <div class="space-y-1">
        <label class="text-xs font-semibold text-[#42526E]">Nama Sprint</label>
        <input
          v-model="form.name"
          placeholder="Contoh: Sprint 1"
          class="w-full text-sm border border-[#DFE1E6] rounded px-3 py-2 outline-none focus:border-[#1226AA]"
        />
      </div>

      <div class="space-y-1">
        <label class="text-xs font-semibold text-[#42526E]">Sprint Goal</label>
        <textarea
          v-model="form.goal"
          rows="2"
          placeholder="Target yang ingin dicapai dalam sprint ini..."
          class="w-full text-sm border border-[#DFE1E6] rounded px-3 py-2 outline-none focus:border-[#1226AA]"
        ></textarea>
      </div>

      <div class="grid grid-cols-2 gap-3">
        <div class="space-y-1">
          <label class="text-xs font-semibold text-[#42526E]">Tanggal Mulai</label>
          <input
            v-model="form.startDate"
            type="date"
            class="w-full text-sm border border-[#DFE1E6] rounded px-3 py-2 outline-none focus:border-[#1226AA]"
          />
        </div>
        <div class="space-y-1">
          <label class="text-xs font-semibold text-[#42526E]">Tanggal Selesai</label>
          <input
            v-model="form.endDate"
            type="date"
            class="w-full text-sm border border-[#DFE1E6] rounded px-3 py-2 outline-none focus:border-[#1226AA]"
          />
        </div>
      </div>

      <div class="space-y-1">
        <label class="text-xs font-semibold text-[#42526E]">Status Sprint</label>
        <select
          v-model="form.state"
          class="w-full text-sm border border-[#DFE1E6] rounded px-2 py-2"
        >
          <option value="future">PLANNED (future)</option>
          <option value="active">ACTIVE</option>
          <option value="done">CLOSED (done)</option>
        </select>
        <p class="text-[11px] text-[#6B778C]">
          Catatan: Bila diubah ke ACTIVE, sprint aktif sebelumnya otomatis kembali ke PLANNED.
        </p>
      </div>

      <div v-if="error" class="text-xs text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">
        {{ error }}
      </div>

      <div class="flex justify-end space-x-2 pt-2 border-t">
        <button @click="$emit('close')" class="px-4 py-2 rounded bg-gray-100 text-xs font-medium text-[#42526E] hover:bg-gray-200">
          Batal
        </button>
        <button
          @click="submit"
          :disabled="busy"
          class="px-4 py-2 rounded-lg bg-[#1226AA] hover:bg-[#0E1F8C] text-white text-xs font-semibold disabled:opacity-60 shadow-xs transition-colors"
        >
          {{ busy ? 'Menyimpan...' : 'Simpan Perubahan' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, watch } from 'vue';

const props = defineProps({
  sprint: { type: Object, required: true },
});
const emit = defineEmits(['close', 'save']);

const form = reactive({
  name: props.sprint?.name || '',
  goal: props.sprint?.goal || '',
  startDate: props.sprint?.startDate || '',
  endDate: props.sprint?.endDate || '',
  state: props.sprint?.state || 'future',
});

watch(
  () => props.sprint,
  (s) => {
    if (s) {
      form.name = s.name || '';
      form.goal = s.goal || '';
      form.startDate = s.startDate || '';
      form.endDate = s.endDate || '';
      form.state = s.state || 'future';
    }
  },
  { immediate: true }
);

const busy = ref(false);
const error = ref('');

function submit() {
  if (!form.name.trim()) {
    error.value = 'Nama sprint tidak boleh kosong';
    return;
  }
  error.value = '';
  busy.value = true;
  emit('save', {
    id: props.sprint.id,
    name: form.name.trim(),
    goal: form.goal.trim(),
    startDate: form.startDate || null,
    endDate: form.endDate || null,
    state: form.state,
  });
}
</script>
