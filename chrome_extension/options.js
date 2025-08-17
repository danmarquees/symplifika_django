// Symplifika Chrome Extension - Options Page JavaScript
// Handles settings configuration and account management

class SymphilikaOptions {
  constructor() {
    this.settings = {
      serverUrl: "http://localhost:8000",
      apiTimeout: 30,
      extensionEnabled: true,
      autoExpand: true,
      showNotifications: true,
      soundEffects: false,
      triggerDelay: 100,
      syncInterval: 30,
      debugMode: false,
      betaFeatures: false,
    };

    this.user = null;
    this.stats = {};
    this.isAuthenticated = false;

    this.init();
  }

  async init() {
    console.log("Symplifika Options page initializing...");

    // Setup event listeners
    this.setupEventListeners();

    // Load settings
    await this.loadSettings();

    // Load user data
    await this.loadUserData();

    // Update UI
    this.updateUI();

    // Test connection
    this.testConnection();
  }

  setupEventListeners() {
    // Save button
    document
      .getElementById("saveBtn")
      .addEventListener("click", () => this.saveSettings());

    // Connection test
    document
      .getElementById("testConnectionBtn")
      .addEventListener("click", () => this.testConnection());

    // Account actions
    document
      .getElementById("openLoginBtn")
      .addEventListener("click", () => this.openLogin());
    document
      .getElementById("logoutBtn")
      .addEventListener("click", () => this.logout());

    // Advanced actions
    document
      .getElementById("clearCacheBtn")
      .addEventListener("click", () => this.clearCache());
    document
      .getElementById("exportSettingsBtn")
      .addEventListener("click", () => this.exportSettings());
    document
      .getElementById("importSettingsBtn")
      .addEventListener("click", () => this.importSettings());

    // File input for import
    document
      .getElementById("importFileInput")
      .addEventListener("change", (e) => this.handleFileImport(e));

    // Form inputs
    document.getElementById("serverUrl").addEventListener("change", (e) => {
      this.settings.serverUrl = e.target.value;
    });

    document.getElementById("apiTimeout").addEventListener("change", (e) => {
      this.settings.apiTimeout = parseInt(e.target.value);
    });

    document
      .getElementById("extensionEnabled")
      .addEventListener("change", (e) => {
        this.settings.extensionEnabled = e.target.checked;
      });

    document.getElementById("autoExpand").addEventListener("change", (e) => {
      this.settings.autoExpand = e.target.checked;
    });

    document
      .getElementById("showNotifications")
      .addEventListener("change", (e) => {
        this.settings.showNotifications = e.target.checked;
      });

    document.getElementById("soundEffects").addEventListener("change", (e) => {
      this.settings.soundEffects = e.target.checked;
    });

    document.getElementById("debugMode").addEventListener("change", (e) => {
      this.settings.debugMode = e.target.checked;
    });

    document.getElementById("betaFeatures").addEventListener("change", (e) => {
      this.settings.betaFeatures = e.target.checked;
    });

    // Range inputs
    document.getElementById("triggerDelay").addEventListener("input", (e) => {
      this.settings.triggerDelay = parseInt(e.target.value);
      document.getElementById("triggerDelayValue").textContent = e.target.value;
    });

    document.getElementById("syncInterval").addEventListener("input", (e) => {
      this.settings.syncInterval = parseInt(e.target.value);
      document.getElementById("syncIntervalValue").textContent = e.target.value;
    });
  }

  async loadSettings() {
    try {
      const stored = await chrome.storage.local.get("settings");
      if (stored.settings) {
        this.settings = { ...this.settings, ...stored.settings };
      }
    } catch (error) {
      console.error("Error loading settings:", error);
      this.showToast("Erro ao carregar configurações", "error");
    }
  }

  async saveSettings() {
    const saveBtn = document.getElementById("saveBtn");
    this.setButtonLoading(saveBtn, true);

    try {
      // Save to local storage
      await chrome.storage.local.set({ settings: this.settings });

      // Send to background script
      await this.sendMessage({
        action: "updateSettings",
        settings: this.settings,
      });

      this.showToast("Configurações salvas com sucesso!", "success");
    } catch (error) {
      console.error("Error saving settings:", error);
      this.showToast("Erro ao salvar configurações", "error");
    } finally {
      this.setButtonLoading(saveBtn, false);
    }
  }

  async loadUserData() {
    try {
      const response = await this.sendMessage({ action: "init" });

      if (response && response.authenticated) {
        this.isAuthenticated = true;

        // Load user stats
        const statsResponse = await this.sendMessage({ action: "getStats" });
        if (statsResponse && statsResponse.authenticated) {
          this.stats = statsResponse;
        }

        // Load user info from storage
        const stored = await chrome.storage.local.get("user");
        if (stored.user) {
          this.user = stored.user;
        }
      } else {
        this.isAuthenticated = false;
      }
    } catch (error) {
      console.error("Error loading user data:", error);
      this.isAuthenticated = false;
    }
  }

