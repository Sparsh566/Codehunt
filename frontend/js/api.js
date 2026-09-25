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

  // Admin Console Operations
  async getAdminStats() {
    return this.request("/api/admin/stats");
  },

  async getAdminScenarios() {
    return this.request("/api/admin/scenarios");
  },

  async createAdminScenario(payload) {
    return this.request("/api/admin/scenarios", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },

  async toggleAdminScenario(id) {
    return this.request(`/api/admin/scenarios/${id}/toggle`, {
      method: "POST"
    });
  },

  toggleUserDropdown(event) {
    if (event) event.stopPropagation();
    const menu = document.getElementById("userDropdownMenu");
    const arrow = document.getElementById("userDropdownArrow");
    if (!menu) return;
    const isVisible = menu.style.display === "block";
    menu.style.display = isVisible ? "none" : "block";
    if (arrow) arrow.style.transform = isVisible ? "rotate(0deg)" : "rotate(180deg)";
  },

  closeUserDropdown() {
    const menu = document.getElementById("userDropdownMenu");
    const arrow = document.getElementById("userDropdownArrow");
    if (menu) menu.style.display = "none";
    if (arrow) arrow.style.transform = "rotate(0deg)";
  },

  // UI Helper: sync navbar with user status
  syncNavbar() {
    const user = this.getUser();
    const authContainer = document.getElementById("navAuthContainer");
    if (!authContainer) return;

    if (user) {
      const adminItem = (user.is_admin || user.role === 'admin') 
        ? `<a href="admin.html" class="user-dropdown-item" style="color:var(--cyan-glow);"><span>⚙️</span> Operations Console</a>` 
        : '';

      authContainer.innerHTML = `
        <div class="user-dropdown-wrapper">
          <button class="user-badge-btn" id="userBadgeBtn" onclick="ApiClient.toggleUserDropdown(event)">
            <span>⚓</span>
            <span class="username">${user.username}</span>
            <span class="user-xp">${user.xp || 0} XP (Lvl ${user.level || 1})</span>
            <span id="userDropdownArrow" style="font-size:0.65rem; transition:transform 0.2s ease;">▼</span>
          </button>
          <div class="user-dropdown-menu" id="userDropdownMenu" style="display:none;">
            <div class="user-dropdown-header">
              <div style="font-weight:700; color:#fff; font-size:0.95rem;">${user.username}</div>
              <div style="font-size:0.75rem; color:var(--cyan-glow); text-transform:uppercase;">${(user.role || 'Learner').replace('_', ' ')}</div>
            </div>
            <div class="user-dropdown-divider"></div>
            <a href="profile.html" class="user-dropdown-item">
              <span>📊</span> Analytics & Badges
            </a>
            ${adminItem}
            <div class="user-dropdown-divider"></div>
            <button class="user-dropdown-item user-dropdown-logout" onclick="ApiClient.logout()">
              <span>🚪</span> Sign Out / Logout
            </button>
          </div>
        </div>
      `;
    } else {
      authContainer.innerHTML = `
        <a href="login.html" class="btn-nav-auth" style="text-decoration:none; display:inline-block;">Sign In / Join</a>
      `;
    }
  },

  initAccessibility() {
    const isHighContrast = localStorage.getItem("a11y_high_contrast") === "true";
    const isLargeText = localStorage.getItem("a11y_large_text") === "true";

    if (isHighContrast) document.body.classList.add("high-contrast");
    if (isLargeText) document.body.classList.add("large-text");

    const bar = document.createElement("div");
    bar.className = "a11y-toolbar";
    bar.innerHTML = `
      <span style="font-size:0.72rem; color:var(--text-muted); font-weight:700;">A11Y:</span>
      <button class="a11y-btn ${isHighContrast ? 'active' : ''}" id="btnA11yContrast" title="Toggle High Contrast">Contrast</button>
      <button class="a11y-btn ${isLargeText ? 'active' : ''}" id="btnA11yFont" title="Toggle Larger Font">Font +</button>
    `;
    document.body.appendChild(bar);

    document.getElementById("btnA11yContrast").addEventListener("click", () => {
      const active = document.body.classList.toggle("high-contrast");
      localStorage.setItem("a11y_high_contrast", active);
      document.getElementById("btnA11yContrast").classList.toggle("active", active);
    });

    document.getElementById("btnA11yFont").addEventListener("click", () => {
      const active = document.body.classList.toggle("large-text");
      localStorage.setItem("a11y_large_text", active);
      document.getElementById("btnA11yFont").classList.toggle("active", active);
    });
  }
};

window.ApiClient = ApiClient;
document.addEventListener("DOMContentLoaded", () => {
  ApiClient.syncNavbar();
  ApiClient.initAccessibility();

  document.addEventListener("click", (e) => {
    const wrapper = document.querySelector(".user-dropdown-wrapper");
    if (wrapper && !wrapper.contains(e.target)) {
      ApiClient.closeUserDropdown();
    }
  });
});

