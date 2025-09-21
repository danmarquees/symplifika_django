/**
 * Symplifika Base System
 * Sistema base para modals, notificações e utilitários
 */

window.Symplifika = window.Symplifika || {};

/**
 * Sistema de Modal
 */
window.Symplifika.Modal = {
  /**
   * Abre um modal
   * @param {string} modalId - ID do modal a ser aberto
   */
  open(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove("hidden");
      document.body.style.overflow = "hidden";

      // Focar no primeiro input visível
      const firstInput = modal.querySelector(
        'input:not([type="hidden"]), textarea, select',
      );
      if (firstInput) {
        setTimeout(() => firstInput.focus(), 100);
      }

      // Adicionar listener para ESC
      this.addEscapeListener(modalId);
    }
  },

  /**
   * Fecha um modal
   * @param {string} modalId - ID do modal a ser fechado
   */
  close(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add("hidden");
      document.body.style.overflow = "";

      // Remover listener do ESC
      this.removeEscapeListener();
    }
  },

  /**
   * Adiciona listener para tecla ESC
   * @param {string} modalId - ID do modal
   */
  addEscapeListener(modalId) {
    this.escapeHandler = (e) => {
      if (e.key === "Escape") {
        this.close(modalId);
      }
    };
    document.addEventListener("keydown", this.escapeHandler);
  },

  /**
   * Remove listener da tecla ESC
   */
  removeEscapeListener() {
    if (this.escapeHandler) {
      document.removeEventListener("keydown", this.escapeHandler);
      this.escapeHandler = null;
    }
  },
};

/**
 * Sistema de Notificações/Toast
 */
window.Symplifika.Toast = {
  container: null,

  /**
   * Inicializa o container de notificações
   */
  init() {
    if (!this.container) {
      this.container = document.createElement("div");
      this.container.id = "toast-container";
      this.container.className = "fixed top-4 right-4 z-50 space-y-2";
      document.body.appendChild(this.container);
    }
  },

  /**
   * Mostra uma notificação
   * @param {string} message - Mensagem da notificação
   * @param {string} type - Tipo da notificação (success, error, warning, info)
   * @param {number} duration - Duração em ms (padrão: 5000)
   */
  show(message, type = "info", duration = 5000) {
    this.init();

    const toast = document.createElement("div");
    toast.className = `toast toast-${type} transform translate-x-full transition-transform duration-300 ease-in-out`;

    const icons = {
      success: `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
            </svg>`,
      error: `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
            </svg>`,
      warning: `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
            </svg>`,
      info: `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
            </svg>`,
    };

    const colors = {
      success:
        "bg-green-100 border-green-500 text-green-900 dark:bg-green-900 dark:border-green-600 dark:text-green-100",
      error:
        "bg-red-100 border-red-500 text-red-900 dark:bg-red-900 dark:border-red-600 dark:text-red-100",
      warning:
        "bg-yellow-100 border-yellow-500 text-yellow-900 dark:bg-yellow-900 dark:border-yellow-600 dark:text-yellow-100",
      info: "bg-blue-100 border-blue-500 text-blue-900 dark:bg-blue-900 dark:border-blue-600 dark:text-blue-100",
    };

    toast.innerHTML = `
            <div class="flex items-center p-4 border-l-4 rounded-lg shadow-lg ${colors[type]} max-w-sm">
                <div class="flex-shrink-0">
                    ${icons[type]}
                </div>
                <div class="ml-3 flex-1">
                    <p class="text-sm font-medium">${message}</p>
                </div>
                <div class="ml-4 flex-shrink-0">
                    <button class="inline-flex text-current hover:opacity-75 focus:outline-none" onclick="this.closest('.toast').remove()">
                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
                        </svg>
                    </button>
                </div>
            </div>
        `;

    this.container.appendChild(toast);

    // Animar entrada
    setTimeout(() => {
      toast.classList.remove("translate-x-full");
      toast.classList.add("translate-x-0");
    }, 10);

    // Auto remover
    if (duration > 0) {
      setTimeout(() => {
        this.remove(toast);
      }, duration);
    }
  },

  /**
   * Remove uma notificação
   * @param {HTMLElement} toast - Elemento da notificação
   */
  remove(toast) {
    if (toast && toast.parentNode) {
      toast.classList.remove("translate-x-0");
      toast.classList.add("translate-x-full");
      setTimeout(() => {
        if (toast.parentNode) {
          toast.parentNode.removeChild(toast);
        }
      }, 300);
    }
  },

  /**
   * Métodos de conveniência
   */
  success(message, duration = 5000) {
    this.show(message, "success", duration);
  },

  error(message, duration = 7000) {
    this.show(message, "error", duration);
  },

  warning(message, duration = 6000) {
    this.show(message, "warning", duration);
  },

  info(message, duration = 5000) {
    this.show(message, "info", duration);
  },
};

/**
 * Utilitários
 */
