<!-- frontend/src/components/IssueDetailModal.vue -->
<!-- Issue Detail Modal 2 kolom ala Jira:
     kiri  = summary, description, subtasks, comments;
     kanan = field detail (status, assignee, reporter, priority, type, SP, sprint). -->
<template>
  <div class="fixed inset-0 bg-[#080E2F]/65 backdrop-blur-xs flex items-center justify-center p-4 z-50" @click.self="$emit('close')">
    <div class="bg-white rounded-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl border border-[#D0D7E2]">
      <!-- Header -->
      <div class="flex items-center justify-between px-6 pt-5 pb-3 border-b border-[#EBECF0]">
        <div class="flex items-center gap-2">
          <span class="font-mono text-sm font-bold text-[#1226AA]">{{ localIssue.key }}</span>
          <span class="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-[#EBECF0] text-[#42526E]">
            {{ localIssue.type }}
          </span>
        </div>
        <div class="flex items-center gap-2">
          <button
            v-if="!readOnly"
            @click="$emit('delete', localIssue.key)"
            class="text-xs font-semibold px-2.5 py-1 rounded border border-[#FFAB00] text-[#BF2600] hover:bg-[#FFFAE6] flex items-center gap-1 transition-colors"
            title="Hapus issue ini secara permanen"
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            </svg>
            Delete Issue
          </button>
          <button @click="$emit('close')" class="text-sm text-[#6B778C] hover:text-[#172B4D] px-1">✕</button>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 p-6">
        <!-- ===== Kolom kiri (2/3): konten ===== -->
        <div class="md:col-span-2 space-y-5">
          <div>
            <label class="text-[10px] font-bold uppercase text-[#6B778C]">Summary</label>
            <input
              v-model="localIssue.summary"
              :readonly="readOnly"
              class="mt-1 w-full text-base font-semibold border border-[#DFE1E6] rounded px-3 py-2 read-only:bg-[#F4F5F7] focus:outline-none focus:border-[#1226AA]"
            />
          </div>

          <div>
            <label class="text-[10px] font-bold uppercase text-[#6B778C]">Description</label>
            <textarea
              v-model="localIssue.description"
              :readonly="readOnly"
              rows="4"
              class="mt-1 w-full text-sm border border-[#DFE1E6] rounded p-3 read-only:bg-[#F4F5F7] focus:outline-none focus:border-[#1226AA]"
            ></textarea>
          </div>

          <!-- Subtasks -->
          <div>
            <div class="flex items-center justify-between mb-2">
              <label class="text-[10px] font-bold uppercase text-[#6B778C]">
                Subtasks ({{ doneSubtasks }}/{{ (localIssue.subtasks || []).length }})
              </label>
              <div class="w-32 h-1.5 bg-[#EBECF0] rounded-full overflow-hidden">
                <div class="h-full bg-[#36B37E]" :style="{ width: subtaskPct + '%' }"></div>
              </div>
            </div>
            <div class="space-y-1.5">
              <div
                v-for="st in localIssue.subtasks || []"
                :key="st.id"
                class="flex items-center justify-between text-sm text-[#172B4D] bg-[#FAFBFC] border border-[#EBECF0] rounded-lg px-3 py-2 group hover:border-[#DFE1E6] transition-colors"
              >
                <label class="flex items-center gap-2 cursor-pointer flex-1 min-w-0 select-none">
                  <input
                    type="checkbox"
                    :checked="st.done"
                    :disabled="readOnly"
                    @change="toggleSubtask(st)"
                    class="w-4 h-4 accent-[#36B37E] cursor-pointer rounded"
                  />
                  <span :class="st.done ? 'line-through text-[#97A0AF]' : ''" class="truncate">{{ st.title }}</span>
                </label>
                <button
                  v-if="!readOnly"
                  @click="removeSubtask(st.id)"
                  type="button"
                  class="opacity-0 group-hover:opacity-100 transition-opacity text-[#97A0AF] hover:text-[#BF2600] p-1 rounded hover:bg-[#FFEBE6] text-xs shrink-0 cursor-pointer"
                  title="Hapus subtask"
                >
                  ✕
                </button>
              </div>
              <p v-if="!(localIssue.subtasks || []).length" class="text-xs text-[#97A0AF] italic py-1">
                Belum ada subtask.
              </p>
            </div>
            <div v-if="!readOnly" class="flex gap-2 mt-2">
              <input
                v-model="newSubtask"
                @keydown.enter.prevent="addSubtask"
                placeholder="+ Tambah subtask (tekan Enter untuk kirim)..."
                class="flex-1 text-xs border border-[#DFE1E6] rounded px-3 py-1.5 focus:outline-none focus:border-[#1226AA]"
              />
              <button
                type="button"
                @click="addSubtask"
                :disabled="!newSubtask.trim() || busySub"
                class="text-xs font-semibold px-3 py-1.5 rounded-lg bg-[#1226AA] text-white hover:bg-[#0E1F8C] disabled:opacity-50 transition-colors shadow-xs"
              >
                {{ busySub ? '...' : 'Add' }}
              </button>
            </div>
          </div>

          <!-- Comments -->
          <div>
            <div class="flex items-center justify-between mb-1.5">
              <label class="text-[10px] font-bold uppercase text-[#6B778C]">
                Comments ({{ (localIssue.comments || []).length }})
              </label>
              <span class="text-[10px] text-[#6B778C]">
                Ketik <span class="font-mono font-bold text-[#1226AA]">@</span> untuk mention email rekan tim
              </span>
            </div>

            <div ref="commentsContainerRef" class="space-y-2 mt-2 max-h-64 overflow-y-auto pr-1">
              <div
                v-for="cm in localIssue.comments || []"
                :key="cm.id"
                class="bg-[#FAFBFC] border border-[#EBECF0] rounded-lg p-3 space-y-1 shadow-2xs"
              >
                <div class="text-[10px] font-mono text-[#6B778C] flex items-center justify-between">
                  <span class="font-semibold text-[#172B4D]">{{ cm.author }}</span>
                  <span>{{ cm.time }}</span>
                </div>
                <div
                  class="text-xs text-[#172B4D] whitespace-pre-wrap leading-relaxed"
                  v-html="renderComment(cm.text)"
                ></div>
              </div>
              <p v-if="!(localIssue.comments || []).length" class="text-xs text-[#97A0AF] italic py-2">
                Belum ada komentar.
              </p>
            </div>

            <div v-if="!readOnly" class="mt-3 space-y-1.5 relative">
              <!-- Autocomplete dropdown for @mentions -->
              <div
                v-if="showMentionMenu && filteredMembers.length"
                class="absolute bottom-full mb-1.5 left-0 w-80 bg-white border border-[#DFE1E6] rounded-lg shadow-xl z-50 overflow-hidden divide-y divide-[#EBECF0]"
              >
                <div class="px-3 py-1.5 bg-[#FAFBFC] text-[10px] font-bold uppercase text-[#6B778C] flex items-center justify-between">
                  <span>Pilih Anggota (Kirim Notifikasi Email)</span>
                  <span class="text-[9px] font-normal lowercase text-[#97A0AF]">klik untuk mention</span>
                </div>
                <div class="max-h-48 overflow-y-auto">
                  <button
                    v-for="m in filteredMembers"
                    :key="m.userOid"
                    type="button"
                    @mousedown.prevent="selectMention(m)"
                    class="w-full flex items-center gap-2.5 px-3 py-2 text-left hover:bg-[#EEF2FF] text-xs transition-colors cursor-pointer"
                  >
                    <div class="w-6 h-6 rounded-full bg-[#1226AA] text-white flex items-center justify-center text-[10px] font-bold shrink-0">
                      {{ (m.user?.name || m.userOid)[0].toUpperCase() }}
                    </div>
                    <div class="min-w-0 flex-1">
                      <div class="font-semibold text-[#172B4D] truncate">{{ m.user?.name || m.userOid }}</div>
                      <div class="text-[10px] text-[#1226AA] font-mono truncate">✉ {{ m.user?.email || 'tanpa email' }}</div>
                    </div>
                  </button>
                </div>
              </div>

              <!-- Input text box & Send button -->
              <div class="flex gap-2">
                <input
                  ref="commentInputRef"
                  v-model="newComment"
                  @input="handleCommentInput"
                  @keydown="handleCommentKeydown"
                  @blur="hideMentionMenuDelayed"
                  placeholder="Tulis komentar... (ketik @ untuk mention email rekan tim, tekan Enter untuk kirim)"
                  class="flex-1 text-xs border border-[#DFE1E6] rounded px-3 py-2 focus:outline-none focus:border-[#1226AA] bg-white"
                />
                <button
                  type="button"
                  @click="addComment"
                  :disabled="!newComment.trim() || busyCom"
                  class="text-xs font-semibold px-4 py-2 rounded-lg bg-[#1226AA] hover:bg-[#0E1F8C] text-white disabled:opacity-50 transition-colors shadow-xs shrink-0 cursor-pointer"
                >
                  {{ busyCom ? 'Mengirim...' : 'Send' }}
                </button>
              </div>

              <!-- Quick Mention Chips -->
              <div v-if="members.length" class="flex items-center gap-1.5 flex-wrap pt-1">
                <span class="text-[10px] font-semibold text-[#6B778C]">@ Mention:</span>
                <button
                  v-for="m in members"
                  :key="m.userOid"
                  type="button"
                  @click="insertMention(m)"
                  class="text-[10px] font-medium bg-[#FAFBFC] border border-[#DFE1E6] hover:bg-[#EEF2FF] hover:border-[#C7D2FE] hover:text-[#1226AA] text-[#42526E] rounded-full px-2.5 py-0.5 transition-colors cursor-pointer flex items-center gap-1"
                  :title="`Kirim email ke ${m.user?.email || m.userOid}`"
                >
                  <span>@{{ (m.user?.name || m.userOid).split(' ')[0] }}</span>
                  <span v-if="m.user?.email" class="text-[9px] text-[#6B778C] font-mono">({{ m.user.email.split('@')[0] }})</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- ===== Kolom kanan (1/3): detail fields ===== -->
        <div class="space-y-4 bg-[#FAFBFC] border border-[#EBECF0] rounded-lg p-4">
          <div>
            <label class="text-[10px] font-bold uppercase text-[#6B778C]">Status</label>
            <select v-if="!readOnly" v-model="localIssue.status" class="mt-1 w-full text-sm border border-[#DFE1E6] rounded px-2 py-1.5">
              <option>TO DO</option><option>IN PROGRESS</option><option>IN REVIEW</option><option>DONE</option>
            </select>
            <div v-else class="mt-1 text-sm font-semibold">{{ localIssue.status }}</div>
          </div>

          <div>
            <label class="text-[10px] font-bold uppercase text-[#6B778C]">Assignee</label>
            <div v-if="!readOnly" class="space-y-1">
              <select v-model="localIssue.assigneeOid" class="mt-1 w-full text-sm border border-[#DFE1E6] rounded px-2 py-1.5">
                <option :value="null">Unassigned</option>
                <option v-for="m in members" :key="m.userOid" :value="m.userOid">
                  {{ m.user?.name || m.userOid }} {{ m.user?.email ? `(${m.user.email})` : '' }}
                </option>
              </select>
              <div v-if="assigneeUser?.email" class="text-xs text-[#1226AA] font-mono px-0.5">
                ✉ {{ assigneeUser.email }}
              </div>
            </div>
            <div v-else class="mt-1">
              <div class="text-sm font-semibold text-[#172B4D]">{{ assigneeUser?.name || 'Unassigned' }}</div>
              <div v-if="assigneeUser?.email" class="text-xs text-[#6B778C] font-mono">✉ {{ assigneeUser.email }}</div>
            </div>
          </div>

          <div>
            <label class="text-[10px] font-bold uppercase text-[#6B778C]">Reporter</label>
            <div class="mt-1 text-sm text-[#42526E] font-mono text-xs flex items-center gap-1.5">
              <span>✉</span>
              <span>{{ localIssue.reporterEmail || '—' }}</span>
            </div>
          </div>

          <div>
            <label class="text-[10px] font-bold uppercase text-[#6B778C]">Priority</label>
            <select v-if="!readOnly" v-model="localIssue.priority" class="mt-1 w-full text-sm border border-[#DFE1E6] rounded px-2 py-1.5">
              <option>Highest</option><option>High</option><option>Medium</option><option>Low</option><option>Lowest</option>
            </select>
            <div v-else class="mt-1 text-sm">{{ localIssue.priority }}</div>
          </div>

          <div>
            <label class="text-[10px] font-bold uppercase text-[#6B778C]">Story Points</label>
            <input
              v-if="!readOnly"
              v-model.number="localIssue.storyPoints"
              type="number" min="0" max="100"
              class="mt-1 w-full text-sm border border-[#DFE1E6] rounded px-2 py-1.5 focus:outline-none focus:border-[#1226AA]"
            />
            <div v-else class="mt-1 text-sm font-bold">{{ localIssue.storyPoints }} SP</div>
          </div>

          <div>
            <label class="text-[10px] font-bold uppercase text-[#6B778C]">Sprint</label>
            <select v-if="!readOnly" v-model="localIssue.sprintId" class="mt-1 w-full text-sm border border-[#DFE1E6] rounded px-2 py-1.5">
              <option :value="null">Backlog</option>
              <option v-for="s in sprints" :key="s.id" :value="s.id">{{ s.name }}</option>
            </select>
            <div v-else class="mt-1 text-sm">{{ sprintName }}</div>
          </div>

          <div class="pt-3 border-t border-[#EBECF0] flex items-center justify-between gap-2">
            <button
              v-if="!readOnly"
              @click="$emit('delete', localIssue.key)"
              class="px-3 py-1.5 rounded border border-[#FFAB00] text-[#BF2600] hover:bg-[#FFFAE6] text-xs font-semibold flex items-center gap-1"
            >
              🗑 Delete Issue
            </button>
            <div v-else></div>
            <div class="flex items-center gap-2">
              <button @click="$emit('close')" class="px-4 py-1.5 rounded bg-[#EBECF0] text-xs font-semibold text-[#42526E] hover:bg-[#DFE1E6]">
                Close
              </button>
              <button
                v-if="!readOnly"
                @click="$emit('save', localIssue)"
                class="px-4 py-1.5 rounded-lg bg-[#1226AA] text-white text-xs font-semibold hover:bg-[#0E1F8C] shadow-xs transition-colors"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed, watch, nextTick } from 'vue';
