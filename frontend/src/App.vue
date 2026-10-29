<!-- frontend/src/App.vue -->
<!-- Orchestrator utama: alur SSO -> onboarding (empty state) -> pemilihan tim -> workspace -->
<template>
  <div class="h-screen flex flex-col bg-white text-[#172B4D]">
    <!-- 0. Public share view (no auth) -->
    <ShareBoardView v-if="screen === 'share'" />

    <!-- 1. Loading sesi SSO -->
    <LoadingScreen v-else-if="screen === 'loading'" label="Menyiapkan workspace JiraVue..." />

    <!-- 2. Login Microsoft Entra ID SSO -->
    <HomeLoginView v-else-if="screen === 'login'" @signed-in="handleSignedIn" />

    <!-- 3. Empty state onboarding: belum join tim mana pun -->
    <WelcomeWorkspaceView
      v-else-if="screen === 'welcome'"
      :user="me.user"
      @create-team="showCreateTeamModal = true"
      @join-team="showJoinTeamModal = true"
    />

    <!-- 4. Hub pemilihan tim -->
    <TeamSelectorView
      v-else-if="screen === 'team-select'"
      :user="me.user"
      :teams="me.teams"
      @select-team="enterTeam"
      @create-team="showCreateTeamModal = true"
      @join-team="showJoinTeamModal = true"
      @edit-team="handleOpenEditTeam"
      @delete-team="handleDeleteTeam"
      @logout="handleRequestLogout"
    />

    <!-- 5. Workspace tim aktif (kanban + member panel) -->
    <template v-else-if="screen === 'workspace' && activeTeam">
      <JiraNavbar
        :current-user="me.user"
        :active-team="activeTeam"
        :sprints="sprints"
        :selected-sprint-id="selectedSprintId"
        :can-create-issue="canWrite"
        :can-manage="myRole === 'Admin'"
        :search="globalSearch"
        :db-ms="dbMs"
        @open-create="showCreateIssueModal = true"
        @switch-team="leaveToTeamSelect"
        @logout="handleRequestLogout"
        @select-sprint="handleSelectSprint"
        @create-sprint="handleCreateSprint"
        @open-agent="showAgentPanel = true"
        @update:search="globalSearch = $event"
      />
      <!-- Banner: kode invite otomatis tim baru (Admin) -->
      <div
        v-if="inviteBanner"
        class="flex items-center justify-between gap-3 bg-[#E3FCEF] border-b border-[#79F2C0] px-5 py-2"
      >
        <div class="text-xs text-[#172B4D]">
          Tim dibuat! Kode invite untuk rekan Anda:
          <span class="font-mono font-bold text-sm">{{ inviteBanner }}</span>
          <span class="text-[#6B778C]"> (berlaku 7 hari — juga ada di tab Team Members)</span>
        </div>
        <div class="flex items-center gap-2">
          <button
            @click="copyInvite"
            class="text-xs font-semibold px-2 py-1 rounded border border-[#79F2C0] bg-white hover:bg-[#F4F5F7]"
          >Copy</button>
          <button
            @click="inviteBanner = null"
            class="text-xs text-[#6B778C] hover:text-[#172B4D] font-bold px-1"
          >✕</button>
        </div>
      </div>
      <div class="flex-1 flex overflow-hidden">
        <JiraSidebar
          :active-view="activeView"
          :issues-count="boardIssues.length"
          :backlog-count="backlogIssues.length"
          :members-count="members.length"
          :team="activeTeam"
          :sprints="sprints"
          :selected-sprint-id="selectedSprintId"
          :can-manage="myRole === 'Admin'"
          @switch-view="activeView = $event"
          @switch-team="leaveToTeamSelect"
          @select-sprint="handleSelectSprint"
          @create-sprint="handleCreateSprint"
          @edit-team="handleOpenEditTeam"
          @delete-team="handleDeleteTeam"
          @share-board="showShareModal = true"
        />

        <main class="flex-1 flex flex-col overflow-hidden">
          <KanbanBoard
            v-if="activeView === 'board'"
            :issues="boardIssues"
            :read-only="!canWrite"
            :sprints="sprints"
            :selected-sprint-id="selectedSprintId"
            :can-manage="myRole === 'Admin'"
            :members="members"
            :current-user-oid="me.user?.oid || ''"
            @select-issue="selectedIssue = $event"
            @status-change="handleStatusChange"
            @select-sprint="handleSelectSprint"
            @create-sprint="handleCreateSprint"
            @edit-sprint="handleOpenEditSprint"
            @start-sprint="handleStartSprint"
            @complete-sprint="handleCompleteSprint"
            @delete-sprint="handleDeleteSprint"
            @delete-issue="handleDeleteIssue"
            @open-create-issue="showCreateIssueModal = true"
          />
          <AllSprintsView
            v-else-if="activeView === 'all-sprints'"
            :team="activeTeam"
            :sprints="sprints"
            :issues="issues"
            :can-manage="myRole === 'Admin'"
            @select-issue="selectedIssue = $event"
            @delete-issue="handleDeleteIssue"
            @create-sprint="handleCreateSprint"
            @edit-sprint="handleOpenEditSprint"
            @start-sprint="handleStartSprint"
            @complete-sprint="handleCompleteSprint"
            @delete-sprint="handleDeleteSprint"
          />
          <JqlFilterView
            v-else-if="activeView === 'jql'"
            :issues="issues"
            @select-issue="selectedIssue = $event"
          />
          <BurndownView
            v-else-if="activeView === 'burndown'"
            :sprints="sprints"
            :issues="issues"
          />
          <TeamMembersPanel
            v-else-if="activeView === 'members'"
            :team="activeTeam"
            :members="members"
            :my-role="myRole"
            @invites-refreshed="loadInvitesIfAdmin"
            @edit-team="handleOpenEditTeam"
            @delete-team="handleDeleteTeam"
          />
        </main>
      </div>
    </template>

    <!-- Modals -->
    <CreateTeamModal
      v-if="showCreateTeamModal"
      @close="showCreateTeamModal = false"
      @created="handleTeamCreated"
    />
    <EditTeamModal
      v-if="editingTeam"
      :team="editingTeam"
      @close="editingTeam = null"
      @saved="handleSaveTeam"
    />
    <JoinTeamModal
      v-if="showJoinTeamModal"
      @close="showJoinTeamModal = false"
      @joined="handleTeamJoined"
    />
    <IssueDetailModal
      v-if="selectedIssue"
      :issue="selectedIssue"
      :read-only="!canWrite"
      :members="members"
      :sprints="sprints"
      :team-id="activeTeam?.id"
      @close="selectedIssue = null"
      @save="handleIssueUpdate"
      @delete="handleDeleteIssue"
      @refreshed="refreshIssues"
      @toast="showToast($event.message, $event.type)"
    />
    <!-- AI Agent: drawer kanan -->
    <div v-if="showAgentPanel" class="fixed inset-0 z-40" @click.self="showAgentPanel = false">
      <div class="absolute inset-y-0 right-0 flex">
        <JiraAiAgent :messages="agentMessages" @send="handleAgentPrompt" @close="showAgentPanel = false" />
      </div>
    </div>
    <CreateIssueModal
      v-if="showCreateIssueModal"
      :team="activeTeam"
      :sprints="sprints"
      @close="showCreateIssueModal = false"
      @created="handleIssueCreated"
    />
    <EditSprintModal
      v-if="editingSprint"
      :sprint="editingSprint"
      @close="editingSprint = null"
      @save="handleSaveSprint"
    />
    <ShareBoardModal
      v-if="showShareModal && activeTeam"
      :team-id="activeTeam.id"
      @close="showShareModal = false"
    />

    <!-- Custom Modal Konfirmasi (Ya/Tidak) -->
    <ConfirmModal
      v-if="confirmModal.show"
      :title="confirmModal.title"
      :message="confirmModal.message"
      :confirm-text="confirmModal.confirmText"
      :cancel-text="confirmModal.cancelText"
      :variant="confirmModal.variant"
      :busy="confirmModal.busy"
      @confirm="handleConfirmModalAction"
      @cancel="confirmModal.show = false"
    />

    <!-- Toast Notification (pengganti browser alert) -->
    <ToastNotification
      :toasts="toasts"
      @dismiss="dismissToast"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { JiraApiService } from './services/jiraApi';
