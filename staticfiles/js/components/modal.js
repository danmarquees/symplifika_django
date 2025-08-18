// Modern Modal Component for Symplifika
// Replaces legacy Modal functionality with improved UX and accessibility

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

    // Setup modal close buttons
    this.setupCloseButtons();

    // Setup focus traps for existing modals
    this.setupFocusTraps();
  }

  /**
   * Opens a modal by ID
   * @param {string} modalId - The ID of the modal to open
   * @param {Object} options - Optional configuration
   */
  open(modalId, options = {}) {
    const modal = document.getElementById(modalId);
    if (!modal) {
      console.warn(`Modal with ID "${modalId}" not found`);
      return;
    }

    // Add modal to open set
    this.openModals.add(modalId);

    // Show modal
    modal.classList.remove("hidden");
    modal.classList.add("show");

    // Prevent body scroll
    document.body.style.overflow = "hidden";

    // Add ARIA attributes
    modal.setAttribute("aria-hidden", "false");
    modal.setAttribute("role", "dialog");
    modal.setAttribute("aria-modal", "true");

    // Focus management
    this.setFocus(modal);

    // Trigger custom event
    modal.dispatchEvent(
      new CustomEvent("modal:opened", {
        detail: { modalId, options },
      }),
    );

    // Animation
    requestAnimationFrame(() => {
      modal.classList.add("animate-in");
    });
  }

  /**
   * Closes a modal by ID
   * @param {string} modalId - The ID of the modal to close
   * @param {Object} options - Optional configuration
   */
  close(modalId, options = {}) {
    const modal = document.getElementById(modalId);
    if (!modal) {
      console.warn(`Modal with ID "${modalId}" not found`);
      return;
    }

    // Remove from open set
    this.openModals.delete(modalId);

    // Animation out
    modal.classList.add("animate-out");
    modal.classList.remove("animate-in");

    // Hide after animation
    setTimeout(() => {
      modal.classList.add("hidden");
      modal.classList.remove("show", "animate-out");

      // ARIA cleanup
      modal.setAttribute("aria-hidden", "true");
      modal.removeAttribute("role");
      modal.removeAttribute("aria-modal");
    }, 200);

    // Restore body scroll if no other modals open
    if (this.openModals.size === 0) {
      document.body.style.overflow = "";
    }

    // Restore focus to trigger element if available
    this.restoreFocus(modal);

    // Trigger custom event
    modal.dispatchEvent(
      new CustomEvent("modal:closed", {
        detail: { modalId, options },
      }),
    );
  }

  /**
   * Closes all open modals
   */
  closeAll() {
    const modalsToClose = Array.from(this.openModals);
    modalsToClose.forEach((modalId) => this.close(modalId));
  }

  /**
   * Toggles a modal open/closed state
   * @param {string} modalId - The ID of the modal to toggle
   */
  toggle(modalId) {
    if (this.isOpen(modalId)) {
      this.close(modalId);
    } else {
      this.open(modalId);
    }
  }

  /**
   * Check if a modal is currently open
   * @param {string} modalId - The ID of the modal to check
   * @returns {boolean}
   */
  isOpen(modalId) {
    return this.openModals.has(modalId);
  }

  /**
   * Handle escape key press
   * @param {KeyboardEvent} event
   */
  handleEscape(event) {
    if (event.key === "Escape" && this.openModals.size > 0) {
      // Close the most recently opened modal
      const lastModal = Array.from(this.openModals).pop();
      this.close(lastModal);
    }
  }

  /**
   * Handle overlay clicks to close modal
   * @param {MouseEvent} event
   */
  handleOverlayClick(event) {
    // Check if click is on modal overlay (not modal content)
    if (event.target.classList.contains("modal-overlay")) {
      const modalId = event.target.id;
      if (modalId && this.isOpen(modalId)) {
        this.close(modalId);
      }
    }
  }

  /**
   * Setup close buttons for all modals
   */
  setupCloseButtons() {
    // Find all modal close buttons and attach event listeners
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

  /**
   * Setup focus traps for accessibility
   */
  setupFocusTraps() {
    document.querySelectorAll(".modal-overlay").forEach((modal) => {
      const focusableElements = this.getFocusableElements(modal);

      if (focusableElements.length > 0) {
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        modal.addEventListener("keydown", (event) => {
          if (event.key === "Tab") {
            if (event.shiftKey) {
              // Shift + Tab
              if (document.activeElement === firstElement) {
                event.preventDefault();
                lastElement.focus();
              }
            } else {
              // Tab
              if (document.activeElement === lastElement) {
                event.preventDefault();
                firstElement.focus();
              }
            }
          }
        });
      }
    });
  }

  /**
   * Set focus to appropriate element in modal
   * @param {HTMLElement} modal
   */
  setFocus(modal) {
    // Store the currently focused element
    modal._previousFocus = document.activeElement;

    // Focus priority: [data-autofocus], first input, first button, first focusable
    const autoFocusElement = modal.querySelector("[data-autofocus]");
    if (autoFocusElement) {
      autoFocusElement.focus();
      return;
    }

    const focusableElements = this.getFocusableElements(modal);
    if (focusableElements.length > 0) {
      // Prefer inputs over buttons
      const firstInput = focusableElements.find(
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

  /**
   * Restore focus to previous element
   * @param {HTMLElement} modal
   */
  restoreFocus(modal) {
    if (modal._previousFocus && document.body.contains(modal._previousFocus)) {
      modal._previousFocus.focus();
    }
  }

  /**
   * Get all focusable elements within a container
   * @param {HTMLElement} container
   * @returns {HTMLElement[]}
   */
  getFocusableElements(container) {
    const focusableSelectors = [
      "button:not([disabled])",
      "[href]:not([disabled])",
      'input:not([disabled]):not([type="hidden"])',
      "select:not([disabled])",
      "textarea:not([disabled])",
      '[tabindex]:not([tabindex="-1"]):not([disabled])',
      '[contenteditable]:not([contenteditable="false"])',
    ].join(", ");

    return Array.from(container.querySelectorAll(focusableSelectors)).filter(
      (element) => {
        // Filter out elements that are not visible
        const style = window.getComputedStyle(element);
        return (
          style.display !== "none" &&
          style.visibility !== "hidden" &&
          element.offsetWidth > 0 &&
          element.offsetHeight > 0
        );
      },
    );
  }

  /**
   * Show modal with custom content
   * @param {string} title
   * @param {string} content
   * @param {Object} options
   */
  show(title, content, options = {}) {
    const modalId = options.id || `modal-${Date.now()}`;

    // Create modal HTML if it doesn't exist
    let modal = document.getElementById(modalId);
    if (!modal) {
      modal = this.createModal(modalId, title, content, options);
      document.body.appendChild(modal);
    } else {
      // Update existing modal
      this.updateModal(modal, title, content, options);
    }

    this.open(modalId, options);
    return modalId;
  }

  /**
   * Create modal HTML element
   * @param {string} modalId
   * @param {string} title
   * @param {string} content
   * @param {Object} options
   * @returns {HTMLElement}
   */
  createModal(modalId, title, content, options = {}) {
    const modal = document.createElement("div");
    modal.id = modalId;
    modal.className =
      "modal-overlay fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 hidden";
    modal.setAttribute("aria-hidden", "true");

    const size = options.size || "md";
    const sizeClasses = {
      sm: "max-w-sm",
      md: "max-w-md",
      lg: "max-w-lg",
      xl: "max-w-xl",
      "2xl": "max-w-2xl",
      full: "max-w-full mx-4",
    };

    modal.innerHTML = `
      <div class="modal-content bg-white dark:bg-gray-800 rounded-lg shadow-xl ${sizeClasses[size]} w-full">
        <div class="modal-header flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 class="modal-title text-lg font-semibold text-gray-900 dark:text-white">
            ${title}
          </h3>
          <button
            type="button"
            data-modal-close="${modalId}"
            class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            aria-label="Close modal"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        <div class="modal-body p-6">
          ${content}
        </div>
        ${
          options.showFooter !== false
            ? `
          <div class="modal-footer flex justify-end space-x-3 p-6 border-t border-gray-200 dark:border-gray-700">
            <button
              type="button"
              data-modal-close="${modalId}"
              class="btn btn-outline"
            >
              Cancelar
            </button>
            ${
              options.confirmButton
                ? `
              <button
                type="button"
                class="btn btn-primary"
                data-modal-confirm="${modalId}"
              >
                ${options.confirmButton}
              </button>
            `
                : ""
            }
          </div>
        `
            : ""
        }
      </div>
    `;

    // Setup close button events
    setTimeout(() => this.setupCloseButtons(), 0);

    return modal;
  }

  /**
   * Update existing modal content
   * @param {HTMLElement} modal
   * @param {string} title
   * @param {string} content
   * @param {Object} options
   */
  updateModal(modal, title, content, options = {}) {
    const titleElement = modal.querySelector(".modal-title");
    const bodyElement = modal.querySelector(".modal-body");

    if (titleElement) titleElement.textContent = title;
    if (bodyElement) bodyElement.innerHTML = content;
  }

  /**
   * Confirm dialog
   * @param {string} title
   * @param {string} message
   * @param {Object} options
   * @returns {Promise<boolean>}
   */
  confirm(title, message, options = {}) {
    return new Promise((resolve) => {
      const modalId = this.show(title, message, {
        ...options,
        confirmButton: options.confirmText || "Confirmar",
        showFooter: true,
      });

      const modal = document.getElementById(modalId);

      // Handle confirm button
      const confirmBtn = modal.querySelector(
        `[data-modal-confirm="${modalId}"]`,
      );
      if (confirmBtn) {
        confirmBtn.addEventListener(
          "click",
          () => {
            this.close(modalId);
            resolve(true);
          },
          { once: true },
        );
      }

      // Handle cancel/close
      modal.addEventListener(
        "modal:closed",
        () => {
          resolve(false);
          setTimeout(() => modal.remove(), 300);
        },
        { once: true },
      );
    });
  }

  /**
   * Alert dialog
   * @param {string} title
   * @param {string} message
   * @param {Object} options
   * @returns {Promise<void>}
   */
  alert(title, message, options = {}) {
    return new Promise((resolve) => {
      const modalId = this.show(title, message, {
        ...options,
        confirmButton: options.confirmText || "OK",
        showFooter: true,
      });

      const modal = document.getElementById(modalId);

      modal.addEventListener(
        "modal:closed",
        () => {
          resolve();
          setTimeout(() => modal.remove(), 300);
        },
        { once: true },
      );
    });
  }
}

// Initialize and export
const ModalManager = new ModalComponent();

// Export for global use
if (typeof window !== "undefined") {
  window.ModalManager = ModalManager;

  // Add to Symplifika namespace
  if (window.Symplifika) {
    window.Symplifika.Modal = ModalManager;
  }
}

export default ModalManager;
