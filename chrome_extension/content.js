// Content Script para Symplifika Chrome Extension
// Detecta atalhos de texto e os expande automaticamente

class SymphilikaContentScript {
  constructor() {
    this.isEnabled = true;
    this.currentInput = null;
    this.lastText = "";
    this.shortcuts = [];
    this.isProcessing = false;
    this.triggerPattern = /\/\/[\w\-]+$/; // Padrão para //palavra-chave
    this.debounceTimer = null;
    this.isAuthenticated = false;

    this.init();
  }

  async init() {
    console.log("Symplifika Content Script iniciado");

    // Carregar configurações
    await this.loadSettings();

    // Verificar autenticação
    await this.checkAuthentication();

    // Configurar listeners
    this.setupEventListeners();

    // Sincronizar atalhos
    await this.syncShortcuts();

    // Criar interface de feedback
    this.createFeedbackUI();

    // Inicializar sistema de ícone de acesso rápido
    if (typeof QuickAccessIcon !== 'undefined') {
      new QuickAccessIcon(this);
    }
  }

  async loadSettings() {
    try {
      const result = await chrome.storage.local.get([
        "isEnabled",
        "shortcuts",
        "token",
      ]);
      this.isEnabled = result.isEnabled !== false; // Padrão é true
      this.shortcuts = result.shortcuts || [];
      this.isAuthenticated = !!result.token;
    } catch (error) {
      console.error("Erro ao carregar configurações:", error);
    }
  }

  async checkAuthentication() {
    try {
      const response = await chrome.runtime.sendMessage({
        action: "init",
      });
      if (response) {
        this.isAuthenticated = response.authenticated;
      }
    } catch (error) {
      console.error("Erro ao verificar autenticação:", error);
    }
  }

  async syncShortcuts() {
    if (!this.isAuthenticated) return;

    try {
      const response = await chrome.runtime.sendMessage({
        action: "getShortcuts",
      });
      if (response && response.shortcuts) {
        this.shortcuts = response.shortcuts;
        console.log(`${this.shortcuts.length} atalhos carregados`);
      }
    } catch (error) {
      console.error("Erro ao sincronizar atalhos:", error);
    }
  }