import { msalInstance } from './auth/msalAuth';
import { consumeTokenFromUrl, hasOAuthSession, clearOAuthToken } from './auth/oauthSession';
import HomeLoginView from './views/HomeLoginView.vue';
import WelcomeWorkspaceView from './views/WelcomeWorkspaceView.vue';
import TeamSelectorView from './views/TeamSelectorView.vue';
import ShareBoardView from './views/ShareBoardView.vue';
import LoadingScreen from './components/LoadingScreen.vue';
import JiraNavbar from './components/JiraNavbar.vue';
import JiraSidebar from './components/JiraSidebar.vue';
import KanbanBoard from './components/KanbanBoard.vue';
import TeamMembersPanel from './components/TeamMembersPanel.vue';
import IssueDetailModal from './components/IssueDetailModal.vue';
import CreateIssueModal from './components/modals/CreateIssueModal.vue';
import CreateTeamModal from './components/modals/CreateTeamModal.vue';
import EditTeamModal from './components/modals/EditTeamModal.vue';
import EditSprintModal from './components/modals/EditSprintModal.vue';
import JoinTeamModal from './components/modals/JoinTeamModal.vue';
import ShareBoardModal from './components/modals/ShareBoardModal.vue';
import ConfirmModal from './components/modals/ConfirmModal.vue';
import ToastNotification from './components/ToastNotification.vue';
import AllSprintsView from './components/AllSprintsView.vue';
import JqlFilterView from './components/JqlFilterView.vue';
import BurndownView from './components/BurndownView.vue';
import JiraAiAgent from './components/JiraAiAgent.vue';
import { dbLatency } from './services/jiraApi';

