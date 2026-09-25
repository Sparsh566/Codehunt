/**
 * Codehunt v2 - Unified API Client
 * Connects frontend directly to FastAPI backend with JWT session handling.
 */

const API_BASE = window.location.origin.includes(":8000") 
  ? window.location.origin 
  : "http://127.0.0.1:8000";

const ApiClient = {
  getToken() {
    return localStorage.getItem("codehunt_token");
  },

  setToken(token) {
    if (token) localStorage.setItem("codehunt_token", token);
    else localStorage.removeItem("codehunt_token");
  },

  getUser() {
    try {
      const u = localStorage.getItem("codehunt_user");
      return u ? JSON.parse(u) : null;
    } catch {
      return null;
    }
  },

  setUser(user) {
    if (user) localStorage.setItem("codehunt_user", JSON.stringify(user));
    else localStorage.removeItem("codehunt_user");
  },

  getAuthHeaders() {
    const headers = { "Content-Type": "application/json" };
    const token = this.getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
    return headers;
  },

  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const headers = { ...this.getAuthHeaders(), ...(options.headers || {}) };
    
    try {
      const resp = await fetch(url, { ...options, headers });
      if (resp.status === 401) {
        // Token expired or invalid
        this.setToken(null);
        this.setUser(null);
      }
      const data = await resp.json();
      if (!resp.ok) {
        throw new Error(data.detail || `Request failed with status ${resp.status}`);
      }
      return data;
    } catch (err) {
      console.error(`API Error on ${endpoint}:`, err);
      throw err;
    }
  },

  // Auth Endpoints
  async register(username, password, email = null, role = "learner") {
    const res = await this.request("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ username, password, email, role })
    });
    this.setToken(res.access_token);
    this.setUser(res.user);
    return res;
  },

  async login(username, password) {
    const res = await this.request("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password })
    });
    this.setToken(res.access_token);
    this.setUser(res.user);
    return res;
  },

  async getMe() {
    const user = await this.request("/api/auth/me");
    this.setUser(user);
    return user;
  },

  logout() {
    this.setToken(null);
    this.setUser(null);
    window.location.reload();
  },

  // Learn Mode
  async getLearnQuestions() {
    return this.request("/api/learn/questions");
  },

  async submitQuiz(answers) {
    return this.request("/api/learn/submit", {
      method: "POST",
      body: JSON.stringify({ answers })
    });
  },

  // Play Mode Scenarios & Telemetry
  async getScenarios(role = null) {
    const q = role ? `?role=${encodeURIComponent(role)}` : "";
    return this.request(`/api/scenarios${q}`);
  },

  async getScenario(code) {
    return this.request(`/api/scenarios/${encodeURIComponent(code)}`);
  },

  async getTelemetry(stationId = "STN-VERAVAL") {
    return this.request(`/api/scenarios/telemetry/station/${encodeURIComponent(stationId)}`);
  },

  async listStations() {
    return this.request("/api/scenarios/telemetry/stations");
  },

  // Decision & Engine
  async evaluateDecision(scenarioCode, chosenOptionId) {
    return this.request("/api/decisions/evaluate", {
      method: "POST",
      body: JSON.stringify({
        scenario_code: scenarioCode,
        chosen_option_id: chosenOptionId
      })
    });
  },

  async explainDecision(scenarioCode, chosenOptionId, language = "en") {
    return this.request("/api/decisions/explain", {
      method: "POST",
      body: JSON.stringify({
        scenario_code: scenarioCode,
        chosen_option_id: chosenOptionId,
        language
      })
    });
  },

  async getLearnMore(scenarioCode) {
    return this.request(`/api/decisions/learn-more?scenario_code=${encodeURIComponent(scenarioCode)}`);
  },

  // Leaderboard
  async getLeaderboard(role = null) {
    const q = role ? `?role=${encodeURIComponent(role)}` : "";
    return this.request(`/api/leaderboard${q}`);
  },

  async getMyRank() {
    return this.request("/api/leaderboard/me");
  },

  // Analytics & Gamification
  async getAnalyticsProfile() {
    return this.request("/api/analytics/profile");
  },

  async getBadges() {
    return this.request("/api/analytics/badges");
  },

  // UI Helper: sync navbar with user status
  syncNavbar() {
    const user = this.getUser();
    const authContainer = document.getElementById("navAuthContainer");
    if (!authContainer) return;

    if (user) {
      authContainer.innerHTML = `
        <a href="profile.html" class="user-badge" style="text-decoration:none; cursor:pointer;" title="View Analytics & Mastery Profile">
          <span>⚓</span>
          <span class="username">${user.username}</span>
          <span class="user-xp">${user.xp || 0} XP (Lvl ${user.level || 1})</span>
        </a>
        <button class="btn-nav-auth" style="background: rgba(239,68,68,0.2); color:#fca5a5; border:1px solid #ef4444;" onclick="ApiClient.logout()">Logout</button>
      `;
    } else {
      authContainer.innerHTML = `
        <a href="login.html" class="btn-nav-auth" style="text-decoration:none; display:inline-block;">Sign In / Join</a>
      `;
    }
  }
};

window.ApiClient = ApiClient;
document.addEventListener("DOMContentLoaded", () => {
  ApiClient.syncNavbar();
});