  setupEventListeners() {
    // Listener principal para input de texto
    document.addEventListener("input", this.handleInput.bind(this), true);

    // Listeners para focus/blur
    document.addEventListener("focus", this.handleFocus.bind(this), true);
    document.addEventListener("blur", this.handleBlur.bind(this), true);

    // Listener para mensagens do background
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      this.handleMessage(request, sender, sendResponse);
    });

    // Listener para teclas especiais
    document.addEventListener("keydown", this.handleKeyDown.bind(this), true);

    // Observer para elementos dinâmicos
    this.setupMutationObserver();
  }

  setupMutationObserver() {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === "childList") {
          mutation.addedNodes.forEach((node) => {
            if (node.nodeType === Node.ELEMENT_NODE) {
              this.processNewElements(node);
            }
          });
        }
      });
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });
  }

  processNewElements(element) {
    // Processar novos campos de texto adicionados dinamicamente
    const textFields = element.querySelectorAll(
      'input[type="text"], input[type="email"], textarea, [contenteditable="true"]',
    );
    textFields.forEach((field) => {
      if (!field.hasAttribute("data-symplifika-processed")) {
        field.setAttribute("data-symplifika-processed", "true");
        // Adicionar listeners específicos se necessário
      }
    });
  }

  handleFocus(event) {
    const target = event.target;
    if (this.isTextInput(target)) {
      this.currentInput = target;
      this.lastText = this.getInputValue(target);
    }
  }

  handleBlur(event) {
    if (event.target === this.currentInput) {
      this.currentInput = null;
      this.lastText = "";
    }
  }

  handleInput(event) {
    if (!this.isEnabled || this.isProcessing) return;

    const target = event.target;
    if (!this.isTextInput(target)) return;

    this.currentInput = target;

    // Debounce para evitar muitas checagens
    clearTimeout(this.debounceTimer);
    this.debounceTimer = setTimeout(() => {
      this.checkForTriggers(target);
    }, 100);
  }

  handleKeyDown(event) {
    // Atalhos de teclado especiais
    if (event.ctrlKey || event.metaKey) {
      if (event.key === "j") {
        // Ctrl/Cmd + J para abrir busca rápida
        event.preventDefault();
        this.openQuickSearch();
      }
    }

    // Enter ou Tab após trigger
    if ((event.key === "Enter" || event.key === "Tab") && this.currentInput) {
      const value = this.getInputValue(this.currentInput);
      const match = value.match(this.triggerPattern);
      if (match) {
        event.preventDefault();
        this.processTrigger(this.currentInput, match[0]);
      }
    }
  }

  async checkForTriggers(input) {
    const currentText = this.getInputValue(input);

    // Verificar se há um trigger no final do texto
    const match = currentText.match(this.triggerPattern);
    if (match) {
      const trigger = match[0];
      await this.processTrigger(input, trigger);
    }
  }

  async processTrigger(input, trigger) {
    if (this.isProcessing) return;

    this.isProcessing = true;

    try {
      // Buscar atalho localmente primeiro
      let shortcut = this.findLocalShortcut(trigger);

      if (!shortcut) {
        // Buscar no servidor por trigger exato
        const response = await chrome.runtime.sendMessage({
          action: "findShortcut",
          trigger: trigger,
        });
        shortcut = response?.shortcut;
      }

      // Se ainda não encontrou, buscar por texto (search)
      if (!shortcut) {
        try {
          const searchResults = await chrome.runtime.sendMessage({
            action: "searchShortcuts",
            query: trigger.replace(/^\/\//, ""), // remove // do início
          });
          if (
            searchResults &&
            searchResults.results &&
            searchResults.results.length > 0
          ) {
            shortcut = searchResults.results[0];
          }
        } catch (searchError) {
          this.showError("Erro ao buscar atalhos por texto");
        }
      }

      if (shortcut) {
        await this.expandShortcut(input, trigger, shortcut);
      } else {
        this.showSuggestion(input, trigger);
      }
    } catch (error) {
      console.error("Erro ao processar trigger:", error);
      this.showError(
        "Erro ao expandir atalho: " +
          (error && error.message ? error.message : error),
      );
    } finally {
      this.isProcessing = false;
    }
  }

  findLocalShortcut(trigger) {
    return this.shortcuts.find(
      (shortcut) => shortcut.trigger === trigger && shortcut.is_active,
    );
  }

  async expandShortcut(input, trigger, shortcut) {
    // Mostrar loading
    this.showLoading(input);

    try {
      let expandedContent;

      if (shortcut.expansion_type === "dynamic" && shortcut.variables) {
        // Solicitar variáveis do usuário
        const variables = await this.requestVariables(shortcut.variables);
        if (variables === null) {
          this.hideLoading();
          return; // Usuário cancelou
        }

        const response = await chrome.runtime.sendMessage({
          action: "useShortcut",
          shortcutId: shortcut.id,
          variables: variables,
        });
        expandedContent = response?.content;
      } else if (shortcut.expansion_type === "ai_enhanced") {
        // Expansão com IA
        const response = await chrome.runtime.sendMessage({
          action: "useShortcut",
          shortcutId: shortcut.id,
        });
        expandedContent = response?.content;
      } else {
        // Expansão estática
        expandedContent = shortcut.content;
      }

      if (expandedContent) {
        this.replaceText(input, trigger, expandedContent);
        this.showSuccess(`Atalho "${trigger}" expandido!`);
      } else {
        throw new Error("Conteúdo não disponível");
      }
    } catch (error) {
      console.error("Erro na expansão:", error);
      this.showError("Falha ao expandir atalho");
    } finally {
      this.hideLoading();
    }
  }

  replaceText(input, trigger, newText) {
    const currentValue = this.getInputValue(input);
    const triggerIndex = currentValue.lastIndexOf(trigger);

    if (triggerIndex !== -1) {
      const beforeTrigger = currentValue.substring(0, triggerIndex);
      const afterTrigger = currentValue.substring(
        triggerIndex + trigger.length,
      );
      const newValue = beforeTrigger + newText + afterTrigger;

      this.setInputValue(input, newValue);

      // Posicionar cursor após o texto inserido
      const newPosition = beforeTrigger.length + newText.length;
      this.setCursorPosition(input, newPosition);

      // Disparar evento de mudança
      input.dispatchEvent(new Event("input", { bubbles: true }));

      // Highlight visual do texto expandido
      this.highlightInsertedText(input, beforeTrigger.length, newText.length);
    }
  }

  /**
   * Destaca visualmente o texto recém-inserido (microanimação highlight).
   */
  highlightInsertedText(input, start, length) {
    if (input.contentEditable === "true") {
      // Para contenteditable, envolve o texto em um span temporário
      const range = document.createRange();
      const sel = window.getSelection();
      const node = input.firstChild || input;
      range.setStart(node, start);
      range.setEnd(node, start + length);

      const highlightSpan = document.createElement("span");
      highlightSpan.style.background = "#b6e6b6";
      highlightSpan.style.transition = "background 1s";
      highlightSpan.className = "symplifika-highlight-inserted";
      range.surroundContents(highlightSpan);

      setTimeout(() => {
        highlightSpan.style.background = "transparent";
        setTimeout(() => {
          if (highlightSpan.parentNode) {
            while (highlightSpan.firstChild) {
              highlightSpan.parentNode.insertBefore(
                highlightSpan.firstChild,
                highlightSpan,
              );
            }
            highlightSpan.parentNode.removeChild(highlightSpan);
          }
        }, 800);
      }, 800);
    } else if (input.setSelectionRange) {
      // Para input/textarea, usa seleção temporária e animação CSS
      input.classList.add("symplifika-input-highlight");
      setTimeout(() => {
        input.classList.remove("symplifika-input-highlight");
      }, 1200);
    }
  }

  async requestVariables(variables) {
    return new Promise((resolve) => {
      const modal = this.createVariableModal(variables, resolve);
      document.body.appendChild(modal);
    });
  }

  createVariableModal(variables, callback) {
    const modal = document.createElement("div");
    modal.className = "symplifika-variable-modal";
    modal.innerHTML = `
      <div class="symplifika-modal-content">
        <div class="symplifika-modal-header">
          <h3>Preencha as variáveis</h3>
          <button class="symplifika-close-btn">&times;</button>
        </div>
        <div class="symplifika-modal-body">
          ${Object.entries(variables)
            .map(
              ([key, defaultValue]) => `
            <div class="symplifika-variable-field">
              <label for="var-${key}">${key}:</label>
              <input type="text" id="var-${key}" value="${defaultValue}" />
            </div>
          `,
            )
            .join("")}
        </div>
        <div class="symplifika-modal-footer">
          <button class="symplifika-btn symplifika-btn-primary" id="confirm-variables">Confirmar</button>
          <button class="symplifika-btn symplifika-btn-secondary" id="cancel-variables">Cancelar</button>
        </div>
      </div>
    `;

    // Event listeners
    modal.querySelector(".symplifika-close-btn").onclick = () => {
      document.body.removeChild(modal);
      callback(null);
    };

    modal.querySelector("#cancel-variables").onclick = () => {
      document.body.removeChild(modal);
      callback(null);
    };

    modal.querySelector("#confirm-variables").onclick = () => {
      const result = {};
      Object.keys(variables).forEach((key) => {
        const input = modal.querySelector(`#var-${key}`);
        result[key] = input.value;
      });
      document.body.removeChild(modal);
      callback(result);
    };

    return modal;
  }

  showSuggestion(input, trigger) {
    // Mostrar sugestão para criar novo atalho
    const suggestion = this.createSuggestionTooltip(trigger);
    this.positionTooltip(suggestion, input);
    document.body.appendChild(suggestion);

    setTimeout(() => {
      if (suggestion.parentNode) {
        document.body.removeChild(suggestion);
      }
    }, 3000);
  }

  createSuggestionTooltip(trigger) {
    const tooltip = document.createElement("div");
    tooltip.className = "symplifika-suggestion-tooltip";
    tooltip.innerHTML = `
      <div class="symplifika-tooltip-content">
        <p>Atalho "${trigger}" não encontrado</p>
        <button class="symplifika-btn symplifika-btn-small" id="symplifika-create-shortcut-btn">
          Criar atalho
        </button>
      </div>
    `;

    // Adiciona evento para abrir painel web na URL correta
    setTimeout(() => {
      const btn = tooltip.querySelector("#symplifika-create-shortcut-btn");
      if (btn) {
        btn.onclick = async () => {
          // Busca a URL do servidor do storage
          let serverUrl = "http://localhost:8000";
          try {
            const result = await chrome.storage.local.get([
              "settings",
              "baseURL",
            ]);
            if (result.settings && result.settings.serverUrl) {
              serverUrl = result.settings.serverUrl;
            } else if (result.baseURL) {
              serverUrl = result.baseURL;
            }
          } catch (e) {}
          window.open(`${serverUrl.replace(/\/$/, "")}/shortcuts/`, "_blank");
          if (tooltip.parentNode) tooltip.parentNode.removeChild(tooltip);
        };
      }
    }, 0);

    return tooltip;
  }

  // Utility methods
  isTextInput(element) {
    if (!element) return false;

    const tagName = element.tagName.toLowerCase();

    if (tagName === "input") {
      const type = element.type.toLowerCase();
      return ["text", "email", "password", "search", "url", "tel"].includes(
        type,
      );
    }

    if (tagName === "textarea") return true;
    if (element.contentEditable === "true") return true;

    return false;
  }

  getInputValue(input) {
    if (input.contentEditable === "true") {
      return input.textContent || "";
    }
    return input.value || "";
  }

  setInputValue(input, value) {
    if (input.contentEditable === "true") {
      input.textContent = value;
    } else {
      input.value = value;
    }
  }

  setCursorPosition(input, position) {
    if (input.contentEditable === "true") {
      const range = document.createRange();
      const sel = window.getSelection();
      range.setStart(
        input.firstChild || input,
        Math.min(position, input.textContent.length),
      );
      range.collapse(true);
      sel.removeAllRanges();
      sel.addRange(range);
    } else if (input.setSelectionRange) {
      input.setSelectionRange(position, position);
    }
    input.focus();
  }

  positionTooltip(tooltip, input) {
    const rect = input.getBoundingClientRect();
    tooltip.style.position = "fixed";
    tooltip.style.top = rect.bottom + 5 + "px";
    tooltip.style.left = rect.left + "px";
    tooltip.style.zIndex = "10000";
  }

  // UI Feedback methods
  createFeedbackUI() {
    if (document.getElementById("symplifika-feedback")) return;

    const feedback = document.createElement("div");
    feedback.id = "symplifika-feedback";
    feedback.className = "symplifika-feedback-container";
    document.body.appendChild(feedback);
  }

  showLoading(input) {
    const loading = document.createElement("div");
    loading.className = "symplifika-loading-indicator";
    loading.innerHTML = "⏳ Expandindo...";
    this.positionTooltip(loading, input);
    document.body.appendChild(loading);
  }

  hideLoading() {
    const loading = document.querySelector(".symplifika-loading-indicator");
    if (loading) {
      document.body.removeChild(loading);
    }
  }

  showSuccess(message) {
    this.showFeedback(message, "success");
  }

  showError(message) {
    this.showFeedback(message, "error");
  }

  showFeedback(message, type) {
    const feedback = document.getElementById("symplifika-feedback");
    if (!feedback) return;

    const notification = document.createElement("div");
    notification.className = `symplifika-notification symplifika-${type}`;
    notification.textContent = message;

    feedback.appendChild(notification);

    setTimeout(() => {
      if (notification.parentNode) {
        feedback.removeChild(notification);
      }
    }, 3000);
  }

  openQuickSearch() {
    // Implementar busca rápida (futuro)
    this.logDebug("Busca rápida não implementada ainda");
  }

  // Message handler
  handleMessage(request, sender, sendResponse) {
    switch (request.action) {
      case "expandSelection":
        if (request.shortcut && window.getSelection().toString()) {
          this.expandSelection(request.shortcut);
        }
        break;

      case "toggleEnabled":
        this.isEnabled = request.enabled;
        break;

      case "syncShortcuts":
        this.syncShortcuts();
        break;
    }
  }

  expandSelection(shortcut) {
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
      const range = selection.getRangeAt(0);
      range.deleteContents();
      range.insertNode(document.createTextNode(shortcut.content));
    }
  }

  // Método para marcar atalho como usado
  async markShortcutAsUsed(trigger) {
    try {
      const shortcut = this.shortcuts.find(s => s.trigger === trigger);
      if (shortcut) {
        await chrome.runtime.sendMessage({
          action: "useShortcut",
          shortcutId: shortcut.id
        });
      }
    } catch (error) {
      console.error("Erro ao marcar atalho como usado:", error);
    }
  }
}

