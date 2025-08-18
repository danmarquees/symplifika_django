// Symplifika Base JavaScript

// Utility functions
const Utils = {
  // Get CSRF token
  getCSRFToken() {
    const token = document.querySelector("[name=csrfmiddlewaretoken]");
    const metaToken = document.querySelector('meta[name="csrf-token"]');
    return token
      ? token.value
      : metaToken
        ? metaToken.getAttribute("content")
        : "";
  },

  // Check if element is in viewport
  isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
      rect.top >= 0 &&
      rect.left >= 0 &&
      rect.bottom <=
        (window.innerHeight || document.documentElement.clientHeight) &&
      rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
  },

  // Smooth scroll to element
  scrollToElement(selector, offset = 0) {
    const element = document.querySelector(selector);
    if (element) {
      const targetPosition = element.offsetTop - offset;
      window.scrollTo({
        top: targetPosition,
        behavior: "smooth",
      });
    }
  },

  // Show/hide loading spinner
  showLoader() {
    const spinner = document.getElementById("loadingSpinner");
    if (spinner) spinner.classList.remove("hidden");
  },

  hideLoader() {
    const spinner = document.getElementById("loadingSpinner");
    if (spinner) spinner.classList.add("hidden");
  },

  // Format date
  formatDate(date, options = {}) {
    const defaultOptions = {
      year: "numeric",
      month: "long",
      day: "numeric",
    };
    return new Date(date).toLocaleDateString("pt-BR", {
      ...defaultOptions,
      ...options,
    });
  },

  // Debounce function
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  // Throttle function
  throttle(func, limit) {
    let inThrottle;
    return function () {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => (inThrottle = false), limit);
      }
    };
  },
};

// Toast notifications
const Toast = {
  show(message, type = "info", duration = 5000) {
    const toast = document.createElement("div");
    toast.className = `toast toast-${type} animate-slide-in`;
    toast.innerHTML = `
            <div class="flex items-center justify-between">
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-white hover:text-gray-200">
                    ×
                </button>
            </div>
        `;

    document.body.appendChild(toast);

    // Auto remove after duration
    setTimeout(() => {
      if (toast.parentNode) {
        toast.classList.add("animate-fade-out");
        setTimeout(() => toast.remove(), 300);
      }
    }, duration);
  },

  success(message, duration) {
    this.show(message, "success", duration);
  },

  error(message, duration) {
    this.show(message, "error", duration);
  },

  warning(message, duration) {
    this.show(message, "warning", duration);
  },

  info(message, duration) {
    this.show(message, "info", duration);
  },
};

// Modern Modal Component - replaces legacy functionality
class ModalComponent {
  constructor() {
    this.openModals = new Set();
    this.escapeHandler = this.handleEscape.bind(this);
    this.clickHandler = this.handleOverlayClick.bind(this);
    this.init();
  }

  init() {
    // Initialize modal event listeners
    document.addEventListener("keydown", this.escapeHandler);
    document.addEventListener("click", this.clickHandler);
    this.setupCloseButtons();
  }

  open(modalId, options = {}) {
    const modal = document.getElementById(modalId);
    if (!modal) {
      console.warn(`Modal with ID "${modalId}" not found`);
      return;
    }

    this.openModals.add(modalId);
    modal.classList.remove("hidden");
    modal.classList.add("show");
    document.body.style.overflow = "hidden";

    modal.setAttribute("aria-hidden", "false");
    modal.setAttribute("role", "dialog");
    modal.setAttribute("aria-modal", "true");

    this.setFocus(modal);

    modal.dispatchEvent(
      new CustomEvent("modal:opened", { detail: { modalId, options } }),
    );

    requestAnimationFrame(() => {
      modal.classList.add("animate-in");
    });
  }

  close(modalId, options = {}) {
    const modal = document.getElementById(modalId);
    if (!modal) {
      console.warn(`Modal with ID "${modalId}" not found`);
      return;
    }

    this.openModals.delete(modalId);
    modal.classList.add("animate-out");
    modal.classList.remove("animate-in");

    setTimeout(() => {
      modal.classList.add("hidden");
      modal.classList.remove("show", "animate-out");
      modal.setAttribute("aria-hidden", "true");
      modal.removeAttribute("role");
      modal.removeAttribute("aria-modal");
    }, 200);

    if (this.openModals.size === 0) {
      document.body.style.overflow = "";
    }

    this.restoreFocus(modal);

    modal.dispatchEvent(
      new CustomEvent("modal:closed", { detail: { modalId, options } }),
    );
  }

  closeOnOverlay(event, modalId) {
    if (event.target === event.currentTarget) {
      this.close(modalId);
    }
  }

  handleEscape(event) {
    if (event.key === "Escape" && this.openModals.size > 0) {
      const lastModal = Array.from(this.openModals).pop();
      this.close(lastModal);
    }
  }

  handleOverlayClick(event) {
    if (event.target.classList.contains("modal-overlay")) {
      const modalId = event.target.id;
      if (modalId && this.openModals.has(modalId)) {
        this.close(modalId);
      }
    }
  }

