// Symplifika Chrome Extension - Options/Settings Page
// Página de configurações da extensão

class SymphilikaOptions {
  constructor() {
    this.serverUrl = "http://localhost:8000";
    this.authToken = null;
    this.isAuthenticated = false;
    this.user = null;
    this.settings = {
      autoExpand: true,
      showNotifications: true,
      syncInterval: 5, // minutos
      triggerPattern: "//",
      enableShortcuts: true,
      debugMode: false,
    };

    this.init();
  }

  async init() {
    console.log("Symplifika Options inicializado");

    try {
      await this.loadSettings();
      await this.loadUserData();
      this.setupEventListeners();
      this.renderSettings();
      this.updateUI();
    } catch (error) {
      console.error("Erro na inicialização das opções:", error);
      this.showNotification("Erro ao carregar configurações", "error");
    }
  }

  async loadSettings() {
    return new Promise((resolve) => {
      chrome.storage.sync.get(
        [
          "serverUrl",
          "authToken",
          "autoExpand",
          "showNotifications",
          "syncInterval",
          "triggerPattern",
          "enableShortcuts",
          "debugMode",
        ],
        (result) => {
          this.serverUrl = result.serverUrl || "http://localhost:8000";
          this.authToken = result.authToken || null;
          this.isAuthenticated = !!this.authToken;
          this.settings = {
            autoExpand: result.autoExpand !== false,
            showNotifications: result.showNotifications !== false,
            syncInterval: result.syncInterval || 5,
            triggerPattern: result.triggerPattern || "//",
            enableShortcuts: result.enableShortcuts !== false,
            debugMode: result.debugMode || false,
          };
          resolve();
        },
      );
    });
  }

  async loadUserData() {
    if (!this.isAuthenticated) return;

    try {
      const response = await this.apiRequest("GET", "/users/api/users/me/");
      if (response.ok) {
        this.user = await response.json();
      }
    } catch (error) {
      console.error("Erro ao carregar dados do usuário:", error);
    }
  }

  async apiRequest(method, endpoint, data = null) {
    const url = `${this.serverUrl}${endpoint}`;
    const options = {
      method,
      headers: {
        "Content-Type": "application/json",
      },
    };

    if (this.authToken) {
      options.headers["Authorization"] = `Token ${this.authToken}`;
    }

    if (data) {
      options.body = JSON.stringify(data);
    }

    return fetch(url, options);
  }

  setupEventListeners() {
    // Formulário de configurações
    const settingsForm = document.getElementById("settingsForm");
    if (settingsForm) {
      settingsForm.addEventListener(
        "submit",
        this.handleSaveSettings.bind(this),
      );
    }

    // Botão de teste de conexão
    const testConnectionBtn = document.getElementById("testConnection");
    if (testConnectionBtn) {
      testConnectionBtn.addEventListener(
        "click",
        this.testConnection.bind(this),
      );
    }

    // Botão de logout
    const logoutBtn = document.getElementById("logoutBtn");
    if (logoutBtn) {
      logoutBtn.addEventListener("click", this.handleLogout.bind(this));
    }

    // Botão de sincronização
    const syncBtn = document.getElementById("syncBtn");
    if (syncBtn) {
      syncBtn.addEventListener("click", this.syncShortcuts.bind(this));
    }

    // Reset para padrões
    const resetBtn = document.getElementById("resetSettings");
    if (resetBtn) {
      resetBtn.addEventListener("click", this.resetToDefaults.bind(this));
    }

    // Validação em tempo real da URL do servidor
    const serverUrlInput = document.getElementById("serverUrl");
    if (serverUrlInput) {
      serverUrlInput.addEventListener(
        "blur",
        this.validateServerUrl.bind(this),
      );
    }

    // Atualizar intervalo de sincronização em tempo real
    const syncIntervalInput = document.getElementById("syncInterval");
    if (syncIntervalInput) {
      syncIntervalInput.addEventListener(
        "input",
        this.updateSyncIntervalDisplay.bind(this),
      );
    }

    // Importar/Exportar configurações
    const exportBtn = document.getElementById("exportSettings");
    if (exportBtn) {
      exportBtn.addEventListener("click", this.exportSettings.bind(this));
    }

    const importBtn = document.getElementById("importSettings");
    if (importBtn) {
      importBtn.addEventListener("click", this.importSettings.bind(this));
    }

    const importFileInput = document.getElementById("importFile");
    if (importFileInput) {
      importFileInput.addEventListener(
        "change",
        this.handleImportFile.bind(this),
      );
    }
  }

  renderSettings() {
    // Preencher campos do formulário
    document.getElementById("serverUrl").value = this.serverUrl;
    document.getElementById("autoExpand").checked = this.settings.autoExpand;
    document.getElementById("showNotifications").checked =
      this.settings.showNotifications;
    document.getElementById("syncInterval").value = this.settings.syncInterval;
    document.getElementById("triggerPattern").value =
      this.settings.triggerPattern;
    document.getElementById("enableShortcuts").checked =
      this.settings.enableShortcuts;
    document.getElementById("debugMode").checked = this.settings.debugMode;

    this.updateSyncIntervalDisplay();
  }