window.Symplifika.Utils = {
  /**
   * Mostra loader global
   */
  showLoader() {
    let loader = document.getElementById("global-loader");
    if (!loader) {
      loader = document.createElement("div");
      loader.id = "global-loader";
      loader.className =
        "fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50";
      loader.innerHTML = `
                <div class="bg-white dark:bg-gray-800 rounded-lg p-6 flex items-center space-x-3">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    <span class="text-gray-900 dark:text-white">Carregando...</span>
                </div>
            `;
      document.body.appendChild(loader);
    }
    loader.classList.remove("hidden");
  },

  /**
   * Esconde loader global
   */
  hideLoader() {
    const loader = document.getElementById("global-loader");
    if (loader) {
      loader.classList.add("hidden");
    }
  },

  /**
   * Remove loader global
   */
  removeLoader() {
    const loader = document.getElementById("global-loader");
    if (loader) {
      loader.remove();
    }
  },

  /**
   * Debounce function
   * @param {Function} func - Função a ser executada
   * @param {number} wait - Tempo de espera em ms
   * @param {boolean} immediate - Executar imediatamente
   */
  debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        timeout = null;
        if (!immediate) func(...args);
      };
      const callNow = immediate && !timeout;
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
      if (callNow) func(...args);
    };
  },

  /**
   * Throttle function
   * @param {Function} func - Função a ser executada
   * @param {number} limit - Limite em ms
   */
  throttle(func, limit) {
    let inThrottle;
    return function (...args) {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => (inThrottle = false), limit);
      }
    };
  },

  /**
   * Escapa HTML
   * @param {string} unsafe - String não segura
   */
  escapeHtml(unsafe) {
    return unsafe
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  },

  /**
   * Formata data
   * @param {string|Date} date - Data a ser formatada
   * @param {string} locale - Locale (padrão: pt-BR)
   */
  formatDate(date, locale = "pt-BR") {
    if (!date) return "";
    const dateObj = typeof date === "string" ? new Date(date) : date;
    return dateObj.toLocaleDateString(locale);
  },

  /**
   * Formata data e hora
   * @param {string|Date} date - Data a ser formatada
   * @param {string} locale - Locale (padrão: pt-BR)
   */
  formatDateTime(date, locale = "pt-BR") {
    if (!date) return "";
    const dateObj = typeof date === "string" ? new Date(date) : date;
    return dateObj.toLocaleString(locale);
  },

  /**
   * Copia texto para clipboard
   * @param {string} text - Texto a ser copiado
   */
  async copyToClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      this.showSuccessMessage("Texto copiado para a área de transferência!");
      return true;
    } catch (err) {
      console.error("Erro ao copiar texto:", err);
      // Fallback para navegadores mais antigos
      const textArea = document.createElement("textarea");
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();

      try {
        document.execCommand("copy");
        this.showSuccessMessage("Texto copiado para a área de transferência!");
        return true;
      } catch (fallbackErr) {
        console.error("Fallback copy failed:", fallbackErr);
        window.Symplifika.Toast.error("Erro ao copiar texto");
        return false;
      } finally {
        document.body.removeChild(textArea);
      }
    }
  },
};

/**
 * API Helper
 */
window.Symplifika.API = {
  baseURL: "",

  /**
   * Obtém token CSRF
   */
  getCSRFToken() {
    const token = document.querySelector("[name=csrfmiddlewaretoken]");
    return token ? token.value : "";
  },

  /**
   * Faz requisição HTTP
   * @param {string} url - URL da requisição
   * @param {Object} options - Opções da requisição
   */
  async request(url, options = {}) {
    const defaultOptions = {
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": this.getCSRFToken(),
      },
    };

    const mergedOptions = {
      ...defaultOptions,
      ...options,
      headers: {
        ...defaultOptions.headers,
        ...options.headers,
      },
    };

    try {
      const response = await fetch(this.baseURL + url, mergedOptions);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP Error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("API Error:", error);
      throw error;
    }
  },

  /**
   * GET request
   */
  async get(url, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const fullUrl = queryString ? `${url}?${queryString}` : url;
    return this.request(fullUrl, { method: "GET" });
  },

  /**
   * POST request
   */
  async post(url, data = {}) {
    return this.request(url, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  /**
   * PUT request
   */
  async put(url, data = {}) {
    return this.request(url, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  /**
   * DELETE request
   */
  async delete(url) {
    return this.request(url, { method: "DELETE" });
  },
};

/**
 * Validação de Formulários
 */
window.Symplifika.Validation = {
  /**
   * Valida email
   * @param {string} email - Email a ser validado
   */
  validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  },

  /**
   * Valida campo obrigatório
   * @param {string} value - Valor a ser validado
   */
  validateRequired(value) {
    return value && value.toString().trim().length > 0;
  },

  /**
   * Valida tamanho mínimo
   * @param {string} value - Valor a ser validado
   * @param {number} min - Tamanho mínimo
   */
  validateMinLength(value, min) {
    return value && value.toString().length >= min;
  },

  /**
   * Valida tamanho máximo
   * @param {string} value - Valor a ser validado
   * @param {number} max - Tamanho máximo
   */
  validateMaxLength(value, max) {
    return !value || value.toString().length <= max;
  },

  /**
   * Valida padrão regex
   * @param {string} value - Valor a ser validado
   * @param {RegExp} pattern - Padrão regex
   */
  validatePattern(value, pattern) {
    return !value || pattern.test(value);
  },
};

// Inicialização automática
document.addEventListener("DOMContentLoaded", function () {
  // Configurar fechamento de modais clicando no backdrop
  document.addEventListener("click", function (e) {
    if (e.target.classList.contains("modal")) {
      const modalId = e.target.id;
      if (modalId) {
        window.Symplifika.Modal.close(modalId);
      }
    }
  });

  // Alternância de tema claro/escuro
  const themeToggleBtn = document.querySelector("[data-theme-toggle]");
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener("click", function () {
      document.documentElement.classList.toggle("dark");
      // Salvar preferência no localStorage
      if (document.documentElement.classList.contains("dark")) {
        localStorage.setItem("theme", "dark");
      } else {
        localStorage.setItem("theme", "light");
      }
    });

    // Restaurar preferência ao carregar
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "dark") {
      document.documentElement.classList.add("dark");
    } else if (savedTheme === "light") {
      document.documentElement.classList.remove("dark");
    }
  }

  console.log("Symplifika Base System initialized");
});
