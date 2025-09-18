// Symplifika Chrome Extension - Popup JavaScript
// Conecta com os endpoints do backend Django

class SymphilikaPopup {
  constructor() {
    this.shortcuts = [];
    this.filteredShortcuts = [];
    this.currentFilter = "all";
    this.searchQuery = "";
    this.isAuthenticated = false;
    this.user = null;
    this.stats = {};
    this.serverUrl = "http://localhost:8000";
    this.authToken = null;
    this.debugMode = false;
    this._lastSearch = "";
    this._searchTimeout = null;
    this._syncInterval = null;

    this.init();
  }

  async init() {
    try {
      await this.loadSettings();
      this.setupEventListeners();
      await this.loadInitialData();
      this.startAutoSync();
    } catch (error) {
      console.error("Erro na inicialização:", error);
      this.showErrorState("Erro ao inicializar a extensão");
    }
  }

  async loadSettings() {
    return new Promise((resolve) => {
      chrome.storage.sync.get(
        ["serverUrl", "authToken", "debugMode", "syncInterval"],
        (result) => {
          this.serverUrl = result.serverUrl || "http://localhost:8000";
          this.authToken = result.authToken;
          this.debugMode = result.debugMode || false;
          this.syncInterval = result.syncInterval || 5; // minutos
          resolve();
        },
      );
    });
  }

  setupEventListeners() {
    // Search
    const searchInput = document.getElementById("searchInput");
    if (searchInput) {
      searchInput.addEventListener("input", this.handleSearch.bind(this));
    }

    // Filter buttons
    const filterBtns = document.querySelectorAll(".filter-btn");
    filterBtns.forEach((btn) => {
      btn.addEventListener("click", this.handleFilter.bind(this));
    });

    // Login form
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
      loginForm.addEventListener("submit", this.handleLogin.bind(this));
    }

    // Actions
    const syncBtn = document.getElementById("syncBtn");
    if (syncBtn) {
      syncBtn.addEventListener("click", this.syncShortcuts.bind(this));
    }

    const settingsBtn = document.getElementById("settingsBtn");
    if (settingsBtn) {
      settingsBtn.addEventListener("click", this.openSettings.bind(this));
    }

    const createBtn = document.getElementById("createBtn");
    if (createBtn) {
      createBtn.addEventListener("click", this.createShortcut.bind(this));
    }

    const dashboardBtn = document.getElementById("dashboardBtn");
    if (dashboardBtn) {
      dashboardBtn.addEventListener("click", this.openDashboard.bind(this));
    }

    // Login modal
    const loginModalBtn = document.getElementById("loginModalBtn");
    if (loginModalBtn) {
      loginModalBtn.addEventListener("click", this.openLoginModal.bind(this));
    }

    const closeModalBtn = document.getElementById("closeModalBtn");
    if (closeModalBtn) {
      closeModalBtn.addEventListener("click", this.closeLoginModal.bind(this));
    }

