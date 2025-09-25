// Sistema de Toast Notifications para Symplifika Chrome Extension
// Alinhado com o design moderno da aplicação principal

class SymplifIkaToast {
  constructor() {
    this.container = null;
    this.toasts = [];
    this.maxToasts = 5;
    this.defaultDuration = 4000;
    this.init();
  }

  init() {
    this.createContainer();
    this.createStyles();
  }

  createContainer() {
    if (this.container) return;

    this.container = document.createElement('div');
    this.container.className = 'symplifika-toast-container';
    this.container.setAttribute('data-symplifika-toast', 'true');
    document.body.appendChild(this.container);
  }

  createStyles() {
    if (document.querySelector('[data-symplifika-toast-styles]')) return;

    const style = document.createElement('style');
    style.setAttribute('data-symplifika-toast-styles', 'true');
    style.textContent = `
      /* Variáveis CSS do Symplifika - Toast Notifications */
      :root {
        --symplifika-primary: #00c853;
        --symplifika-secondary: #00ff57;
        --gradient-primary: linear-gradient(135deg, #00ff57 0%, #00c853 100%);
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
      }

      .symplifika-toast-container {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 999999;
        pointer-events: none;
        display: flex;
        flex-direction: column;
        gap: 12px;
        max-width: 400px;
      }

      .symplifika-toast {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 16px;
        padding: 16px 20px;
        box-shadow: var(--shadow-xl);
        border: 1px solid rgba(255, 255, 255, 0.3);
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 14px;
        font-weight: 500;
        line-height: 1.5;
        pointer-events: auto;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        transform: translateX(100%);
        opacity: 0;
        display: flex;
        align-items: flex-start;
        gap: 12px;
        min-width: 320px;
        max-width: 400px;
        word-wrap: break-word;
        position: relative;
        overflow: hidden;
      }

      .symplifika-toast.show {
        transform: translateX(0);
        opacity: 1;
      }

      .symplifika-toast.hide {
        transform: translateX(100%);
        opacity: 0;
      }

      .symplifika-toast:hover {
        transform: translateX(-4px) scale(1.02);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
      }

      .symplifika-toast-icon {
        font-size: 20px;
        flex-shrink: 0;
        margin-top: 2px;
      }

      .symplifika-toast-content {
        flex: 1;
        min-width: 0;
      }

      .symplifika-toast-title {
        font-weight: 700;
        font-size: 15px;
        margin-bottom: 4px;
        letter-spacing: -0.025em;
        line-height: 1.3;
      }

      .symplifika-toast-message {
        font-weight: 500;
        font-size: 13px;
        line-height: 1.4;
        opacity: 0.9;
      }

      .symplifika-toast-close {
        position: absolute;
        top: 12px;
        right: 12px;
        width: 24px;
        height: 24px;
        border: none;
        background: rgba(0, 0, 0, 0.1);
        border-radius: 50%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        font-weight: 700;
        color: rgba(0, 0, 0, 0.6);
        transition: all 0.2s ease;
        opacity: 0.7;
      }

      .symplifika-toast-close:hover {
        background: rgba(0, 0, 0, 0.2);
        opacity: 1;
        transform: scale(1.1);
      }

      .symplifika-toast-progress {
        position: absolute;
        bottom: 0;
        left: 0;
        height: 3px;
        background: var(--gradient-primary);
        border-radius: 0 0 16px 16px;
        transition: width linear;
        opacity: 0.8;
      }

      /* Tipos de Toast */
      .symplifika-toast.success {
        border-left: 4px solid #10b981;
      }

      .symplifika-toast.success .symplifika-toast-icon {
        color: #10b981;
      }

      .symplifika-toast.success .symplifika-toast-title {
        color: #065f46;
      }

      .symplifika-toast.success .symplifika-toast-progress {
        background: linear-gradient(90deg, #10b981, #059669);
      }

      .symplifika-toast.error {
        border-left: 4px solid #ef4444;
      }

      .symplifika-toast.error .symplifika-toast-icon {
        color: #ef4444;
      }

      .symplifika-toast.error .symplifika-toast-title {
        color: #991b1b;
      }

      .symplifika-toast.error .symplifika-toast-progress {
        background: linear-gradient(90deg, #ef4444, #dc2626);
      }

      .symplifika-toast.warning {
        border-left: 4px solid #f59e0b;
      }

      .symplifika-toast.warning .symplifika-toast-icon {
        color: #f59e0b;
      }

      .symplifika-toast.warning .symplifika-toast-title {
        color: #92400e;
      }

      .symplifika-toast.warning .symplifika-toast-progress {
        background: linear-gradient(90deg, #f59e0b, #d97706);
      }

      .symplifika-toast.info {
        border-left: 4px solid #3b82f6;
      }

      .symplifika-toast.info .symplifika-toast-icon {
        color: #3b82f6;
      }

      .symplifika-toast.info .symplifika-toast-title {
        color: #1e40af;
      }

      .symplifika-toast.info .symplifika-toast-progress {
        background: linear-gradient(90deg, #3b82f6, #2563eb);
      }

      /* Animações */
      @keyframes slideInRight {
        from {
          transform: translateX(100%);
          opacity: 0;
        }
        to {
          transform: translateX(0);
          opacity: 1;
        }
      }

      @keyframes slideOutRight {
        from {
          transform: translateX(0);
          opacity: 1;
        }
        to {
          transform: translateX(100%);
          opacity: 0;
        }
      }

      @keyframes pulse {
        0%, 100% {
          transform: scale(1);
        }
        50% {
          transform: scale(1.05);
        }
      }

      /* Responsividade */
      @media (max-width: 480px) {
        .symplifika-toast-container {
          top: 10px;
          right: 10px;
          left: 10px;
          max-width: none;
        }

        .symplifika-toast {
          min-width: auto;
          max-width: none;
        }
      }
    `;
    document.head.appendChild(style);
  }

