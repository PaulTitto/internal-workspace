<!-- frontend/src/components/JiraAiAgent.vue -->
<!-- Komponen Frontend Khusus AI Agent: User cukup mengetik prompt natural language -->
<template>
  <aside class="w-96 bg-white border-l border-[#DFE1E6] flex flex-col h-full shadow-xl">
    <div class="p-4 bg-[#080E2F] text-white flex items-center justify-between">
      <div class="flex items-center space-x-2">
        <span class="text-lg">🤖</span>
        <div>
          <h3 class="text-sm font-bold">SRKK AI Agent</h3>
          <p class="text-[11px] text-blue-200 font-mono">Prompt-to-Action (Function Calling)</p>
        </div>
      </div>
      <button @click="$emit('close')" class="text-slate-300 hover:text-white">✕</button>
    </div>

    <div class="flex-1 overflow-y-auto p-4 space-y-3 bg-[#FAFBFC]">
      <div
        v-for="(msg, i) in messages"
        :key="i"
        :class="msg.role === 'user' ? 'ml-6 bg-[#1226AA] text-white' : 'mr-4 bg-white border border-[#DFE1E6] text-[#172B4D]'"
        class="p-3 rounded-lg text-xs space-y-2 shadow-2xs"
      >
        <div class="leading-relaxed">{{ msg.text }}</div>
        <!-- Daftar Tool / Action yang dieksekusi otomatis oleh Agent -->
        <div v-if="msg.actions && msg.actions.length" class="pt-2 border-t border-slate-200 space-y-1">
          <div
            v-for="(act, idx) in msg.actions"
            :key="idx"
            class="px-2 py-1 rounded bg-emerald-50 text-emerald-800 font-mono text-[10px]"
          >
            ⚡ {{ act.tool }}: {{ act.summary }}
          </div>
        </div>
      </div>
    </div>

    <form @submit.prevent="submitPrompt" class="p-3 border-t border-[#DFE1E6] bg-white flex space-x-2">
      <input
        v-model="promptInput"
        placeholder="Ketik perintah (misal: Buatkan tiket bug login)..."
        class="flex-1 text-xs px-3 py-2 border border-[#DFE1E6] rounded outline-none focus:border-[#1226AA]"
      />
      <button type="submit" class="px-3 py-2 bg-[#1226AA] hover:bg-[#0E1F8C] text-white text-xs font-semibold rounded-lg shadow-xs transition-colors">
        Send
      </button>
    </form>
  </aside>
</template>

<script setup>
import { ref } from 'vue';
defineProps({ messages: Array });
const emit = defineEmits(['send', 'close']);
const promptInput = ref('');

function submitPrompt() {
  if (!promptInput.value.trim()) return;
  emit('send', promptInput.value.trim());
  promptInput.value = '';
}
</script>
