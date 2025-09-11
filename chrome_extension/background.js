// Background Service Worker para Symplifika Chrome Extension
// Gerencia comunicação com a API, armazenamento e eventos da extensão

class SymphilikaAPI {
  constructor() {
    this.baseURL = "http://localhost:8000";
    this.token = null;
    this.shortcuts = [];
    this.lastSync = null;
  }

  async init() {
    const stored = await chrome.storage.local.get([
      "token",
      "baseURL",
      "shortcuts",
      "lastSync",
    ]);
    this.token = stored.token || null;
    this.baseURL = stored.baseURL || "http://localhost:8000";
    this.shortcuts = stored.shortcuts || [];
    this.lastSync = stored.lastSync || null;
  }

  async setBaseURL(url) {
    this.baseURL = url;
    await chrome.storage.local.set({ baseURL: url });
  }

  async login(username, password) {
    try {
      const response = await fetch(`${this.baseURL}/users/auth/login/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Login failed");
      }

      const data = await response.json();
      this.token = data.token;

      await chrome.storage.local.set({
        token: this.token,
        user: data.user,
      });

      // Sync shortcuts after login
      await this.syncShortcuts();

      return { success: true, user: data.user };
    } catch (error) {
      console.error("Login error:", error);
      return { success: false, error: error.message };
    }
  }

  async logout() {
    try {
      if (this.token) {
        await fetch(`${this.baseURL}/users/auth/logout/`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${this.token}`,
            "Content-Type": "application/json",
          },
        });
      }
    } catch (error) {
      console.error("Logout error:", error);
    }

    this.token = null;
    this.shortcuts = [];
    this.lastSync = null;

    await chrome.storage.local.clear();
  }

  async syncShortcuts() {
    if (!this.token) return false;

    try {
      const response = await fetch(`${this.baseURL}/shortcuts/api/shortcuts/`, {
        headers: {
          Authorization: `Bearer ${this.token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Failed to sync shortcuts");
      }

      const data = await response.json();
      this.shortcuts = data.results || [];
      this.lastSync = new Date().toISOString();

      await chrome.storage.local.set({
        shortcuts: this.shortcuts,
        lastSync: this.lastSync,
      });

      return true;
    } catch (error) {
      console.error("Sync error:", error);
      return false;
    }
  }

  async useShortcut(shortcutId, variables = {}) {
    if (!this.token) return null;

    try {
      const response = await fetch(
        `${this.baseURL}/shortcuts/api/shortcuts/${shortcutId}/use/`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${this.token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ variables }),
        },
      );

      if (!response.ok) {
        throw new Error("Failed to use shortcut");
      }

      const data = await response.json();
      return data.expanded_content || data.content;
    } catch (error) {
      console.error("Use shortcut error:", error);
      return null;
    }
  }

  async searchShortcuts(query) {
    if (!this.token) return [];

    try {
      const response = await fetch(`${this.baseURL}/shortcuts/api/shortcuts/search/`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${this.token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error("Failed to search shortcuts");
      }

      const data = await response.json();
      return data.results || [];
    } catch (error) {
      console.error("Search error:", error);
      return [];
    }
  }

  async getCategories() {
    if (!this.token) return [];

    try {
      const response = await fetch(`${this.baseURL}/shortcuts/api/categories/`, {
        headers: {
          Authorization: `Bearer ${this.token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Failed to get categories");
      }

      const data = await response.json();
      return data.results || [];
    } catch (error) {
      console.error("Get categories error:", error);
      return [];
    }
  }

  async getMostUsedShortcuts() {
    if (!this.token) return [];

    try {
      const response = await fetch(`${this.baseURL}/shortcuts/api/shortcuts/most-used/`, {
        headers: {
          Authorization: `Bearer ${this.token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Failed to get most used shortcuts");
      }

      const data = await response.json();
      return data.results || [];
    } catch (error) {
      console.error("Get most used shortcuts error:", error);
      return [];
    }
  }

  async getShortcutStats() {
    if (!this.token) return {};

    try {
      const response = await fetch(`${this.baseURL}/shortcuts/api/shortcuts/stats/`, {
        headers: {
          Authorization: `Bearer ${this.token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Failed to get shortcut stats");
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Get shortcut stats error:", error);
      return {};
    }
  }

  async getUserStats() {
    if (!this.token) return {};

    try {
      const response = await fetch(`${this.baseURL}/users/api/users/stats/`, {
        headers: {
          Authorization: `Bearer ${this.token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Failed to get user stats");
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Get user stats error:", error);
      return {};
    }
  }

  async getUserProfile() {
    if (!this.token) return null;

    try {
      const response = await fetch(`${this.baseURL}/users/api/users/me/`, {
        headers: {
          Authorization: `Bearer ${this.token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Failed to get user profile");
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Get user profile error:", error);
      return null;
    }
  }

  findShortcutByTrigger(trigger) {
    return this.shortcuts.find(
      (shortcut) => shortcut.trigger === trigger && shortcut.is_active,
    );
  }

  isAuthenticated() {
    return !!this.token;
  }
}

// Instância global da API
const api = new SymphilikaAPI();

// Inicializar quando o service worker carregar
chrome.runtime.onStartup.addListener(async () => {
  await api.init();
});

chrome.runtime.onInstalled.addListener(async () => {
  await api.init();

  // Configurar alarme para sync periódico
  chrome.alarms.create("syncShortcuts", { periodInMinutes: 30 });
});

// Sync periódico
chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === "syncShortcuts" && api.isAuthenticated()) {
    await api.syncShortcuts();
  }
});

// Comunicação com content scripts e popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  handleMessage(request, sender, sendResponse);
  return true; // Mantém o canal aberto para resposta assíncrona
});

async function handleMessage(request, sender, sendResponse) {
  try {
    switch (request.action) {
      case "init":
        await api.init();
        sendResponse({
          success: true,
          authenticated: api.isAuthenticated(),
          shortcuts: api.shortcuts.length,
          lastSync: api.lastSync,
        });
        break;

      case "login":
        const loginResult = await api.login(request.username, request.password);
        sendResponse(loginResult);
        break;

      case "logout":
        await api.logout();
        sendResponse({ success: true });
        break;

      case "setBaseURL":
        await api.setBaseURL(request.url);
        sendResponse({ success: true });
        break;

      case "syncShortcuts":
        const syncResult = await api.syncShortcuts();
        sendResponse({
          success: syncResult,
          shortcuts: api.shortcuts.length,
          lastSync: api.lastSync,
        });
        break;

      case "findShortcut":
        const shortcut = api.findShortcutByTrigger(request.trigger);
        sendResponse({ shortcut });
        break;

      case "useShortcut":
        const expandedContent = await api.useShortcut(
          request.shortcutId,
          request.variables,
        );
        sendResponse({ content: expandedContent });
        break;

      case "searchShortcuts":
        const searchResults = await api.searchShortcuts(request.query);
        sendResponse({ results: searchResults });
        break;

      case "getShortcuts":
        sendResponse({ shortcuts: api.shortcuts });
        break;

      case "getCategories":
        const categories = await api.getCategories();
        sendResponse({ categories });
        break;

      case "getMostUsed":
        const mostUsed = await api.getMostUsedShortcuts();
        sendResponse({ shortcuts: mostUsed });
        break;

      case "getStats":
        const userStats = await api.getUserStats();
        const shortcutStats = await api.getShortcutStats();
        sendResponse({ userStats, shortcutStats });
        break;

      case "getUserProfile":
        const profile = await api.getUserProfile();
        sendResponse({ profile });
        break;

      default:
        sendResponse({ success: false, error: "Unknown action" });
    }
  } catch (error) {
    console.error("Background message handler error:", error);
    sendResponse({ success: false, error: error.message });
  }
}

// Listener para quando a extensão é ativada
chrome.action.onClicked.addListener(async (tab) => {
  // Se não houver popup configurado, fazer sync
  if (api.isAuthenticated()) {
    await api.syncShortcuts();
  }
});

// Context menu para páginas web
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "symphilikaExpand",
    title: "Expandir com Symplifika",
    contexts: ["selection"],
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === "symphilikaExpand" && info.selectionText) {
    // Buscar por atalhos que correspondam à seleção
    const results = await api.searchShortcuts(info.selectionText);

    if (results.length > 0) {
      // Enviar resultado para o content script
      chrome.tabs.sendMessage(tab.id, {
        action: "expandSelection",
        shortcut: results[0],
      });
    }
  }
});

// Notification helpers
function showNotification(title, message, type = "basic") {
  chrome.notifications.create({
    type: type,
    iconUrl: "icons/icon48.png",
    title: title,
    message: message,
  });
}

// Error handling global
self.addEventListener("error", (event) => {
  console.error("Background script error:", event.error);
});

self.addEventListener("unhandledrejection", (event) => {
  console.error("Unhandled promise rejection:", event.reason);
});

console.log("Symplifika Background Service Worker loaded");