const screen = ref('loading');
const me = ref({ user: null, teams: [], hasTeams: false });
const activeTeam = ref(null);
const activeView = ref('board');
const issues = ref([]);
const sprints = ref([]);
const selectedSprintId = ref(null);
const members = ref([]);
const selectedIssue = ref(null);

const showCreateTeamModal = ref(false);
const showJoinTeamModal = ref(false);
const showCreateIssueModal = ref(false);
const showShareModal = ref(false);
const showAgentPanel = ref(false);
const editingSprint = ref(null);
const editingTeam = ref(null);

// ---- Toast Notification System (pengganti window.alert browser) ----
const toasts = ref([]);
let toastSeq = 0;
function showToast(message, type = 'success', title = '') {
  const id = ++toastSeq;
  toasts.value.push({ id, message, type, title });
  setTimeout(() => {
    toasts.value = toasts.value.filter((t) => t.id !== id);
  }, 4000);
}
function dismissToast(id) {
  toasts.value = toasts.value.filter((t) => t.id !== id);
}

// ---- Custom Confirm Modal (pengganti window.confirm browser) ----
const confirmModal = ref({
  show: false,
  title: '',
  message: '',
  confirmText: 'Ya, Lanjutkan',
  cancelText: 'Tidak, Batal',
  variant: 'danger',
  busy: false,
  onConfirm: null,
});

function openConfirm({ title, message, confirmText = 'Ya, Lanjutkan', cancelText = 'Tidak, Batal', variant = 'danger', onConfirm }) {
  confirmModal.value = {
    show: true,
    title,
    message,
    confirmText,
    cancelText,
    variant,
    busy: false,
    onConfirm,
  };
}

async function handleConfirmModalAction() {
  if (!confirmModal.value.onConfirm) return;
  confirmModal.value.busy = true;
  try {
    await confirmModal.value.onConfirm();
    confirmModal.value.show = false;
  } catch (err) {
    showToast(err?.response?.data?.error || 'Terjadi kesalahan saat memproses tindakan', 'error');
  } finally {
    confirmModal.value.busy = false;
  }
}

const globalSearch = ref('');
const dbMs = ref(null);
const agentMessages = ref([]);
setInterval(() => { dbMs.value = dbLatency.ms; }, 2000);

