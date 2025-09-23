/**
 * Ícone de Acesso Rápido - Symplifika Chrome Extension
 * Exibe ícone no hover de campos com 3 atalhos mais relevantes
 */
class QuickAccessIcon {
  constructor(contentScript) {
    this.contentScript = contentScript;
    this.activeIcons = new Map();
    this.tooltipElement = null;
    this.currentField = null;
    this.hideAllTimeout = null;

    if (!this.contentScript) {
      console.error("QuickAccessIcon: contentScript instance is required.");
      return;
    }

    this.init();
  }

  init() {
    this.createTooltip();
    this.observeFields();

    this.tooltipElement.addEventListener('mouseenter', () => this.cancelHideAll());
    this.tooltipElement.addEventListener('mouseleave', () => this.scheduleHideAll());

    document.addEventListener('scroll', () => this.hideAll(true), true);
    document.addEventListener('click', (e) => {
        if (this.tooltipElement && !this.tooltipElement.contains(e.target) && !Array.from(this.activeIcons.values()).some(icon => icon.contains(e.target))) {
            this.hideAll(true);
        }
    });
  }

  createTooltip() {
    if (document.querySelector('.symplifika-tooltip')) {
        this.tooltipElement = document.querySelector('.symplifika-tooltip');
        return;
    }
    this.tooltipElement = document.createElement('div');
    this.tooltipElement.className = 'symplifika-tooltip';
    this.tooltipElement.style.display = 'none';

    this.tooltipElement.innerHTML = `
      <div class="symplifika-tooltip-header">Atalhos Rápidos</div>
      <div class="symplifika-tooltip-shortcuts"></div>
    `;
    document.body.appendChild(this.tooltipElement);
  }

  getFieldSelector() {
    // Seletor expandido para cobrir mais tipos de campos de texto
    return 'input[type="text"], input[type="email"], input[type="search"], input[type="url"], input[type="tel"], textarea, [contenteditable="true"]';
  }

  observeFields() {
    const fields = document.querySelectorAll(this.getFieldSelector());
    fields.forEach(field => this.attachToField(field));
    
    const observer = new MutationObserver(mutations => {
      mutations.forEach(mutation => {
        mutation.addedNodes.forEach(node => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            const newFields = node.matches(this.getFieldSelector()) ? [node] : node.querySelectorAll(this.getFieldSelector());
            newFields.forEach(field => this.attachToField(field));
          }
        });
      });
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  attachToField(field) {
    if (this.activeIcons.has(field) || field.offsetParent === null || field.dataset.symplifikaAttached) return;
    
    field.dataset.symplifikaAttached = 'true';
    const icon = this.createIcon();
    this.activeIcons.set(field, icon);
    
    field.addEventListener('mouseenter', () => {
        this.cancelHideAll();
        this.showIcon(field, icon);
    });
    field.addEventListener('mouseleave', () => this.scheduleHideAll());
    
    icon.addEventListener('mouseenter', () => {
        this.cancelHideAll();
    });
    icon.addEventListener('mouseleave', () => {
        this.scheduleHideAll();
    });
    icon.addEventListener('click', (e) => {
        e.stopPropagation();
        this.cancelHideAll();

        // Alterna a visibilidade do tooltip. Se já estiver visível para este campo, esconde.
        if (this.tooltipElement.classList.contains('visible') && this.currentField === field) {
            this.hideAll(true);
        } else {
            this.showTooltip(field, icon);
        }
    });
  }

  createIcon() {
    const icon = document.createElement('div');
    icon.className = 'symplifika-icon';
    icon.style.display = 'none';
    icon.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24"><path d="M13 10V3L4 14h7v7l9-11h-7z" fill="currentColor"/></svg>';
    document.body.appendChild(icon);
    return icon;
  }

  showIcon(field, icon) {
    if (!this.contentScript.isEnabled || !this.contentScript.isAuthenticated) return;
    if (field.type === 'password') return;
    
    const rect = field.getBoundingClientRect();
    // Don't show on very small fields
    if (rect.height < 20 || rect.width < 50) return;

    icon.style.position = 'fixed';
    icon.style.top = `${rect.top + (rect.height / 2) - (icon.offsetHeight / 2)}px`;
    icon.style.left = `${rect.right - icon.offsetWidth - 5}px`;
    icon.style.display = 'flex';
  }

  async showTooltip(field, icon) {
    this.cancelHideAll();
    this.currentField = field;
    const shortcuts = (this.contentScript.shortcuts || []).slice(0, 3);
    
    if (shortcuts.length === 0) {
        // Optionally show a message or just don't show the tooltip
        return;
    }
    
    const shortcutsHtml = shortcuts.slice(0, 3).map(shortcut => 
      `<div class="shortcut-item" data-id="${shortcut.id}">
        <span class="trigger">${shortcut.trigger}</span>
        <span class="title">${shortcut.title}</span>
      </div>`
    ).join('');
    
    this.tooltipElement.querySelector('.symplifika-tooltip-shortcuts').innerHTML = shortcutsHtml;
    
    this.tooltipElement.style.position = 'fixed';
    this.tooltipElement.style.display = 'block';

    const iconRect = icon.getBoundingClientRect();
    const tooltipRect = this.tooltipElement.getBoundingClientRect();
    
    let top = iconRect.top + (iconRect.height / 2) - (tooltipRect.height / 2);
    let left = iconRect.left - tooltipRect.width - 10;

    // Adjust if it goes off-screen
    if (left < 10) left = iconRect.right + 10;
    if (top < 10) top = 10;
    if (top + tooltipRect.height > window.innerHeight - 10) top = window.innerHeight - 10 - tooltipRect.height;

    this.tooltipElement.style.top = `${top}px`;
    this.tooltipElement.style.left = `${left}px`;
    
    this.tooltipElement.classList.add('visible');

    this.tooltipElement.querySelectorAll('.shortcut-item').forEach(item => {
      item.addEventListener('click', () => {
        const shortcut = shortcuts.find(s => s.id == item.dataset.id);
        if (shortcut) {
            this.contentScript.expandShortcut(this.currentField, shortcut.trigger, shortcut);
        }
        this.hideAll(true);
      });
    });
  }

  getFieldContext(field) {
    const placeholder = field.placeholder || '';
    const label = field.labels?.[0]?.textContent || '';
    const name = field.name || '';
    return (placeholder + ' ' + label + ' ' + name).toLowerCase();
  }

  scheduleHideAll() {
    this.cancelHideAll();
    this.hideAllTimeout = setTimeout(() => {
        this.hideAll();
    }, 300);
  }

  cancelHideAll() {
    clearTimeout(this.hideAllTimeout);
  }

  hideAll(immediate = false) {
    if (this.tooltipElement) {
        this.tooltipElement.classList.remove('visible');
        
        const hideCompletely = () => {
            // Garante que o tooltip não voltou a ser visível antes de escondê-lo
            if (!this.tooltipElement.classList.contains('visible')) {
                this.tooltipElement.style.display = 'none';
            }
        };

        if (immediate) {
            hideCompletely();
        } else {
            // Esconde o elemento do DOM após a transição de 200ms do CSS (ver content.css)
            setTimeout(hideCompletely, 200);
        }
    }
    this.activeIcons.forEach(icon => {
        icon.style.display = 'none';
    });
    this.cancelHideAll();
  }
}