import { JiraApiService } from '../services/jiraApi';

const props = defineProps({
  issue: { type: Object, required: true },
  readOnly: { type: Boolean, default: false },
  members: { type: Array, default: () => [] },
  sprints: { type: Array, default: () => [] },
  teamId: { type: Number, default: null },
});
const emit = defineEmits(['close', 'save', 'delete', 'refreshed', 'toast']);

const localIssue = reactive(JSON.parse(JSON.stringify(props.issue)));
const newSubtask = ref('');
const newComment = ref('');
const busySub = ref(false);
const busyCom = ref(false);
const commentsContainerRef = ref(null);

// Sinkronisasi data bila props.issue diperbarui oleh auto-sync / reload
watch(
  () => props.issue,
  (val) => {
    if (val && val.key === localIssue.key) {
      localIssue.subtasks = val.subtasks ? JSON.parse(JSON.stringify(val.subtasks)) : [];
      localIssue.comments = val.comments ? JSON.parse(JSON.stringify(val.comments)) : [];
      localIssue.summary = val.summary;
      localIssue.description = val.description;
      localIssue.status = val.status;
      localIssue.storyPoints = val.storyPoints;
      localIssue.assigneeOid = val.assigneeOid;
      localIssue.sprintId = val.sprintId;
    }
  },
  { deep: true }
);