  show(options = {}) {
    const {
      type = 'info',
      title = '',
      message = '',
      duration = this.defaultDuration,
      persistent = false,
      onClick = null
    } = options;

    // Limitar número de toasts
    if (this.toasts.length >= this.maxToasts) {
      this.remove(this.toasts[0]);
    }

    const toast = this.createToast(type, title, message, duration, persistent, onClick);
    this.container.appendChild(toast.element);
    this.toasts.push(toast);

    // Animar entrada
    setTimeout(() => {
      toast.element.classList.add('show');
    }, 10);

    // Auto-remover se não for persistente
    if (!persistent && duration > 0) {
      toast.timeout = setTimeout(() => {
        this.remove(toast);
      }, duration);

      // Animar barra de progresso
      const progressBar = toast.element.querySelector('.symplifika-toast-progress');
      if (progressBar) {
        progressBar.style.width = '100%';
        setTimeout(() => {
          progressBar.style.width = '0%';
          progressBar.style.transition = `width ${duration}ms linear`;
        }, 50);
      }
    }

    return toast;
  }

  createToast(type, title, message, duration, persistent, onClick) {
    const toastElement = document.createElement('div');
    toastElement.className = `symplifika-toast ${type}`;

    const icons = {
      success: '✅',
      error: '❌',
      warning: '⚠️',
      info: 'ℹ️'
    };

    const icon = icons[type] || icons.info;

    toastElement.innerHTML = `
      <div class="symplifika-toast-icon">${icon}</div>
      <div class="symplifika-toast-content">
        ${title ? `<div class="symplifika-toast-title">${title}</div>` : ''}
        <div class="symplifika-toast-message">${message}</div>
      </div>
      <button class="symplifika-toast-close" type="button">×</button>
      ${!persistent && duration > 0 ? '<div class="symplifika-toast-progress"></div>' : ''}
    `;

    const toast = {
      element: toastElement,
      type,
      title,
      message,
      duration,
      persistent,
      timeout: null
    };

    // Event listeners
    const closeBtn = toastElement.querySelector('.symplifika-toast-close');
    closeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      this.remove(toast);
    });

    if (onClick) {
      toastElement.addEventListener('click', onClick);
      toastElement.style.cursor = 'pointer';
    }

    // Pausar timer no hover
    if (!persistent && duration > 0) {
      toastElement.addEventListener('mouseenter', () => {
        if (toast.timeout) {
          clearTimeout(toast.timeout);
          const progressBar = toastElement.querySelector('.symplifika-toast-progress');
          if (progressBar) {
            progressBar.style.animationPlayState = 'paused';
          }
        }
      });

      toastElement.addEventListener('mouseleave', () => {
        const remainingTime = this.getRemainingTime(toastElement);
        if (remainingTime > 0) {
          toast.timeout = setTimeout(() => {
            this.remove(toast);
          }, remainingTime);
          const progressBar = toastElement.querySelector('.symplifika-toast-progress');
          if (progressBar) {
            progressBar.style.animationPlayState = 'running';
          }
        }
      });
    }

    return toast;
  }

  getRemainingTime(toastElement) {
    const progressBar = toastElement.querySelector('.symplifika-toast-progress');
    if (!progressBar) return 0;

    const computedStyle = window.getComputedStyle(progressBar);
    const currentWidth = parseFloat(computedStyle.width);
    const totalWidth = parseFloat(computedStyle.maxWidth || progressBar.parentElement.offsetWidth);
    const percentage = currentWidth / totalWidth;
    
    return Math.max(0, percentage * this.defaultDuration);
  }

  remove(toast) {
    if (!toast || !toast.element) return;

    // Limpar timeout
    if (toast.timeout) {
      clearTimeout(toast.timeout);
    }

    // Animar saída
    toast.element.classList.add('hide');
    toast.element.classList.remove('show');

    setTimeout(() => {
      if (toast.element && toast.element.parentNode) {
        toast.element.parentNode.removeChild(toast.element);
      }
      this.toasts = this.toasts.filter(t => t !== toast);
    }, 300);
  }

  removeAll() {
    this.toasts.forEach(toast => this.remove(toast));
  }

  // Métodos de conveniência
  success(title, message, options = {}) {
    return this.show({ ...options, type: 'success', title, message });
  }

  error(title, message, options = {}) {
    return this.show({ ...options, type: 'error', title, message });
  }

  warning(title, message, options = {}) {
    return this.show({ ...options, type: 'warning', title, message });
  }

  info(title, message, options = {}) {
    return this.show({ ...options, type: 'info', title, message });
  }
}

// Instância global
window.SymplifIkaToast = window.SymplifIkaToast || new SymplifIkaToast();

// Export para uso em módulos
if (typeof module !== 'undefined' && module.exports) {
  module.exports = SymplifIkaToast;
}