// Auto real-time background sync setiap 4 detik saat berada di board
setInterval(() => {
  if (
    screen.value === 'board' &&
    activeTeam.value?.id &&
    document.visibilityState === 'visible' &&
    !showCreateIssueModal.value
  ) {
    refreshIssues();
  }
}, 4000);

const WRITE_ROLES = ['Admin', 'Developer'];
const myRole = computed(() => {
  if (!activeTeam.value || !me.value.user) return 'Viewer';
  const m = me.value.memberships?.find((mem) => mem.teamId === activeTeam.value.id);
  if (m?.role) return m.role;
  if (activeTeam.value.role) return activeTeam.value.role;
  if (activeTeam.value.yourRole) return activeTeam.value.yourRole;
  const t = me.value.teams?.find((team) => team.id === activeTeam.value.id);
  if (t?.role || t?.yourRole) return t.role || t.yourRole;
  if (activeTeam.value.createdByOid && activeTeam.value.createdByOid === me.value.user?.oid) return 'Admin';
  return 'Viewer';
});
const canWrite = computed(() => WRITE_ROLES.includes(myRole.value));

onMounted(async () => {
  // Jalur 0: public share link — /share/<token>
  if (window.location.pathname.startsWith('/share/')) {
    screen.value = 'share';
    return;
  }

  // Tidak ada mock team/mock user: state awal sepenuhnya dari SSO + database.
  // Jalur 1: sesi OAuth Google/GitHub (redirect callback backend membawa #token=...)
  const cameFromOAuth = consumeTokenFromUrl();
  if (cameFromOAuth || hasOAuthSession()) {
    try {
      await loadMe();
      return;
    } catch (err) {
      console.error('Sesi OAuth tidak valid:', err);
      clearOAuthToken();
      // lanjut ke cek MSAL / login
    }
  }
  // Jalur 2: SSO Microsoft Entra ID (MSAL)
  const account = msalInstance.getActiveAccount() || msalInstance.getAllAccounts()[0];
  if (!account) {
    screen.value = 'login';
    return;
  }
  try {
    await loadMe();
  } catch (err) {
    console.error('Gagal memuat sesi:', err);
    screen.value = 'login';
  }
});

async function loadMe() {
  const data = await JiraApiService.fetchMe();
  // Sisipkan role user per tim (dari team_memberships) ke daftar teams
  const roleByTeam = Object.fromEntries(data.memberships.map((m) => [m.teamId, m.role]));
  data.teams = data.teams.map((t) => {
    const userRole = roleByTeam[t.id] || (t.createdByOid === data.user?.oid ? 'Admin' : 'Viewer');
    return { ...t, role: userRole, yourRole: userRole };
  });
  me.value = data;
  // Refresh tetap di workspace tim terakhir (persist di localStorage)
  const lastTeamId = localStorage.getItem('jiravue_last_team');
  const lastTeam = lastTeamId && data.teams.find((t) => t.id === Number(lastTeamId));
  if (lastTeam) {
    await enterTeam(lastTeam);
    return;
  }
  screen.value = me.value.hasTeams ? 'team-select' : 'welcome';
}

async function handleSignedIn() {
  try {
    await loadMe();
  } catch (err) {
    console.error('Login gagal memuat profil:', err);
  }
}

// ---- Logout (dengan konfirmasi modal dan toast) ----
function handleRequestLogout() {
  openConfirm({
    title: 'Konfirmasi Keluar',
    message: 'Apakah Anda yakin ingin keluar dari akun JiraVue?',
    confirmText: 'Ya, Keluar',
    cancelText: 'Tidak, Batal',
    variant: 'warning',
    onConfirm: async () => {
      clearOAuthToken();
      localStorage.removeItem('jiravue_last_team');
      activeTeam.value = null;
      me.value = { user: null, teams: [], hasTeams: false };
      screen.value = 'login';
      showToast('Anda telah berhasil keluar dari akun.', 'info');
    },
  });
}

function handleLogout() {
  handleRequestLogout();
}