    // Logout
    const logoutBtn = document.getElementById("logoutBtn");
    if (logoutBtn) {
      logoutBtn.addEventListener("click", this.handleLogout.bind(this));
    }
  }

  async loadInitialData() {
    this.showLoadingState();

    try {
      if (this.authToken) {
        // Verificar se o token ainda é válido
        const userValid = await this.validateUser();
        if (userValid) {
          await this.loadUserData();
          await this.loadShortcuts();
          await this.loadStats();
          this.showMainContent();
        } else {
          this.showAuthState();
        }
      } else {
        this.showAuthState();
      }
    } catch (error) {
      console.error("Erro ao carregar dados iniciais:", error);
      this.showErrorState("Não foi possível conectar ao servidor");
    }
  }

  async validateUser() {
    try {
      const response = await this.apiRequest("GET", "/users/api/users/me/");
      if (response.ok) {
        this.user = await response.json();
        this.isAuthenticated = true;
        this.updateUserAvatar();
        return true;
      }
      return false;
    } catch (error) {
      console.error("Erro na validação do usuário:", error);
      return false;
    }
  }

  async loadUserData() {
    try {
      const response = await this.apiRequest("GET", "/users/api/users/me/");
      if (response.ok) {
        this.user = await response.json();
        this.updateUserAvatar();
      }
    } catch (error) {
      console.error("Erro ao carregar dados do usuário:", error);
    }
  }

  async loadShortcuts() {
    try {
      const response = await this.apiRequest(
        "GET",
        "/shortcuts/api/shortcuts/",
      );
      if (response.ok) {
        const data = await response.json();
        this.shortcuts = data.results || data;
        this.filteredShortcuts = [...this.shortcuts];
        this.renderShortcuts();
      }
    } catch (error) {
      console.error("Erro ao carregar atalhos:", error);
      this.shortcuts = [];
      this.filteredShortcuts = [];
      this.renderShortcuts();
    }
  }

  async loadStats() {
    try {
      // Carregar stats do usuário
      const userStatsResponse = await this.apiRequest(
        "GET",
        "/users/api/users/stats/",
      );

      if (userStatsResponse.ok) {
        const userStats = await userStatsResponse.json();
        this.stats.user = userStats;
      }

      // Carregar stats dos atalhos
      const shortcutStatsResponse = await this.apiRequest(
        "GET",
        "/shortcuts/api/shortcuts/stats/",
      );

      if (shortcutStatsResponse.ok) {
        const shortcutStats = await shortcutStatsResponse.json();
        this.stats.shortcuts = shortcutStats;
      }

      this.updateStatsDisplay();
    } catch (error) {
      console.error("Erro ao carregar estatísticas:", error);
    }
  }

  renderShortcuts() {
    const container = document.getElementById("shortcutsContainer");
    if (!container) return;

    if (this.filteredShortcuts.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <i class="fas fa-keyboard"></i>
          <p>Nenhum atalho encontrado</p>
          <button class="btn btn-primary" onclick="window.open('${this.serverUrl}/shortcuts/', '_blank')">
            Criar Primeiro Atalho
          </button>
        </div>
      `;
      return;
    }

    container.innerHTML = this.filteredShortcuts
      .map(
        (shortcut) => `
        <div class="shortcut-item" data-id="${shortcut.id}">
          <div class="shortcut-header">
            <span class="shortcut-trigger">${this.escapeHtml(shortcut.trigger)}</span>
            <span class="shortcut-category">${shortcut.category?.name || "Geral"}</span>
          </div>
          <div class="shortcut-title">${this.escapeHtml(shortcut.title)}</div>
          <div class="shortcut-content">${this.truncateText(this.escapeHtml(shortcut.content), 100)}</div>
          <div class="shortcut-footer">
            <span class="shortcut-uses">${shortcut.use_count || 0} usos</span>
            <button class="btn btn-sm btn-primary use-shortcut-btn" data-id="${shortcut.id}">
              <i class="fas fa-play"></i> Usar
            </button>
          </div>
        </div>
      `,
      )
      .join("");

    // Adicionar event listeners para os botões de usar atalho
    container.querySelectorAll(".use-shortcut-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const shortcutId = e.target.closest("button").dataset.id;
        this.useShortcut(shortcutId);
      });
    });
  }

  async syncShortcuts() {
    const syncBtn = document.getElementById("syncBtn");
    const syncIcon = syncBtn?.querySelector("i");
    const syncText = syncBtn?.querySelector(".sync-text");

    try {
      if (syncBtn) {
        syncBtn.disabled = true;
        syncIcon?.classList.add("fa-spin");
        if (syncText) syncText.textContent = "Sincronizando...";
      }

      await this.loadShortcuts();
      await this.loadStats();

      this.showNotification("Atalhos sincronizados com sucesso!", "success");
    } catch (error) {
      console.error("Erro na sincronização:", error);
      this.showNotification("Erro ao sincronizar atalhos", "error");
    } finally {
      if (syncBtn) {
        syncBtn.disabled = false;
        syncIcon?.classList.remove("fa-spin");
        if (syncText) syncText.textContent = "Sincronizar";
      }
    }
  }

  async handleLogin(event) {
    event.preventDefault();

    const submitBtn = document.getElementById("submitLogin");
    const errorDiv = document.getElementById("loginError");
    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");

    if (errorDiv) {
      errorDiv.classList.add("hidden");
      errorDiv.textContent = "";
    }

    // Validação de campos
    if (!emailInput.value.trim() || !passwordInput.value.trim()) {
      this.showLoginError("Preencha todos os campos.");
      return;
    }

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.querySelector(".btn-text").textContent = "Entrando...";
      submitBtn.querySelector(".btn-spinner").classList.remove("hidden");
    }

    const loginData = {
      username: emailInput.value.trim(), // Backend espera 'username'
      password: passwordInput.value,
    };

    try {
      const response = await fetch(`${this.serverUrl}/users/api/auth/login/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        mode: "cors",
        credentials: "omit",
        body: JSON.stringify(loginData),
      });

      const data = await response.json();

      if (response.ok && data.token) {
        this.authToken = data.token;
        this.user = data.user;

        // Salvar token no storage
        await this.saveAuthToken(data.token);

        this.closeLoginModal();
        this.showNotification("Login realizado com sucesso!", "success");
        await this.loadInitialData();
      } else {
        const errorMessage =
          data.error || data.message || "Erro ao fazer login";
        this.showLoginError(errorMessage);
      }
    } catch (error) {
      console.error("Erro no login:", error);
      this.showLoginError("Não foi possível conectar ao servidor");
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.querySelector(".btn-text").textContent = "Entrar";
        submitBtn.querySelector(".btn-spinner").classList.add("hidden");
      }
    }
  }

  async handleLogout() {
    try {
      if (this.authToken) {
        await this.apiRequest("POST", "/users/api/auth/logout/");
      }
    } catch (error) {
      console.error("Erro no logout:", error);
    }

    this.authToken = null;
    this.user = null;
    this.isAuthenticated = false;

    // Remover token do storage
    chrome.storage.sync.remove("authToken");

    this.showAuthState();
    this.showNotification("Logout realizado com sucesso!", "success");
  }

  async saveAuthToken(token) {
    return new Promise((resolve) => {
      chrome.storage.sync.set({ authToken: token }, resolve);
    });
  }

  showLoginError(message) {
    const errorDiv = document.getElementById("loginError");
    if (errorDiv) {
      errorDiv.textContent = message;
      errorDiv.classList.remove("hidden");
    }
  }

  handleSearch(event) {
    const query = event.target.value.toLowerCase().trim();
    this.searchQuery = query;

    // Debounce search
    clearTimeout(this._searchTimeout);
    this._searchTimeout = setTimeout(() => {
      this.filterShortcuts();
    }, 300);
  }

  handleFilter(event) {
    const filterValue = event.target.dataset.filter;
    this.currentFilter = filterValue;

    // Update active filter button
    document.querySelectorAll(".filter-btn").forEach((btn) => {
      btn.classList.remove("active");
    });
    event.target.classList.add("active");

    this.filterShortcuts();
  }

  filterShortcuts() {
    let filtered = [...this.shortcuts];

    // Apply search filter
    if (this.searchQuery) {
      filtered = filtered.filter(
        (shortcut) =>
          shortcut.title.toLowerCase().includes(this.searchQuery) ||
          shortcut.trigger.toLowerCase().includes(this.searchQuery) ||
          shortcut.content.toLowerCase().includes(this.searchQuery),
      );
    }

    // Apply category filter
    if (this.currentFilter !== "all") {
      filtered = filtered.filter((shortcut) => {
        if (this.currentFilter === "recent") {
          // Show shortcuts used in last 7 days
          const weekAgo = new Date();
          weekAgo.setDate(weekAgo.getDate() - 7);
          return shortcut.last_used && new Date(shortcut.last_used) > weekAgo;
        } else if (this.currentFilter === "favorites") {
          return shortcut.is_favorite;
        } else {
          return shortcut.category?.slug === this.currentFilter;
        }
      });
    }

    this.filteredShortcuts = filtered;
    this.renderShortcuts();
  }

  async useShortcut(shortcutId) {
    try {
      const shortcut = this.shortcuts.find((s) => s.id == shortcutId);
      if (!shortcut) return;

      // Registrar uso no backend
      const response = await this.apiRequest(
        "POST",
        `/shortcuts/api/shortcuts/${shortcutId}/use/`,
      );

      if (response.ok) {
        // Copiar conteúdo para clipboard
        await navigator.clipboard.writeText(shortcut.content);

        this.showNotification(
          `Atalho "${shortcut.title}" copiado para a área de transferência!`,
          "success",
        );

        // Atualizar estatísticas
        await this.loadStats();
      } else {
        throw new Error("Falha ao usar o atalho");
      }
    } catch (error) {
      console.error("Erro ao usar atalho:", error);
      this.showNotification("Erro ao usar atalho", "error");
    }
  }

  async apiRequest(method, endpoint, data = null) {
    const url = `${this.serverUrl}${endpoint}`;
    const headers = {
      "Content-Type": "application/json",
    };

    if (this.authToken) {
      headers["Authorization"] = `Token ${this.authToken}`;
    }

    const config = {
      method,
      headers,
      mode: "cors",
      credentials: "omit", // Don't send cookies for token auth
    };

    if (data && method !== "GET") {
      config.body = JSON.stringify(data);
    }

    if (this.debugMode) {
      console.log("API Request:", { method, url, headers, data });
    }

    return fetch(url, config);
  }

  updateUserAvatar() {
    const avatar = document.getElementById("userAvatar");
    if (avatar && this.user) {
      avatar.textContent = this.user.username?.charAt(0).toUpperCase() || "U";
    }

    const username = document.getElementById("userName");
    if (username && this.user) {
      username.textContent = this.user.username || "Usuário";
    }
  }

  updateStatsDisplay() {
    const totalShortcuts = document.getElementById("totalShortcuts");
    const totalUsage = document.getElementById("totalUsage");
    const todayUsage = document.getElementById("todayUsage");

    if (totalShortcuts) {
      totalShortcuts.textContent =
        this.stats.user?.total_shortcuts || this.shortcuts.length;
    }
    if (totalUsage) {
      totalUsage.textContent = this.stats.user?.total_usage || 0;
    }
    if (todayUsage) {
      todayUsage.textContent = this.stats.user?.today_usage || 0;
    }
  }

  showLoadingState() {
    this.hideAllStates();
    const loadingState = document.getElementById("loadingState");
    if (loadingState) {
      loadingState.classList.remove("hidden");
    }
  }

  showMainContent() {
    this.hideAllStates();
    const mainContent = document.getElementById("mainContent");
    if (mainContent) {
      mainContent.classList.remove("hidden");
    }
  }

  showAuthState() {
    this.hideAllStates();
    const authState = document.getElementById("authState");
    if (authState) {
      authState.classList.remove("hidden");
    }
  }

  showErrorState(message) {
    this.hideAllStates();
    const errorState = document.getElementById("errorState");
    const errorMessage = document.getElementById("errorMessage");
    if (errorState) {
      errorState.classList.remove("hidden");
    }
    if (errorMessage) {
      errorMessage.textContent = message;
    }
  }

  hideAllStates() {
    const states = ["loadingState", "mainContent", "authState", "errorState"];
    states.forEach((stateId) => {
      const element = document.getElementById(stateId);
      if (element) {
        element.classList.add("hidden");
      }
    });
  }

  openLoginModal() {
    const modal = document.getElementById("loginModal");
    if (modal) {
      modal.classList.remove("hidden");
    }
  }

  closeLoginModal() {
    const modal = document.getElementById("loginModal");
    if (modal) {
      modal.classList.add("hidden");
    }

    const form = document.getElementById("loginForm");
    if (form) {
      form.reset();
    }

    const errorDiv = document.getElementById("loginError");
    if (errorDiv) {
      errorDiv.classList.add("hidden");
    }
  }

  openSettings() {
    chrome.runtime.openOptionsPage();
  }

  createShortcut() {
    window.open(`${this.serverUrl}/shortcuts/`, "_blank");
  }

  openDashboard() {
    window.open(`${this.serverUrl}/dashboard/`, "_blank");
  }

  startAutoSync() {
    if (this._syncInterval) {
      clearInterval(this._syncInterval);
    }

    this._syncInterval = setInterval(
      () => {
        if (this.isAuthenticated) {
          this.syncShortcuts();
        }
      },
      this.syncInterval * 60 * 1000,
    );
  }

  showNotification(message, type = "info") {
    // Criar notificação temporária na interface
    const notification = document.createElement("div");
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
      <div class="notification-content">
        <i class="fas fa-${type === "success" ? "check-circle" : type === "error" ? "exclamation-circle" : "info-circle"}"></i>
        <span>${message}</span>
      </div>
    `;

    document.body.appendChild(notification);

    // Remover após 3 segundos
    setTimeout(() => {
      notification.remove();
    }, 3000);

    // Mostrar animação
    setTimeout(() => {
      notification.classList.add("show");
    }, 10);

    setTimeout(() => {
      notification.classList.remove("show");
    }, 2700);
  }

  truncateText(text, maxLength) {
    return text.length > maxLength ? text.slice(0, maxLength) + "..." : text;
  }

  escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }
}

// Inicializar popup quando o DOM estiver carregado
document.addEventListener("DOMContentLoaded", () => {
  new SymphilikaPopup();
});