  setupCloseButtons() {
    document.querySelectorAll("[data-modal-close]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.preventDefault();
        const modalId =
          button.getAttribute("data-modal-close") ||
          button.closest(".modal-overlay")?.id;
        if (modalId) {
          this.close(modalId);
        }
      });
    });
  }

  setFocus(modal) {
    modal._previousFocus = document.activeElement;
    const autoFocusElement = modal.querySelector("[data-autofocus]");

    if (autoFocusElement) {
      autoFocusElement.focus();
      return;
    }

    const focusableElements = modal.querySelectorAll(
      'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
    );

    if (focusableElements.length > 0) {
      const firstInput = Array.from(focusableElements).find(
        (el) =>
          el.tagName === "INPUT" ||
          el.tagName === "TEXTAREA" ||
          el.tagName === "SELECT",
      );

      if (firstInput) {
        firstInput.focus();
      } else {
        focusableElements[0].focus();
      }
    }
  }

  restoreFocus(modal) {
    if (modal._previousFocus && document.body.contains(modal._previousFocus)) {
      modal._previousFocus.focus();
    }
  }
}

// Initialize Modal component
const ModalManager = new ModalComponent();

// Legacy Modal API for backward compatibility (no warnings)
const Modal = {
  open(modalId) {
    return ModalManager.open(modalId);
  },

  close(modalId) {
    return ModalManager.close(modalId);
  },

  closeOnOverlay(event, modalId) {
    return ModalManager.closeOnOverlay(event, modalId);
  },
};

// API helper
const API = {
  async request(url, options = {}) {
    const defaultOptions = {
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": Utils.getCSRFToken(),
      },
    };

    const config = {
      ...defaultOptions,
      ...options,
      headers: {
        ...defaultOptions.headers,
        ...options.headers,
      },
    };

    try {
      Utils.showLoader();
      const response = await fetch(url, config);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error("API request failed:", error);
      Toast.error("Erro na requisição. Tente novamente.");
      throw error;
    } finally {
      Utils.hideLoader();
    }
  },

  async get(url, options = {}) {
    return this.request(url, { ...options, method: "GET" });
  },

  async post(url, data, options = {}) {
    return this.request(url, {
      ...options,
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async put(url, data, options = {}) {
    return this.request(url, {
      ...options,
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  async delete(url, options = {}) {
    return this.request(url, { ...options, method: "DELETE" });
  },
};

// Form handling
const Form = {
  serialize(form) {
    const formData = new FormData(form);
    const data = {};
    for (let [key, value] of formData.entries()) {
      data[key] = value;
    }
    return data;
  },

  validate(form) {
    const inputs = form.querySelectorAll(
      "input[required], select[required], textarea[required]",
    );
    let isValid = true;

    inputs.forEach((input) => {
      const errorElement = input.parentNode.querySelector(".error-message");

      if (!input.value.trim()) {
        this.showFieldError(input, "Este campo é obrigatório");
        isValid = false;
      } else if (input.type === "email" && !this.isValidEmail(input.value)) {
        this.showFieldError(input, "Digite um email válido");
        isValid = false;
      } else {
        this.clearFieldError(input);
      }
    });

    return isValid;
  },

  showFieldError(input, message) {
    input.classList.add("border-red-500");
    let errorElement = input.parentNode.querySelector(".error-message");

    if (!errorElement) {
      errorElement = document.createElement("div");
      errorElement.className = "error-message text-red-500 text-sm mt-1";
      input.parentNode.appendChild(errorElement);
    }

    errorElement.textContent = message;
  },

  clearFieldError(input) {
    input.classList.remove("border-red-500");
    const errorElement = input.parentNode.querySelector(".error-message");
    if (errorElement) {
      errorElement.remove();
    }
  },

  isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  },
};

// Theme handling
const Theme = {
  init() {
    const savedTheme = localStorage.getItem("theme");
    const systemPrefersDark = window.matchMedia(
      "(prefers-color-scheme: dark)",
    ).matches;

    if (savedTheme === "dark" || (!savedTheme && systemPrefersDark)) {
      this.setDark();
    } else {
      this.setLight();
    }
  },

  setDark() {
    document.documentElement.classList.add("dark");
    localStorage.setItem("theme", "dark");
    this.updateToggleButton();
  },

  setLight() {
    document.documentElement.classList.remove("dark");
    localStorage.setItem("theme", "light");
    this.updateToggleButton();
  },

  toggle() {
    if (document.documentElement.classList.contains("dark")) {
      this.setLight();
    } else {
      this.setDark();
    }
  },

  updateToggleButton() {
    const buttons = document.querySelectorAll("[data-theme-toggle]");
    const isDark = document.documentElement.classList.contains("dark");

    buttons.forEach((button) => {
      const icon = button.querySelector(".theme-icon");
      if (icon) {
        icon.textContent = isDark ? "☀️" : "🌙";
      }
    });
  },
};

// Sidebar functionality
const Sidebar = {
  toggle() {
    const sidebar = document.querySelector(".sidebar, .dashboard-sidebar");
    if (sidebar) {
      sidebar.classList.toggle("open");
      // Update main content margin if dashboard layout
      const main = document.querySelector(".dashboard-main");
      if (main) {
        main.classList.toggle("expanded");
      }
    }
  },

  close() {
    const sidebar = document.querySelector(".sidebar, .dashboard-sidebar");
    if (sidebar) {
      sidebar.classList.remove("open");
      // Reset main content margin if dashboard layout
      const main = document.querySelector(".dashboard-main");
      if (main) {
        main.classList.remove("expanded");
      }
    }
  },

  collapse() {
    const sidebar = document.querySelector(".dashboard-sidebar");
    if (sidebar) {
      sidebar.classList.add("collapsed");
      const main = document.querySelector(".dashboard-main");
      if (main) {
        main.classList.add("expanded");
      }
    }
  },

  expand() {
    const sidebar = document.querySelector(".dashboard-sidebar");
    if (sidebar) {
      sidebar.classList.remove("collapsed");
      const main = document.querySelector(".dashboard-main");
      if (main) {
        main.classList.remove("expanded");
      }
    }
  },
};

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  // Initialize theme
  Theme.init();

  // Setup theme toggle buttons
  document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
    button.addEventListener("click", () => Theme.toggle());
  });

  // Setup sidebar toggle
  document.querySelectorAll("[data-sidebar-toggle]").forEach((button) => {
    button.addEventListener("click", () => Sidebar.toggle());
  });

  // Setup sidebar collapse/expand
  document.querySelectorAll("[data-sidebar-collapse]").forEach((button) => {
    button.addEventListener("click", () => Sidebar.collapse());
  });

  document.querySelectorAll("[data-sidebar-expand]").forEach((button) => {
    button.addEventListener("click", () => Sidebar.expand());
  });

  // Close sidebar on outside click (mobile)
  document.addEventListener("click", function (event) {
    const sidebar = document.querySelector(".sidebar");
    const sidebarToggle = document.querySelector("[data-sidebar-toggle]");

    if (
      sidebar &&
      sidebar.classList.contains("open") &&
      !sidebar.contains(event.target) &&
      !sidebarToggle.contains(event.target)
    ) {
      Sidebar.close();
    }
  });

  // Setup form validation
  document.querySelectorAll("form[data-validate]").forEach((form) => {
    form.addEventListener("submit", function (event) {
      if (!Form.validate(this)) {
        event.preventDefault();
      }
    });
  });

  // Setup modal close on escape key
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      const openModals = document.querySelectorAll(
        ".modal-overlay:not(.hidden)",
      );
      openModals.forEach((modal) => {
        modal.classList.add("hidden");
        document.body.style.overflow = "";
      });
    }
  });

  // Auto-hide alerts
  document.querySelectorAll(".alert").forEach((alert) => {
    setTimeout(() => {
      alert.style.opacity = "0";
      setTimeout(() => alert.remove(), 300);
    }, 5000);
  });

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    });
  });
});