// Keluar dari workspace ke halaman pilih tim (refresh tidak balik otomatis)
function leaveToTeamSelect() {
  localStorage.removeItem('jiravue_last_team');
  activeTeam.value = null;
  screen.value = 'team-select';
  showToast('Beralih ke halaman pemilihan tim.', 'info');
}

async function enterTeam(team) {
  const teamWithRole = me.value.teams?.find((t) => t.id === team.id) || team;
  activeTeam.value = { ...team, ...teamWithRole };
  activeView.value = 'board';
  screen.value = 'workspace';
  localStorage.setItem('jiravue_last_team', String(team.id));
  issues.value = [];
  selectedIssue.value = null;
  try {
    const [teamIssues, teamSprints, membersRes] = await Promise.all([
      JiraApiService.fetchIssues(team.id),
      JiraApiService.fetchTeamSprints(team.id),
      JiraApiService.fetchTeamMembers(team.id),
    ]);
    issues.value = teamIssues;
    sprints.value = teamSprints;
    // Default tampilan board: sprint yang sedang active (atau backlog)
    const active = teamSprints.find((s) => s.state === 'active');
    selectedSprintId.value = active ? active.id : (teamSprints[0]?.id ?? 'backlog');
    members.value = membersRes.members;
    await loadInvitesIfAdmin();
  } catch (err) {
    console.error('Gagal memuat workspace tim:', err);
  }
}

async function loadInvitesIfAdmin() {
  if (myRole.value !== 'Admin') return;
  try {
    activeTeam.value.invites = await JiraApiService.fetchTeamInvites(activeTeam.value.id);
  } catch (err) {
    console.error('Gagal memuat invite:', err);
  }
}

// ---- Handler tim (create / join) -> langsung masuk workspace tim baru ----
const inviteBanner = ref(null);

async function handleTeamCreated(team) {
  showCreateTeamModal.value = false;
  await loadMe();
  await enterTeam(me.value.teams.find((t) => t.id === team.id) || team);
  // Backend meng-auto-generate kode invite saat tim dibuat — tampilkan langsung
  inviteBanner.value = team.defaultInviteCode || null;
}

async function copyInvite() {
  try {
    await navigator.clipboard.writeText(inviteBanner.value || '');
  } catch {
    /* clipboard diblokir browser — kode tetap terlihat di banner */
  }
}

async function handleTeamJoined(team) {
  showJoinTeamModal.value = false;
  await loadMe();
  await enterTeam(me.value.teams.find((t) => t.id === team.id) || team);
}

function handleOpenEditTeam(team) {
  editingTeam.value = team;
}

async function handleSaveTeam(payload) {
  try {
    const updated = await JiraApiService.updateTeam(payload.id, payload);
    // Update daftar teams
    me.value.teams = me.value.teams.map((t) => (t.id === updated.id ? { ...t, ...updated } : t));
    if (activeTeam.value?.id === updated.id) {
      activeTeam.value = { ...activeTeam.value, ...updated };
    }
    editingTeam.value = null;
    showToast('Detail tim berhasil diperbarui.', 'success');
  } catch (err) {
    showToast(err?.response?.data?.error || 'Gagal mengubah detail tim', 'error');
  }
}

function handleDeleteTeam(team) {
  openConfirm({
    title: `Hapus Tim "${team.name}"?`,
    message: `Apakah Anda yakin ingin menghapus tim "${team.name}" (${team.key})?\nSemua sprint, issue, dan seluruh data tim akan dihapus secara permanen.`,
    confirmText: 'Ya, Hapus Tim',
    cancelText: 'Tidak, Batal',
    variant: 'danger',
    onConfirm: async () => {
      await JiraApiService.deleteTeam(team.id);
      me.value.teams = me.value.teams.filter((t) => t.id !== team.id);
      if (activeTeam.value?.id === team.id) {
        localStorage.removeItem('jiravue_last_team');
        activeTeam.value = null;
        screen.value = me.value.teams.length ? 'team-select' : 'welcome';
      }
      showToast(`Tim "${team.name}" berhasil dihapus.`, 'success');
    },
  });
}