  updateUI() {
    // Update form values
    document.getElementById("serverUrl").value = this.settings.serverUrl;
    document.getElementById("apiTimeout").value = this.settings.apiTimeout;
    document.getElementById("extensionEnabled").checked =
      this.settings.extensionEnabled;
    document.getElementById("autoExpand").checked = this.settings.autoExpand;
    document.getElementById("showNotifications").checked =
      this.settings.showNotifications;
    document.getElementById("soundEffects").checked =
      this.settings.soundEffects;
    document.getElementById("debugMode").checked = this.settings.debugMode;
    document.getElementById("betaFeatures").checked =
      this.settings.betaFeatures;

    // Range inputs
    document.getElementById("triggerDelay").value = this.settings.triggerDelay;
    document.getElementById("triggerDelayValue").textContent =
      this.settings.triggerDelay;
    document.getElementById("syncInterval").value = this.settings.syncInterval;
    document.getElementById("syncIntervalValue").textContent =
      this.settings.syncInterval;

    // Update account section
    if (this.isAuthenticated && this.user) {
      this.showAccountInfo();
    } else {
      this.showNotLoggedIn();
    }

    // Update extension version
    const manifest = chrome.runtime.getManifest();
    document.getElementById("extensionVersion").textContent = manifest.version;
  }

  showAccountInfo() {
    document.getElementById("accountInfo").style.display = "block";
    document.getElementById("notLoggedIn").style.display = "none";

    // User info
    document.getElementById("userName").textContent =
      this.user.username || "--";
    document.getElementById("userEmail").textContent = this.user.email || "--";

    // User plan
    const planEl = document.getElementById("userPlan");
    const plan = this.user.profile?.plan || "free";
    planEl.textContent = this.getPlanLabel(plan);
    planEl.className = `user-plan ${plan}`;

    // User avatar
    const avatarEl = document.getElementById("userAvatar");
    const initials = this.user.username
      ? this.user.username.substring(0, 2).toUpperCase()
      : "??";
    avatarEl.textContent = initials;

    // Stats
    document.getElementById("totalShortcuts").textContent =
      this.stats.total_shortcuts || "--";
    document.getElementById("totalUsage").textContent =
      this.stats.total_usage_count || "--";
    document.getElementById("aiUsage").textContent =
      this.stats.ai_requests_used || "--";
  }

  showNotLoggedIn() {
    document.getElementById("accountInfo").style.display = "none";
    document.getElementById("notLoggedIn").style.display = "block";
  }

  getPlanLabel(plan) {
    const labels = {
      free: "Gratuito",
      premium: "Premium",
      enterprise: "Enterprise",
    };
    return labels[plan] || plan;
  }

