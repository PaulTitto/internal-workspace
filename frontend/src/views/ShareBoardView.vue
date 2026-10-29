<!-- frontend/src/views/ShareBoardView.vue -->
<!-- Public read-only board view — accessible via /share/<token> -->
<template>
  <div class="h-screen flex flex-col bg-white text-[#172B4D]">
    <!-- Loading -->
    <div
      v-if="state === 'loading'"
      class="flex-1 flex items-center justify-center"
    >
      <div class="text-center space-y-3">
        <div
          class="w-10 h-10 border-4 border-[#1226AA] border-t-transparent rounded-full animate-spin mx-auto"
        ></div>
        <p class="text-sm text-[#6B778C]">Loading shared board…</p>
      </div>
    </div>

    <!-- Error -->
    <div
      v-else-if="state === 'error'"
      class="flex-1 flex items-center justify-center"
    >
      <div class="text-center space-y-3 max-w-sm">
        <div class="text-5xl">🔗</div>
        <h2 class="text-lg font-bold text-[#172B4D]">
          Link tidak valid atau sudah expired
        </h2>
        <p class="text-sm text-[#6B778C]">{{ errorMsg }}</p>
      </div>
    </div>

    <!-- Board -->
    <template v-else-if="state === 'ready'">
      <!-- Navbar read-only -->
      <header
        class="h-14 bg-white border-b border-[#DFE1E6] px-5 flex items-center justify-between"
      >
        <div class="flex items-center space-x-4">
          <div class="flex items-center gap-2">
            <div
              class="w-7 h-7 rounded bg-[#1226AA] flex items-center justify-center text-white text-xs font-black"
            >
              SRKK
            </div>
            <div class="font-bold text-base text-[#1226AA]">SRKK Workspace</div>
          </div>
          <span class="text-[#DFE1E6]">/</span>
          <span class="text-sm font-semibold text-[#172B4D]">
            <span
              class="font-mono text-xs bg-[#EEF2FF] text-[#1226AA] border border-[#C7D2FE] px-1.5 py-0.5 rounded mr-2"
              >{{ boardData.team.key }}</span
            >
            {{ boardData.team.name }}
          </span>
          <span
            class="text-[10px] bg-[#FFFAE6] text-[#FF8B00] border border-[#FFAB00] px-2 py-0.5 rounded-full font-bold"
            >READ-ONLY</span
          >
        </div>
        <a href="/" class="text-xs text-[#1226AA] hover:underline font-semibold"
          >← Login to SRKK Workspace</a
        >
      </header>

      <!-- Kanban board (read-only, no sprint controls) -->
      <div class="flex-1 overflow-x-auto p-6 flex flex-col">
        <!-- Stats dashboard -->
        <div class="mb-4 p-4 bg-[#F4F5F7] rounded-lg border border-[#DFE1E6]">
          <div class="flex flex-wrap items-center gap-4 mb-3">
            <div class="text-xs font-semibold text-[#172B4D]">
              Total: <strong>{{ stats.total }}</strong>
            </div>
            <div class="text-xs font-semibold text-[#1226AA]">
              To Do: <strong>{{ stats.todo }}</strong>
            </div>
            <div class="text-xs font-semibold text-[#FF8B00]">
              In Progress: <strong>{{ stats.inProgress }}</strong>
            </div>
            <div class="text-xs font-semibold text-[#006644]">
              Done: <strong>{{ stats.done }}</strong>
            </div>
            <div class="text-xs font-semibold text-[#42526E]">
              SP: <strong>{{ stats.doneSP }}/{{ stats.totalSP }}</strong>
            </div>
          </div>
          <div>
            <div class="flex justify-between text-[11px] text-[#6B778C] mb-1">
              <span>Progress</span>
              <span class="font-semibold text-[#172B4D]"
                >{{ stats.doneSP }}/{{ stats.totalSP }} SP ({{
                  stats.pct
                }}%)</span
              >
            </div>
            <div class="h-2.5 bg-[#DFE1E6] rounded-full overflow-hidden">
              <div
                class="h-full bg-[#1226AA] rounded-full transition-all duration-500"
                :style="{ width: stats.pct + '%' }"
              ></div>
            </div>
          </div>
        </div>

        <!-- Sprint selector (view only) -->
        <div
          v-if="boardData.sprints.length"
          class="flex items-center gap-2 mb-4"
        >
          <select
            v-model="selectedSprintId"
            class="border border-[#DFE1E6] rounded px-2 py-1.5 text-sm text-[#172B4D] bg-white"
          >
            <option value="all">All Issues</option>
            <option v-for="s in boardData.sprints" :key="s.id" :value="s.id">
              {{ s.name }} — {{ s.state.toUpperCase() }}
            </option>
          </select>
        </div>

        <!-- Columns -->
        <div class="flex space-x-4 flex-1 min-w-[960px]">
          <div
            v-for="col in columns"
            :key="col"
            class="flex-1 bg-[#F4F5F7] rounded-md p-2.5 flex flex-col"
          >
            <div
              class="text-xs font-bold uppercase text-[#5E6C84] mb-3 px-1 flex justify-between"
            >
              <span>{{ col }}</span>
              <span>{{ getIssuesByStatus(col).length }}</span>
            </div>
            <div class="flex-1 overflow-y-auto space-y-2">
              <div
                v-for="item in getIssuesByStatus(col)"
                :key="item.key"
                class="bg-white rounded-md border border-[#DFE1E6] p-3 shadow-sm"
              >
                <div class="flex items-start justify-between gap-2 mb-1.5">
                  <span class="font-mono text-[10px] text-[#6B778C]">{{
                    item.key
                  }}</span>
                  <span
                    class="text-[10px] px-1.5 py-0.5 rounded-full font-semibold"
                    :class="priorityClass(item.priority)"
                    >{{ item.priority }}</span
                  >
                </div>
                <p class="text-xs font-medium text-[#172B4D] leading-snug">
                  {{ item.summary }}
                </p>
                <div
                  class="mt-2 flex items-center gap-2 text-[10px] text-[#6B778C]"
                >
                  <span>{{ item.type }}</span>
                  <span v-if="item.storyPoints" class="ml-auto font-semibold"
                    >{{ item.storyPoints }} SP</span
                  >
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import axios from "axios";