  updateUI() {
    const authStatus = document.getElementById("authStatus");
    const userInfo = document.getElementById("userInfo");
    const logoutBtn = document.getElementById("logoutBtn");

    if (this.isAuthenticated && this.user) {
      authStatus.innerHTML = `
        <div class="status-badge status-success">
          <i class="fas fa-check-circle"></i>
          Conectado
        </div>
      `;

      userInfo.innerHTML = `
        <div class="user-card">
          <div class="user-avatar">
            ${this.user.username?.charAt(0).toUpperCase() || "U"}
          </div>
          <div class="user-details">
            <div class="user-name">${this.user.username}</div>
            <div class="user-email">${this.user.email || "N/A"}</div>
            <div class="user-plan">Plano: ${this.user.profile?.plan_type || "Free"}</div>
          </div>
        </div>
      `;

      if (logoutBtn) {
        logoutBtn.style.display = "block";
      }
    } else {
      authStatus.innerHTML = `
        <div class="status-badge status-error">
          <i class="fas fa-times-circle"></i>
          Desconectado
        </div>
      `;

      userInfo.innerHTML = `
        <div class="auth-message">
          <p>Faça login através do popup da extensão para acessar todas as funcionalidades.</p>
        </div>
      `;

      if (logoutBtn) {
        logoutBtn.style.display = "none";
      }
    }
  }

  async handleSaveSettings(event) {
    event.preventDefault();

    const saveBtn = document.getElementById("saveSettings");
    const originalText = saveBtn.textContent;

    try {
      saveBtn.textContent = "Salvando...";
      saveBtn.disabled = true;

      // Coletar dados do formulário
      const formData = new FormData(event.target);
      const newSettings = {
        serverUrl: formData.get("serverUrl").trim(),
        autoExpand: formData.has("autoExpand"),
        showNotifications: formData.has("showNotifications"),
        syncInterval: parseInt(formData.get("syncInterval")) || 5,
        triggerPattern: formData.get("triggerPattern").trim() || "//",
        enableShortcuts: formData.has("enableShortcuts"),
        debugMode: formData.has("debugMode"),
      };

      // Validar configurações
      if (!this.validateSettings(newSettings)) {
        return;
      }

      // Salvar configurações
      await this.saveSettings(newSettings);

      this.showNotification("Configurações salvas com sucesso!", "success");
    } catch (error) {
      console.error("Erro ao salvar configurações:", error);
      this.showNotification("Erro ao salvar configurações", "error");
    } finally {
      saveBtn.textContent = originalText;
      saveBtn.disabled = false;
    }
  }

  validateSettings(settings) {
    // Validar URL do servidor
    try {
      new URL(settings.serverUrl);
    } catch {
      this.showNotification("URL do servidor inválida", "error");
      return false;
    }

    // Validar intervalo de sincronização
    if (settings.syncInterval < 1 || settings.syncInterval > 60) {
      this.showNotification(
        "Intervalo de sincronização deve ser entre 1 e 60 minutos",
        "error",
      );
      return false;
    }

    // Validar padrão de trigger
    if (!settings.triggerPattern || settings.triggerPattern.length === 0) {
      this.showNotification("Padrão de ativação não pode estar vazio", "error");
      return false;
    }

    return true;
  }

  async saveSettings(newSettings) {
    return new Promise((resolve, reject) => {
      chrome.storage.sync.set(newSettings, () => {
        if (chrome.runtime.lastError) {
          reject(chrome.runtime.lastError);
        } else {
          // Atualizar configurações locais
          Object.assign(this.settings, newSettings);
          this.serverUrl = newSettings.serverUrl;
          resolve();
        }
      });
    });
  }