// ---- Handler issues ----
async function handleStatusChange({ issueKey, newStatus }) {
  if (!canWrite.value) return;
  const updated = await JiraApiService.updateIssue(activeTeam.value.id, issueKey, { status: newStatus });
  const idx = issues.value.findIndex((i) => i.key === issueKey);
  if (idx !== -1) issues.value[idx] = updated;
}

async function handleIssueUpdate(updatedPayload) {
  try {
    const updated = await JiraApiService.updateIssue(activeTeam.value.id, updatedPayload.key, updatedPayload);
    const idx = issues.value.findIndex((i) => i.key === updated.key);
    if (idx !== -1) issues.value[idx] = updated;
    selectedIssue.value = null;
    showToast(`Issue ${updated.key} berhasil diperbarui.`, 'success');
  } catch (err) {
    showToast(err?.response?.data?.error || 'Gagal memperbarui issue', 'error');
  }
}

function handleIssueCreated(createdIssue) {
  if (createdIssue && createdIssue.key) {
    // Issue sudah dibuat oleh CreateIssueModal via backend API.
    // Jangan panggil API lagi agar tidak terjadi double-create!
    const exists = issues.value.some((i) => i.key === createdIssue.key);
    if (!exists) {
      issues.value.unshift(createdIssue);
    }
    showCreateIssueModal.value = false;
    showToast(`Issue ${createdIssue.key} berhasil dibuat.`, 'success');
  }
}

function handleDeleteIssue(issueKey) {
  openConfirm({
    title: `Hapus Issue ${issueKey}?`,
    message: `Apakah Anda yakin ingin menghapus issue ${issueKey}?\nTindakan ini permanen dan tidak dapat dibatalkan.`,
    confirmText: 'Ya, Hapus Issue',
    cancelText: 'Tidak, Batal',
    variant: 'danger',
    onConfirm: async () => {
      await JiraApiService.deleteIssue(activeTeam.value.id, issueKey);
      issues.value = issues.value.filter((i) => i.key !== issueKey);
      if (selectedIssue.value?.key === issueKey) {
        selectedIssue.value = null;
      }
      showToast(`Issue ${issueKey} berhasil dihapus.`, 'success');
    },
  });
}

// ---- Sprint (Jira-lite): pilih sprint, create / start / complete / delete ----
const boardIssues = computed(() => {
  if (selectedSprintId.value === 'backlog') {
    return issues.value.filter((i) => !i.sprintId);
  }
  if (selectedSprintId.value == null) return issues.value;
  return issues.value.filter((i) => i.sprintId === Number(selectedSprintId.value));
});

function handleSelectSprint(value) {
  selectedSprintId.value = value === 'backlog' ? 'backlog' : Number(value);
}

async function handleCreateSprint() {
  try {
    const created = await JiraApiService.createSprint(activeTeam.value.id);
    sprints.value.push(created);
    selectedSprintId.value = created.id;
    showToast(`${created.name} berhasil dibuat.`, 'success');
  } catch (err) {
    showToast(err?.response?.data?.error || 'Gagal membuat sprint', 'error');
  }
}

async function handleStartSprint(sprintId) {
  try {
    const updated = await JiraApiService.startSprint(activeTeam.value.id, sprintId);
    sprints.value = sprints.value.map((s) => {
      // Aturan satu-sprint-aktif: sprint active lain turun ke future
      if (s.id === sprintId) return updated;
      return s.state === 'active' ? { ...s, state: 'future' } : s;
    });
    showToast(`${updated.name} sekarang berstatus ACTIVE.`, 'success');
  } catch (err) {
    showToast(err?.response?.data?.error || 'Gagal memulai sprint', 'error');
  }
}