  async testConnection() {
    const statusDot = document.getElementById("connectionDot");
    const statusText = document.getElementById("connectionStatus");
    const testBtn = document.getElementById("testConnectionBtn");

    // Set checking state
    statusDot.className = "status-dot checking";
    statusText.textContent = "Testando conexão...";
    this.setButtonLoading(testBtn, true);

    try {
      // Prefer a user endpoint that always exists and does not require authentication for health check
      const response = await fetch(
        `${this.settings.serverUrl}/users/api/users/me/`,
        {
          method: "GET",
          // timeout: this.settings.apiTimeout * 1000 // fetch does not support timeout natively
        },
      );

      if (response.ok) {
        statusDot.className = "status-dot connected";
        statusText.textContent = "Conectado";
        this.showToast("Conexão estabelecida com sucesso!", "success");
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error("Connection test failed:", error);
      statusDot.className = "status-dot disconnected";
      statusText.textContent = "Falha na conexão";
      this.showToast("Erro na conexão: " + error.message, "error");
    } finally {
      this.setButtonLoading(testBtn, false);
    }
  }

  openLogin() {
    chrome.tabs.create({
      url: `${this.settings.serverUrl.replace(/\/$/, "")}/users/auth/login/`,
    });
  }

  async logout() {
    try {
      await this.sendMessage({ action: "logout" });
      this.isAuthenticated = false;
      this.user = null;
      this.stats = {};
      this.updateUI();
      this.showToast("Logout realizado com sucesso!", "info");
    } catch (error) {
      console.error("Logout error:", error);
      this.showToast("Erro no logout", "error");
    }
  }

  async clearCache() {
    const clearBtn = document.getElementById("clearCacheBtn");
    this.setButtonLoading(clearBtn, true);

    try {
      // Clear extension storage
      await chrome.storage.local.clear();

      // Reset settings to defaults
      this.settings = {
        serverUrl: "http://localhost:8000",
        apiTimeout: 30,
        extensionEnabled: true,
        autoExpand: true,
        showNotifications: true,
        soundEffects: false,
        triggerDelay: 100,
        syncInterval: 30,
        debugMode: false,
        betaFeatures: false,
      };

      // Reset authentication
      this.isAuthenticated = false;
      this.user = null;
      this.stats = {};

      // Update UI
      this.updateUI();

      this.showToast("Cache limpo com sucesso!", "success");
    } catch (error) {
      console.error("Clear cache error:", error);
      this.showToast("Erro ao limpar cache", "error");
    } finally {
      this.setButtonLoading(clearBtn, false);
    }
  }

  async exportSettings() {
    try {
      const exportData = {
        version: "1.0.0",
        timestamp: new Date().toISOString(),
        settings: this.settings,
        user: this.user
          ? {
              username: this.user.username,
              email: this.user.email,
            }
          : null,
      };

      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: "application/json",
      });

      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `symplifika-settings-${new Date().toISOString().split("T")[0]}.json`;
      a.click();

      URL.revokeObjectURL(url);
      this.showToast("Configurações exportadas com sucesso!", "success");
    } catch (error) {
      console.error("Export error:", error);
      this.showToast("Erro ao exportar configurações", "error");
    }
  }

  importSettings() {
    document.getElementById("importFileInput").click();
  }

  async handleFileImport(event) {
    const file = event.target.files[0];
    if (!file) return;

    try {
      const text = await file.text();
      const importData = JSON.parse(text);

      // Validate import data
      if (!importData.version || !importData.settings) {
        throw new Error("Arquivo de configuração inválido");
      }

      // Merge settings
      this.settings = { ...this.settings, ...importData.settings };

      // Update UI
      this.updateUI();

      // Auto-save
      await this.saveSettings();

      this.showToast("Configurações importadas com sucesso!", "success");
    } catch (error) {
      console.error("Import error:", error);
      this.showToast(
        "Erro ao importar configurações: " + error.message,
        "error",
      );
    }

    // Clear file input
    event.target.value = "";
  }

  // Utility methods
  setButtonLoading(button, loading) {
    if (loading) {
      button.disabled = true;
      button.innerHTML = `
        <div class="spinner"></div>
        Carregando...
      `;
    } else {
      button.disabled = false;
      // Restore original content
      const originalContent = button.dataset.originalContent;
      if (originalContent) {
        button.innerHTML = originalContent;
      } else {
        // Find original content from button ID
        const btnTexts = {
          saveBtn:
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17,21 17,13 7,13 7,21"/><polyline points="7,3 7,8 15,8"/></svg>Salvar',
          testConnectionBtn: "Testar Conexão",
          clearCacheBtn:
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>Limpar Cache',
        };
        button.innerHTML = btnTexts[button.id] || "Ação";
      }
    }
  }

  showToast(message, type = "info") {
    const container = document.getElementById("toastContainer");

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;

    const icons = {
      success: "✓",
      error: "✗",
      warning: "⚠",
      info: "ℹ",
    };

    toast.innerHTML = `
      <div class="toast-content">
        <div class="toast-icon">${icons[type] || icons.info}</div>
        <div class="toast-message">${message}</div>
        <button class="toast-close">&times;</button>
      </div>
    `;

    // Close button
    toast.querySelector(".toast-close").addEventListener("click", () => {
      container.removeChild(toast);
    });

    container.appendChild(toast);

    // Auto remove after 5 seconds
    setTimeout(() => {
      if (toast.parentNode) {
        container.removeChild(toast);
      }
    }, 5000);
  }

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

// Initialize options page when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  new SymphilikaOptions();
});

// Handle messages from other parts of the extension
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "settingsUpdated") {
    // Reload page to reflect changes
    window.location.reload();
  }
});

// Banner de debugMode
document.addEventListener("DOMContentLoaded", () => {
  chrome.storage.local.get("settings", (result) => {
    const settings = result.settings || {};
    if (settings.debugMode) {
      const banner = document.createElement("div");
      banner.style.position = "fixed";
      banner.style.top = "0";
      banner.style.left = "0";
      banner.style.right = "0";
      banner.style.background = "#ffc107";
      banner.style.color = "#222";
      banner.style.fontWeight = "bold";
      banner.style.textAlign = "center";
      banner.style.zIndex = "9999";
      banner.style.padding = "6px 0";
      banner.textContent = "⚡ MODO DEBUG ATIVO";
      document.body.appendChild(banner);
      // Ajusta o topo do header para não sobrepor
      const header = document.querySelector(".options-header");
      if (header) header.style.marginTop = "32px";
    }
  });
});

console.log("Symplifika Options Script loaded");