// Global error handler
window.addEventListener("error", function (event) {
  console.error("Global error:", event.error);
  if (
    window.location.hostname !== "localhost" &&
    window.location.hostname !== "127.0.0.1"
  ) {
    // Only show user-friendly messages in production
    Toast.error("Ocorreu um erro inesperado. Tente recarregar a página.");
  }
});

// Handle unhandled promise rejections
window.addEventListener("unhandledrejection", function (event) {
  console.error("Unhandled promise rejection:", event.reason);
  if (
    window.location.hostname !== "localhost" &&
    window.location.hostname !== "127.0.0.1"
  ) {
    Toast.error("Erro de conexão. Verifique sua internet e tente novamente.");
  }
});

// Performance monitoring
const Performance = {
  // Mark performance points
  mark(name) {
    if (window.performance && window.performance.mark) {
      window.performance.mark(name);
    }
  },

  // Measure performance between marks
  measure(name, startMark, endMark) {
    if (window.performance && window.performance.measure) {
      window.performance.measure(name, startMark, endMark);
    }
  },

  // Get navigation timing
  getNavigationTiming() {
    if (window.performance && window.performance.timing) {
      const timing = window.performance.timing;
      return {
        dns: timing.domainLookupEnd - timing.domainLookupStart,
        connect: timing.connectEnd - timing.connectStart,
        request: timing.responseStart - timing.requestStart,
        response: timing.responseEnd - timing.responseStart,
        dom: timing.domContentLoadedEventEnd - timing.navigationStart,
        load: timing.loadEventEnd - timing.navigationStart,
      };
    }
    return null;
  },
};

// Export for use in other scripts
window.Symplifika = {
  Utils,
  Toast,
  Modal: ModalManager,
  API,
  Form,
  Theme,
  Sidebar,
  Performance,
};

// Compatibility aliases
window.SymplifHelper = window.Symplifika; // Legacy support
window.SUtils = Utils;
window.SToast = Toast;
window.SAPI = API;