function handleCompleteSprint(sprintId) {
  const targetSprint = sprints.value.find((s) => s.id === sprintId);
  const sprintName = targetSprint?.name || 'sprint ini';
  openConfirm({
    title: `Complete ${sprintName}?`,
    message: `Apakah Anda yakin ingin menyelesaikan ${sprintName}?\nIssue yang belum selesai akan otomatis dikembalikan ke Backlog.`,
    confirmText: 'Ya, Selesaikan',
    cancelText: 'Tidak, Batal',
    variant: 'info',
    onConfirm: async () => {
      const result = await JiraApiService.completeSprint(activeTeam.value.id, sprintId);
      sprints.value = sprints.value.map((s) => {
        if (s.id === sprintId) return result.completed;
        if (result.nextActive && s.id === result.nextActive.id) return result.nextActive;
        return s;
      });
      issues.value = await JiraApiService.fetchIssues(activeTeam.value.id);
      showToast(`${sprintName} berhasil diselesaikan.`, 'success');
    },
  });
}

function handleDeleteSprint(sprintId) {
  const targetSprint = sprints.value.find((s) => s.id === sprintId);
  const sprintName = targetSprint?.name || 'sprint ini';
  openConfirm({
    title: `Hapus ${sprintName}?`,
    message: `Apakah Anda yakin ingin menghapus ${sprintName}?\nIssue di dalamnya TIDAK akan terhapus dan otomatis dipindahkan ke Backlog.`,
    confirmText: 'Ya, Hapus Sprint',
    cancelText: 'Tidak, Batal',
    variant: 'warning',
    onConfirm: async () => {
      await JiraApiService.deleteSprint(activeTeam.value.id, sprintId);
      sprints.value = sprints.value.filter((s) => s.id !== sprintId);
      issues.value = await JiraApiService.fetchIssues(activeTeam.value.id);
      const active = sprints.value.find((s) => s.state === 'active');
      selectedSprintId.value = active ? active.id : 'backlog';
      showToast(`${sprintName} berhasil dihapus.`, 'success');
    },
  });
}

function handleOpenEditSprint(sprint) {
  editingSprint.value = sprint;
}

async function handleSaveSprint(payload) {
  try {
    const updated = await JiraApiService.updateSprint(activeTeam.value.id, payload.id, payload);
    sprints.value = sprints.value.map((s) => {
      if (s.id === updated.id) return updated;
      if (updated.state === 'active' && s.state === 'active') {
        return { ...s, state: 'future' };
      }
      return s;
    });
    editingSprint.value = null;
    showToast(`Sprint "${updated.name}" berhasil disimpan.`, 'success');
  } catch (err) {
    showToast(err?.response?.data?.error || 'Gagal mengubah sprint', 'error');
  }
}

// ---- Backlog & AI Agent ----
const backlogIssues = computed(() => issues.value.filter((i) => !i.sprintId));

async function refreshIssues(updatedIssue = null) {
  if (updatedIssue && updatedIssue.key) {
    const idx = issues.value.findIndex((i) => i.key === updatedIssue.key);
    if (idx !== -1) {
      issues.value[idx] = { ...issues.value[idx], ...updatedIssue };
    }
    if (selectedIssue.value && selectedIssue.value.key === updatedIssue.key) {
      selectedIssue.value = { ...selectedIssue.value, ...updatedIssue };
    }
  }
  if (!activeTeam.value?.id) return;
  try {
    const fresh = await JiraApiService.fetchIssues(activeTeam.value.id);
    issues.value = fresh;
    if (selectedIssue.value) {
      const match = fresh.find((i) => i.key === selectedIssue.value.key);
      if (match) {
        selectedIssue.value = match;
      }
    }
  } catch (err) {
    console.error('Gagal refresh issue:', err);
  }
}

async function handleAgentPrompt(prompt) {
  agentMessages.value.push({ role: 'user', text: prompt });
  agentMessages.value.push({ role: 'agent', text: 'Memproses prompt...', actions: [] });
  try {
    const res = await JiraApiService.sendAgentPrompt(activeTeam.value.id, prompt);
    const reply = res.reply || res.message || JSON.stringify(res);
    const actions = res.actions || res.executed || [];
    agentMessages.value[agentMessages.value.length - 1] = { role: 'agent', text: reply, actions };
    await refreshIssues();
  } catch (err) {
    agentMessages.value[agentMessages.value.length - 1] = {
      role: 'agent',
      text: err?.response?.data?.error || 'Gagal memproses prompt AI Agent.',
      actions: [],
    };
  }
}
</script>
