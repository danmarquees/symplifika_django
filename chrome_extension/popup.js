// Symplifika Chrome Extension - Popup JavaScript
// Handles the popup interface logic and interaction with background script

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
    this.debugMode = false;

    this.init();
  }

  setupEventListeners() {
    // Header actions
    document
      .getElementById("refreshBtn")
      .addEventListener("click", () => this.syncShortcuts());
    document
      .getElementById("settingsBtn")
      .addEventListener("click", () => this.openSettings());

    // Authentication
    document
      .getElementById("loginBtn")
      .addEventListener("click", () => this.openLoginModal());

    // Login modal
    document
      .getElementById("closeLoginModal")
      .addEventListener("click", () => this.closeLoginModal());
    document
      .getElementById("cancelLogin")
      .addEventListener("click", () => this.closeLoginModal());
    document
      .getElementById("loginForm")
      .addEventListener("submit", (e) => this.handleLogin(e));

    // Search
    document
      .getElementById("searchInput")
      .addEventListener("input", (e) => this.handleSearch(e));
    document
      .getElementById("clearSearch")
      .addEventListener("click", () => this.clearSearch());

    // Filter tabs
    document.querySelectorAll(".filter-tab").forEach((tab) => {
      tab.addEventListener("click", (e) => this.handleFilterChange(e));
    });

    // Footer actions
    document
      .getElementById("createShortcutBtn")
      .addEventListener("click", () => this.createShortcut());
    document
      .getElementById("dashboardBtn")
      .addEventListener("click", () => this.openDashboard());
    document
      .getElementById("openWebBtn")
      .addEventListener("click", () => this.openDashboard());
    document
      .getElementById("retryBtn")
      .addEventListener("click", () => this.loadInitialData());

    // Modal overlay clicks
    document.getElementById("loginModal").addEventListener("click", (e) => {
      if (e.target.id === "loginModal") {
        this.closeLoginModal();
      }
    });
  }

  async loadInitialData() {
    this.showLoading();

    try {
      // Initialize background script
      const response = await this.sendMessage({ action: "init" });

      if (response.success) {
        this.isAuthenticated = response.authenticated;

        if (this.isAuthenticated) {
          await this.loadAuthenticatedData();
        } else {
          this.showNotAuthenticated();
        }
      } else {
        throw new Error("Failed to initialize");
      }
    } catch (error) {
      console.error("Error loading initial data:", error);
      this.showError("Erro ao carregar dados", error.message);
    }
  }

  async loadAuthenticatedData() {
    try {
      // Load shortcuts
      const shortcutsResponse = await this.sendMessage({
        action: "getShortcuts",
      });
      this.shortcuts = shortcutsResponse.shortcuts || [];

      // Load stats
      const statsResponse = await this.sendMessage({ action: "getStats" });
      this.stats = statsResponse || {};

      this.updateUI();
      this.showAuthenticated();
    } catch (error) {
      console.error("Error loading authenticated data:", error);
      this.showError("Erro ao carregar dados do usuário", error.message);
    }
  }

  async syncShortcuts() {
    this.setSyncStatus("syncing", "Sincronizando...");

    try {
      const response = await this.sendMessage({ action: "syncShortcuts" });

      if (response.success) {
        this.shortcuts = [];
        await this.loadAuthenticatedData();
        this.setSyncStatus("success", "Sincronizado");
        this.showNotification("Atalhos sincronizados com sucesso", "success");
      } else {
        throw new Error("Sync failed");
      }
    } catch (error) {
      console.error("Sync error:", error);
      this.setSyncStatus("error", "Erro na sincronização");
      this.showNotification("Erro ao sincronizar atalhos", "error");
    }
  }

  updateUI() {
    this.updateStats();
    this.filterShortcuts();
    this.renderShortcuts();
  }

  updateStats() {
    const shortcutsCount = this.shortcuts.length;
    const usageCount = this.stats.today_usage_count || 0;
    const aiRemaining = this.stats.ai_requests_remaining || 0;

    document.getElementById("shortcutsCount").textContent = shortcutsCount;
    document.getElementById("usageCount").textContent = usageCount;
    document.getElementById("aiCount").textContent = aiRemaining;
  }

  filterShortcuts() {
    let filtered = [...this.shortcuts];

    // Apply search filter
    if (this.searchQuery) {
      const query = this.searchQuery.toLowerCase();
      filtered = filtered.filter(
        (shortcut) =>
          shortcut.trigger.toLowerCase().includes(query) ||
          shortcut.title.toLowerCase().includes(query) ||
          shortcut.content.toLowerCase().includes(query) ||
          (shortcut.category &&
            shortcut.category.name.toLowerCase().includes(query)),
      );
    }

    // Apply category filter
    switch (this.currentFilter) {
      case "recent":
        filtered = filtered
          .filter((shortcut) => shortcut.last_used)
          .sort((a, b) => new Date(b.last_used) - new Date(a.last_used));
        break;
      case "favorites":
        filtered = filtered
          .filter((shortcut) => shortcut.use_count > 0)
          .sort((a, b) => b.use_count - a.use_count);
        break;
      default:
        filtered.sort((a, b) => b.use_count - a.use_count);
    }

    this.filteredShortcuts = filtered;
  }

  renderShortcuts() {
    const container = document.getElementById("shortcutsList");
    const emptyState = document.getElementById("emptyState");
    const noResultsState = document.getElementById("noResultsState");

    // Clear container
    container.innerHTML = "";

    if (this.shortcuts.length === 0) {
      // No shortcuts at all
      container.style.display = "none";
      emptyState.style.display = "flex";
      noResultsState.style.display = "none";
      return;
    }

    if (this.filteredShortcuts.length === 0) {
      // No results for current filter/search
      container.style.display = "none";
      emptyState.style.display = "none";
      noResultsState.style.display = "flex";
      return;
    }

    // Show shortcuts
    container.style.display = "block";
    emptyState.style.display = "none";
    noResultsState.style.display = "none";

    this.filteredShortcuts.forEach((shortcut) => {
      const element = this.createShortcutElement(shortcut);
      container.appendChild(element);
    });
  }

  createShortcutElement(shortcut) {
    const template = document.getElementById("shortcutItemTemplate");
    const element = template.content.cloneNode(true);

    // Set data
    const item = element.querySelector(".shortcut-item");
    item.dataset.shortcutId = shortcut.id;

    // Fill content
    element.querySelector(".shortcut-trigger").textContent = shortcut.trigger;
    element.querySelector(".shortcut-title").textContent = shortcut.title;
    element.querySelector(".shortcut-preview").textContent = this.truncateText(
      shortcut.content,
      60,
    );

    // Category
    const categoryEl = element.querySelector(".shortcut-category");
    if (shortcut.category) {
      categoryEl.textContent = shortcut.category.name;
      categoryEl.style.backgroundColor = shortcut.category.color + "20";
      categoryEl.style.color = shortcut.category.color;
    } else {
      categoryEl.textContent = "Sem categoria";
    }

    // Usage count
    element.querySelector(".shortcut-usage").textContent =
      `${shortcut.use_count} usos`;

    // Type
    const typeEl = element.querySelector(".shortcut-type");
    typeEl.textContent = this.getTypeLabel(shortcut.expansion_type);
    typeEl.className = `shortcut-type ${shortcut.expansion_type}`;

    // Event listeners
    element.querySelector(".copy-btn").addEventListener("click", (e) => {
      e.stopPropagation();
      this.copyShortcut(shortcut);
    });

    element.querySelector(".use-btn").addEventListener("click", (e) => {
      e.stopPropagation();
      this.useShortcut(shortcut);
    });

    item.addEventListener("click", () => this.useShortcut(shortcut));

    return element;
  }

  getTypeLabel(type) {
    const labels = {
      static: "Texto",
      dynamic: "Dinâmico",
      ai_enhanced: "IA",
    };
    return labels[type] || type;
  }

  truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + "...";
  }

  async copyShortcut(shortcut) {
    try {
      let content = shortcut.content;

      if (
        shortcut.expansion_type === "ai_enhanced" &&
        shortcut.expanded_content
      ) {
        content = shortcut.expanded_content;
      }

      await navigator.clipboard.writeText(content);
      this.showNotification(`Atalho "${shortcut.trigger}" copiado!`, "success");
    } catch (error) {
      console.error("Copy error:", error);
      this.showNotification("Erro ao copiar atalho", "error");
    }
  }

  async useShortcut(shortcut) {
    try {
      const response = await this.sendMessage({
        action: "useShortcut",
        shortcutId: shortcut.id,
      });

      if (response.content) {
        await navigator.clipboard.writeText(response.content);
        this.showNotification(
          `Atalho "${shortcut.trigger}" usado e copiado!`,
          "success",
        );

        // Update usage count locally
        shortcut.use_count++;
        this.updateUI();
      } else {
        throw new Error("No content returned");
      }
    } catch (error) {
      console.error("Use shortcut error:", error);
      this.showNotification("Erro ao usar atalho", "error");
    }
  }

  handleSearch(event) {
    this.searchQuery = event.target.value;
    this.filterShortcuts();
    this.renderShortcuts();

    // Show/hide clear button
    const clearBtn = document.getElementById("clearSearch");
    if (this.searchQuery) {
      clearBtn.style.display = "block";
    } else {
      clearBtn.style.display = "none";
    }
  }

  clearSearch() {
    document.getElementById("searchInput").value = "";
    document.getElementById("clearSearch").style.display = "none";
    this.searchQuery = "";
    this.filterShortcuts();
    this.renderShortcuts();
  }

  handleFilterChange(event) {
    // Update active tab
    document.querySelectorAll(".filter-tab").forEach((tab) => {
      tab.classList.remove("active");
    });
    event.target.classList.add("active");

    this.currentFilter = event.target.dataset.filter;
    this.filterShortcuts();
    this.renderShortcuts();
  }

  // Authentication methods
  openLoginModal() {
    document.getElementById("loginModal").style.display = "flex";
    document.getElementById("username").focus();
  }

  closeLoginModal() {
    document.getElementById("loginModal").style.display = "none";
    document.getElementById("loginForm").reset();
  }

  async handleLogin(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const username = formData.get("username");
    const password = formData.get("password");
    const serverUrl = formData.get("serverUrl");

    const submitBtn = document.getElementById("submitLogin");
    this.setButtonLoading(submitBtn, true);

    try {
      // Set server URL
      if (serverUrl) {
        await this.sendMessage({ action: "setBaseURL", url: serverUrl });
      }

      // Attempt login
      const response = await this.sendMessage({
        action: "login",
        username,
        password,
      });

      if (response.success) {
        this.isAuthenticated = true;
        this.user = response.user;
        this.closeLoginModal();
        await this.loadAuthenticatedData();
        this.showNotification("Login realizado com sucesso!", "success");
      } else {
        throw new Error(response.error || "Login failed");
      }
    } catch (error) {
      console.error("Login error:", error);
      this.showNotification("Erro no login: " + error.message, "error");
    } finally {
      this.setButtonLoading(submitBtn, false);
    }
  }

  async logout() {
    try {
      await this.sendMessage({ action: "logout" });
      this.isAuthenticated = false;
      this.user = null;
      this.shortcuts = [];
      this.showNotAuthenticated();
      this.showNotification("Logout realizado com sucesso", "info");
    } catch (error) {
      console.error("Logout error:", error);
      this.showNotification("Erro no logout", "error");
    }
  }

  // Navigation methods
  createShortcut() {
    chrome.tabs.create({ url: "http://localhost:8000/shortcuts/" });
    window.close();
  }

  openDashboard() {
    chrome.tabs.create({ url: "http://localhost:8000/" });
    window.close();
  }

  openSettings() {
    chrome.runtime.openOptionsPage();
    window.close();
  }

  // UI State methods
  showLoading() {
    this.hideAllStates();
    document.getElementById("loadingState").style.display = "flex";
  }

  showNotAuthenticated() {
    this.hideAllStates();
    document.getElementById("notAuthenticatedState").style.display = "flex";
  }

  showAuthenticated() {
    this.hideAllStates();
    document.getElementById("authenticatedState").style.display = "flex";
  }

  showError(title, message) {
    this.hideAllStates();
    document.getElementById("errorState").style.display = "flex";
    document.getElementById("errorMessage").textContent = message;
  }

  hideAllStates() {
    document.getElementById("loadingState").style.display = "none";
    document.getElementById("notAuthenticatedState").style.display = "none";
    document.getElementById("authenticatedState").style.display = "none";
    document.getElementById("errorState").style.display = "none";
  }

  setSyncStatus(status, text) {
    const indicator = document.getElementById("syncIndicator");
    const statusText = document.getElementById("syncStatus");

    indicator.className = "sync-indicator";
    if (status !== "success") {
      indicator.classList.add(status);
    }

    statusText.textContent = text;
  }

  setButtonLoading(button, loading) {
    const textEl = button.querySelector(".btn-text");
    const spinnerEl = button.querySelector(".btn-spinner");

    if (loading) {
      button.disabled = true;
      textEl.style.display = "none";
      spinnerEl.style.display = "flex";
    } else {
      button.disabled = false;
      textEl.style.display = "inline";
      spinnerEl.style.display = "none";
    }
  }

  // Notification system
  showNotification(message, type = "info") {
    const container = document.getElementById("notificationContainer");

    const notification = document.createElement("div");
    notification.className = `notification ${type}`;
    notification.textContent = message;

    container.appendChild(notification);

    // Auto remove after 3 seconds
    setTimeout(() => {
      if (notification.parentNode) {
        container.removeChild(notification);
      }
    }, 3000);
  }

  // Communication with background script
  async sendMessage(message) {
    return new Promise((resolve, reject) => {
      chrome.runtime.sendMessage(message, (response) => {
        if (chrome.runtime.lastError) {
          reject(new Error(chrome.runtime.lastError.message));
        } else {
          resolve(response);
        }
      });
    });
  }
}

// Initialize popup when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  new SymphilikaPopup();
});

// Handle extension updates/reloads
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "shortcutsUpdated") {
    // Refresh the popup data
    window.location.reload();
  }
});

console.log("Symplifika Popup Script loaded");