// ---- @Mention Autocomplete & Highlights ----
const commentInputRef = ref(null);
const showMentionMenu = ref(false);
const mentionQuery = ref('');

const filteredMembers = computed(() => {
  const q = mentionQuery.value.trim().toLowerCase();
  if (!q) return props.members;
  return props.members.filter((m) => {
    const name = (m.user?.name || m.userOid || '').toLowerCase();
    const email = (m.user?.email || '').toLowerCase();
    return name.includes(q) || email.includes(q);
  });
});

function handleCommentInput(e) {
  const val = newComment.value;
  const cursor = e.target.selectionStart || val.length;
  const beforeCursor = val.slice(0, cursor);
  const lastAt = beforeCursor.lastIndexOf('@');
  if (lastAt !== -1 && (lastAt === 0 || /\s/.test(beforeCursor[lastAt - 1]))) {
    mentionQuery.value = beforeCursor.slice(lastAt + 1);
    showMentionMenu.value = true;
  } else {
    showMentionMenu.value = false;
  }
}

function handleCommentKeydown(e) {
  if (e.key === 'Escape') {
    showMentionMenu.value = false;
    return;
  }
  if (e.key === 'Enter') {
    e.preventDefault();
    // Jika dropdown mention sedang terbuka, pilih item pertama
    if (showMentionMenu.value && filteredMembers.value.length) {
      selectMention(filteredMembers.value[0]);
      return;
    }
    // Kirim komentar secara aman sekali tekan
    addComment();
  }
}