const state = ref("loading");
const errorMsg = ref("");
const boardData = ref({ team: {}, issues: [], sprints: [] });
const selectedSprintId = ref("all");

const columns = ["TO DO", "IN PROGRESS", "IN REVIEW", "DONE"];

onMounted(async () => {
  // Extract token from URL path: /share/<token>
  const parts = window.location.pathname.split("/");
  const token = parts[parts.indexOf("share") + 1];
  if (!token) {
    state.value = "error";
    errorMsg.value = "No share token found in URL.";
    return;
  }
  try {
    const baseURL =
      import.meta.env.VITE_FLASK_API_URL || "http://localhost:5001/api/v1";
    const { data } = await axios.get(`${baseURL}/share/${token}`);
    boardData.value = data;
    // Default to active sprint if available
    const active = data.sprints.find((s) => s.state === "active");
    selectedSprintId.value = active ? active.id : "all";
    state.value = "ready";
  } catch (err) {
    errorMsg.value =
      err?.response?.data?.error || "Share link tidak valid atau sudah expired";
    state.value = "error";
  }
});

const filteredIssues = computed(() => {
  if (selectedSprintId.value === "all") return boardData.value.issues;
  return boardData.value.issues.filter(
    (i) => i.sprintId === Number(selectedSprintId.value)
  );
});

const getIssuesByStatus = (status) =>
  filteredIssues.value.filter((i) => i.status === status);

const stats = computed(() => {
  const all = filteredIssues.value;
  const total = all.length;
  const done = all.filter((i) => i.status === "DONE").length;
  const inProgress = all.filter(
    (i) => i.status === "IN PROGRESS" || i.status === "IN REVIEW"
  ).length;
  const todo = all.filter((i) => i.status === "TO DO").length;
  const totalSP = all.reduce((s, i) => s + (i.storyPoints || 0), 0);
  const doneSP = all
    .filter((i) => i.status === "DONE")
    .reduce((s, i) => s + (i.storyPoints || 0), 0);
  const pct = totalSP > 0 ? Math.round((doneSP / totalSP) * 100) : 0;
  return { total, done, inProgress, todo, totalSP, doneSP, pct };
});

function priorityClass(priority) {
  const map = {
    Highest: "bg-red-100 text-red-700",
    High: "bg-orange-100 text-orange-700",
    Medium: "bg-yellow-100 text-yellow-700",
    Low: "bg-green-100 text-green-700",
    Lowest: "bg-gray-100 text-gray-500",
  };
  return map[priority] || "bg-gray-100 text-gray-500";
}
</script>