// Inicializar quando o DOM estiver pronto
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    new SymphilikaContentScript();
  });
} else {
  new SymphilikaContentScript();
}

/**
 * Loga mensagens de debug se o modo debug estiver ativo.
 */
function getDebugMode() {
  return new Promise((resolve) => {
    chrome.storage.local.get(["settings", "debugMode"], (result) => {
      if (result.settings && typeof result.settings.debugMode !== "undefined") {
        resolve(result.settings.debugMode);
      } else if (typeof result.debugMode !== "undefined") {
        resolve(result.debugMode);
      } else {
        resolve(false);
      }
    });
  });
}

SymphilikaContentScript.prototype.logDebug = async function (...args) {
  const debug = await getDebugMode();
  if (debug) {
    // eslint-disable-next-line no-console
    console.log("[Symplifika DEBUG]", ...args);
  }
};

// CSS para highlight visual (injetado se não existir)
(function injectSymplifikaHighlightCSS() {
  if (!document.getElementById("symplifika-highlight-style")) {
    const style = document.createElement("style");
    style.id = "symplifika-highlight-style";
    style.innerHTML = `
      .symplifika-highlight-inserted {
        background: #b6e6b6 !important;
        transition: background 1s;
        border-radius: 3px;
        padding: 0 2px;
      }
      .symplifika-input-highlight {
        box-shadow: 0 0 0 3px #b6e6b6 !important;
        transition: box-shadow 1s;
      }
    `;
    document.head.appendChild(style);
  }
})();

console.log("Symplifika Content Script carregado");