function hideMentionMenuDelayed() {
  setTimeout(() => {
    showMentionMenu.value = false;
  }, 250);
}

function selectMention(m) {
  const targetEmail = m.user?.email || m.user?.name || m.userOid;
  const val = newComment.value;
  const lastAt = val.lastIndexOf('@');
  if (lastAt !== -1) {
    newComment.value = val.slice(0, lastAt) + `@${targetEmail} `;
  } else {
    newComment.value += `@${targetEmail} `;
  }
  showMentionMenu.value = false;
  if (commentInputRef.value) {
    commentInputRef.value.focus();
  }
}

function insertMention(m) {
  const targetEmail = m.user?.email || m.user?.name || m.userOid;
  if (!newComment.value.endsWith(' ') && newComment.value.length > 0) {
    newComment.value += ' ';
  }
  newComment.value += `@${targetEmail} `;
  if (commentInputRef.value) {
    commentInputRef.value.focus();
  }
}

function renderComment(text) {
  if (!text) return '';
  const escaped = String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
  return escaped.replace(
    /@([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)/g,
    '<span class="inline-flex items-center gap-0.5 font-semibold text-[#1226AA] bg-[#EEF2FF] border border-[#C7D2FE] px-1.5 py-0.5 rounded font-mono text-[11px]">@$1</span>'
  );
}

const doneSubtasks = computed(() => (localIssue.subtasks || []).filter((s) => s.done).length);
const subtaskPct = computed(() => {
  const n = (localIssue.subtasks || []).length;
  return n ? Math.round((doneSubtasks.value / n) * 100) : 0;
});

const assigneeUser = computed(() => {
  const m = props.members.find((x) => x.userOid === localIssue.assigneeOid);
  return m?.user || null;
});
const assigneeName = computed(() => {
  return assigneeUser.value?.name || localIssue.assigneeOid || 'Unassigned';
});
const sprintName = computed(() => {
  const s = props.sprints.find((x) => x.id === localIssue.sprintId);
  return s ? s.name : 'Backlog';
});

async function addSubtask() {
  if (!newSubtask.value.trim() || busySub.value) return;
  busySub.value = true;
  const title = newSubtask.value.trim();
  try {
    const res = await JiraApiService.addSubtask(props.teamId, localIssue.key, title);
    // res adalah issue.to_dict() lengkap dengan daftar subtasks terbaru
    localIssue.subtasks = res.subtasks || [];
    newSubtask.value = '';
    emit('refreshed', res);
    emit('toast', { message: 'Subtask berhasil ditambahkan', type: 'success' });
  } catch (err) {
    emit('toast', { message: err?.response?.data?.error || 'Gagal menambah subtask', type: 'error' });
  } finally {
    busySub.value = false;
  }
}

async function toggleSubtask(st) {
  if (props.readOnly) return;
  const newDone = !st.done;
  st.done = newDone; // Optimistic update langsung di UI
  try {
    const res = await JiraApiService.toggleSubtask(props.teamId, localIssue.key, st.id, newDone);
    localIssue.subtasks = res.subtasks || [];
    emit('refreshed', res);
  } catch (err) {
    st.done = !newDone; // Revert jika gagal
    emit('toast', { message: 'Gagal memperbarui status subtask', type: 'error' });
  }
}

async function removeSubtask(stId) {
  if (props.readOnly) return;
  try {
    const res = await JiraApiService.deleteSubtask(props.teamId, localIssue.key, stId);
    localIssue.subtasks = res.subtasks || [];
    emit('refreshed', res);
    emit('toast', { message: 'Subtask dihapus', type: 'success' });
  } catch (err) {
    emit('toast', { message: 'Gagal menghapus subtask', type: 'error' });
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (commentsContainerRef.value) {
      commentsContainerRef.value.scrollTop = commentsContainerRef.value.scrollHeight;
    }
  });
}

async function addComment() {
  if (!newComment.value.trim() || busyCom.value) return;
  busyCom.value = true;
  showMentionMenu.value = false;
  const commentText = newComment.value.trim();
  try {
    const res = await JiraApiService.addComment(props.teamId, localIssue.key, commentText);
    // res adalah issue.to_dict() lengkap dengan daftar comments terbaru
    localIssue.comments = res.comments || [];
    newComment.value = '';
    scrollToBottom();
    emit('refreshed', res);

    if (res.mentioned && res.mentioned.length) {
      emit('toast', {
        message: `Komentar terkirim & notifikasi email dikirim ke ${res.mentioned.join(', ')}`,
        type: 'success',
      });
    } else {
      emit('toast', { message: 'Komentar berhasil ditambahkan', type: 'success' });
    }
  } catch (err) {
    emit('toast', { message: err?.response?.data?.error || 'Gagal menambah komentar', type: 'error' });
  } finally {
    busyCom.value = false;
  }
}
</script>
