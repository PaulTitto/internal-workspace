// frontend/src/services/jiraApi.js
// Service Layer Frontend untuk berkomunikasi dengan Backend Python Flask
import axios from "axios";
import { acquireBearerToken } from "../auth/msalAuth";
import { getOAuthToken, clearOAuthToken } from "../auth/oauthSession";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_FLASK_API_URL || "http://localhost:5001/api/v1",
  headers: { "Content-Type": "application/json" },
});

// Interceptor: sisipkan Bearer token ke setiap request Flask.
// Prioritas: sesi OAuth Google/GitHub (JWT internal backend) -> MSAL Entra ID.
export const dbLatency = { ms: null };

apiClient.interceptors.request.use(async (config) => {
  const oauth = getOAuthToken();
  if (oauth) {
    config.headers.Authorization = `Bearer ${oauth}`;
    return config;
  }
  const token = await acquireBearerToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => {
    // "DB Connected (Xms)": latensi request API terakhir
    if (response.config?.metadata?.start) {
      dbLatency.ms = Math.round(performance.now() - response.config.metadata.start);
    }
    return response;
  },
  (error) => {
    // Sesi token tidak valid / kedaluwarsa (mis. SECRET_KEY dirotasi server):
    // hapus sesi OAuth dan paksa ke halaman login sekali saja (hindari loop).
    if (error?.response?.status === 401 && getOAuthToken()) {
      clearOAuthToken();
      if (!window.__jiravue_reauth) {
        window.__jiravue_reauth = true;
        alert('Sesi login kamu sudah tidak valid. Silakan login ulang.');
        window.location.reload();
      }
    }
    return Promise.reject(error);
  }
);

apiClient.interceptors.request.use((config) => {
  config.metadata = { start: performance.now() };
  return config;
});

export const JiraApiService = {
  // ---- Onboarding / current user (SSO) ----
  async fetchMe() {
    const { data } = await apiClient.get("/me");
    return data;
  },

  // ---- Teams ----
  async fetchMyTeams() {
    const { data } = await apiClient.get("/teams");
    return data;
  },
  async createTeam(payload) {
    const { data } = await apiClient.post("/teams", payload);
    return data;
  },
  async updateTeam(teamId, payload) {
    const { data } = await apiClient.put(`/teams/${teamId}`, payload);
    return data;
  },
  async deleteTeam(teamId) {
    const { data } = await apiClient.delete(`/teams/${teamId}`);
    return data;
  },
  async joinTeam(inviteCode) {
    const { data } = await apiClient.post("/teams/join", { inviteCode });
    return data;
  },

  // ---- Members & invites ----
  async fetchTeamMembers(teamId) {
    const { data } = await apiClient.get(`/teams/${teamId}/members`);
    return data;
  },
  async fetchTeamInvites(teamId) {
    const { data } = await apiClient.get(`/teams/${teamId}/invites`);
    return data;
  },
  async createInvite(teamId, payload = {}) {
    const { data } = await apiClient.post(`/teams/${teamId}/invites`, payload);
    return data;
  },

  // ---- Sprints ----
  async fetchTeamSprints(teamId) {
    const { data } = await apiClient.get(`/teams/${teamId}/sprints`);
    return data;
  },
  async createSprint(teamId, payload = {}) {
    const { data } = await apiClient.post(`/teams/${teamId}/sprints`, payload);
    return data;
  },
  async startSprint(teamId, sprintId) {
    const { data } = await apiClient.put(`/teams/${teamId}/sprints/${sprintId}`, { state: 'active' });
    return data;
  },
  async completeSprint(teamId, sprintId) {
    const { data } = await apiClient.post(`/teams/${teamId}/sprints/${sprintId}/complete`);
    return data;
  },
  async updateSprint(teamId, sprintId, payload) {
    const { data } = await apiClient.put(`/teams/${teamId}/sprints/${sprintId}`, payload);
    return data;
  },
  async deleteSprint(teamId, sprintId) {
    const { data } = await apiClient.delete(`/teams/${teamId}/sprints/${sprintId}`);
    return data;
  },
  async seedTeam(teamId) {
    const { data } = await apiClient.post(`/teams/${teamId}/seed`);
    return data;
  },
  async exportTeam(teamId) {
    const { data } = await apiClient.get(`/teams/${teamId}/export`);
    return data;
  },

  // ---- Issues (team-scoped) ----
  async fetchIssues(teamId, params = {}) {
    const { data } = await apiClient.get(`/teams/${teamId}/issues`, { params });
    return data;
  },
  async createIssue(teamId, payload) {
    const { data } = await apiClient.post(`/teams/${teamId}/issues`, payload);
    return data;
  },
  async updateIssue(teamId, issueKey, payload) {
    const { data } = await apiClient.put(
      `/teams/${teamId}/issues/${issueKey}`,
      payload
    );
    return data;
  },
  async deleteIssue(teamId, issueKey) {
    await apiClient.delete(`/teams/${teamId}/issues/${issueKey}`);
  },
  async addSubtask(teamId, issueKey, title) {
    const { data } = await apiClient.post(
      `/teams/${teamId}/issues/${issueKey}/subtasks`,
      { title }
    );
    return data;
  },
  async toggleSubtask(teamId, issueKey, subtaskId, done) {
    const { data } = await apiClient.patch(
      `/teams/${teamId}/issues/${issueKey}/subtasks/${subtaskId}`,
      { done }
    );
    return data;
  },
  async deleteSubtask(teamId, issueKey, subtaskId) {
    const { data } = await apiClient.delete(
      `/teams/${teamId}/issues/${issueKey}/subtasks/${subtaskId}`
    );
    return data;
  },
  async addComment(teamId, issueKey, body) {
    const { data } = await apiClient.post(
      `/teams/${teamId}/issues/${issueKey}/comments`,
      { body }
    );
    return data;
  },

  // ---- AI Agent (team-scoped) ----
  async sendAgentPrompt(teamId, prompt) {
    const { data } = await apiClient.post("/agent/prompt", { teamId, prompt });
    return data;
  },

  // ---- Share board (read-only link) ----
  async fetchTeamShareToken(teamId, regenerate = false) {
    const { data } = await apiClient.post(`/teams/${teamId}/share-token`, { regenerate });
    return data;
  },
  async createShareToken(teamId, payload = {}) {
    const { data } = await apiClient.post(`/teams/${teamId}/share-token`, payload);
    return data;
  },
  async fetchPublicShare(token) {
    // Public endpoint — no auth header needed; use a plain axios call
    const baseURL = import.meta.env.VITE_FLASK_API_URL || "http://localhost:5001/api/v1";
    const { data } = await apiClient.get(`/share/${token}`);
    return data;
  },

  // ---- Email OTP Passwordless Auth ----
  async sendOtp(email) {
    const { data } = await apiClient.post("/auth/otp/send", { email });
    return data;
  },
  async verifyOtp(email, otp) {
    const { data } = await apiClient.post("/auth/otp/verify", { email, otp });
    return data;
  },
};