  async testConnection() {
    const testBtn = document.getElementById("testConnection");
    const statusIcon = testBtn.querySelector("i");
    const statusText = testBtn.querySelector(".status-text");

    try {
      testBtn.disabled = true;
      statusIcon.className = "fas fa-spinner fa-spin";
      statusText.textContent = "Testando...";

      const response = await fetch(`${this.serverUrl}/api/root/`);

      if (response.ok) {
        const data = await response.json();
        statusIcon.className = "fas fa-check-circle";
        statusText.textContent = "Conexão OK";
        this.showNotification(
          `Conectado com sucesso ao ${data.message || "servidor"}`,
          "success",
        );
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error("Erro no teste de conexão:", error);
      statusIcon.className = "fas fa-times-circle";
      statusText.textContent = "Falha na conexão";
      this.showNotification("Falha na conexão com o servidor", "error");
    } finally {
      testBtn.disabled = false;

      // Resetar ícone após 3 segundos
      setTimeout(() => {
        statusIcon.className = "fas fa-plug";
        statusText.textContent = "Testar Conexão";
      }, 3000);
    }
  }

  async validateServerUrl() {
    const input = document.getElementById("serverUrl");
    const url = input.value.trim();

    if (!url) return;

    try {
      new URL(url);
      input.classList.remove("invalid");
      input.classList.add("valid");
    } catch {
      input.classList.remove("valid");
      input.classList.add("invalid");
    }
  }

  updateSyncIntervalDisplay() {
    const input = document.getElementById("syncInterval");
    const display = document.getElementById("syncIntervalDisplay");
    const value = parseInt(input.value) || 5;

    display.textContent = value === 1 ? "1 minuto" : `${value} minutos`;
  }

  async handleLogout() {
    if (confirm("Tem certeza que deseja fazer logout?")) {
      try {
        // Notificar background script
        await chrome.runtime.sendMessage({ action: "logout" });

        // Limpar dados locais
        await chrome.storage.sync.remove("authToken");

        this.authToken = null;
        this.isAuthenticated = false;
        this.user = null;

        this.updateUI();
        this.showNotification("Logout realizado com sucesso!", "success");
      } catch (error) {
        console.error("Erro no logout:", error);
        this.showNotification("Erro ao fazer logout", "error");
      }
    }
  }

  async syncShortcuts() {
    if (!this.isAuthenticated) {
      this.showNotification("Faça login para sincronizar atalhos", "warning");
      return;
    }

    const syncBtn = document.getElementById("syncBtn");
    const syncIcon = syncBtn.querySelector("i");
    const syncText = syncBtn.querySelector(".sync-text");

    try {
      syncBtn.disabled = true;
      syncIcon.classList.add("fa-spin");
      syncText.textContent = "Sincronizando...";

      const response = await chrome.runtime.sendMessage({
        action: "syncShortcuts",
      });

      if (response && response.success) {
        this.showNotification(
          `${response.shortcuts || 0} atalhos sincronizados com sucesso!`,
          "success",
        );
      } else {
        throw new Error("Falha na sincronização");
      }
    } catch (error) {
      console.error("Erro na sincronização:", error);
      this.showNotification("Erro ao sincronizar atalhos", "error");
    } finally {
      syncBtn.disabled = false;
      syncIcon.classList.remove("fa-spin");
      syncText.textContent = "Sincronizar Agora";
    }
  }

  async resetToDefaults() {
    if (
      confirm(
        "Tem certeza que deseja restaurar as configurações padrão? Esta ação não pode ser desfeita.",
      )
    ) {
      const defaultSettings = {
        serverUrl: "http://localhost:8000",
        autoExpand: true,
        showNotifications: true,
        syncInterval: 5,
        triggerPattern: "//",
        enableShortcuts: true,
        debugMode: false,
      };

      try {
        await this.saveSettings(defaultSettings);
        this.renderSettings();
        this.showNotification(
          "Configurações restauradas para os padrões",
          "success",
        );
      } catch (error) {
        console.error("Erro ao restaurar configurações:", error);
        this.showNotification("Erro ao restaurar configurações", "error");
      }
    }
  }

  exportSettings() {
    const exportData = {
      version: "1.0.0",
      timestamp: new Date().toISOString(),
      settings: {
        ...this.settings,
        serverUrl: this.serverUrl,
      },
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: "application/json",
    });

    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `symplifika-settings-${new Date().toISOString().split("T")[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    this.showNotification("Configurações exportadas com sucesso!", "success");
  }

  importSettings() {
    document.getElementById("importFile").click();
  }

  async handleImportFile(event) {
    const file = event.target.files[0];
    if (!file) return;

    try {
      const text = await file.text();
      const importData = JSON.parse(text);

      if (!importData.settings || !importData.version) {
        throw new Error("Formato de arquivo inválido");
      }

      if (
        confirm(
          "Tem certeza que deseja importar essas configurações? As configurações atuais serão substituídas.",
        )
      ) {
        await this.saveSettings(importData.settings);
        await this.loadSettings();
        this.renderSettings();
        this.showNotification(
          "Configurações importadas com sucesso!",
          "success",
        );
      }
    } catch (error) {
      console.error("Erro ao importar configurações:", error);
      this.showNotification(
        "Erro ao importar configurações: " + error.message,
        "error",
      );
    } finally {
      event.target.value = ""; // Limpar input
    }
  }

  showNotification(message, type = "info") {
    const container = document.getElementById("notifications");
    if (!container) return;

    const notification = document.createElement("div");
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
      <div class="notification-content">
        <i class="fas fa-${
          type === "success"
            ? "check-circle"
            : type === "error"
              ? "exclamation-circle"
              : type === "warning"
                ? "exclamation-triangle"
                : "info-circle"
        }"></i>
        <span class="notification-message">${message}</span>
        <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
          <i class="fas fa-times"></i>
        </button>
      </div>
    `;

    container.appendChild(notification);

    // Auto remove após 5 segundos
    setTimeout(() => {
      if (notification.parentElement) {
        notification.remove();
      }
    }, 5000);

    // Mostrar animação
    setTimeout(() => {
      notification.classList.add("show");
    }, 10);
  }
}

// Inicializar quando o DOM estiver carregado
document.addEventListener("DOMContentLoaded", () => {
  new SymphilikaOptions();
});
