/**
 * Ícone de Acesso Rápido - Symplifika Chrome Extension
 * Exibe ícone clicável ao lado de campos de texto com tooltip de atalhos
 * Last updated: 2025-09-23 02:52:00 - Fixed this.log binding issues
 */
class QuickAccessIcon {
  constructor(contentScript) {
    this.contentScript = contentScript;
    this.activeIcons = new Map();
    this.tooltipElement = null;
    this.currentField = null;
    this.hideAllTimeout = null;
    this.showTooltipPromise = null;
    this.showTooltipController = null;
    this.mutationObserver = null;
    this.cleanupInterval = null;
    this.isDestroyed = false;

    if (!this.contentScript) {
      console.error("QuickAccessIcon: contentScript instance is required.");
      return;
    }

    this.init();

    // Inicialização automática imediata
    this.autoInitialize();

    // Iniciar manutenção de ícones ativos
    setTimeout(() => this.maintainActiveFieldIcons(), 1000);

    // Expor funções de debug no console global
    if (typeof window !== "undefined") {
      window.symplifikaDebug = {
        showTextFieldIcons: () => this.debugShowIconsInTextFields(),
        listActiveIcons: () => this.debugListActiveIcons(),
        toggleAllIcons: () => this.debugToggleAllIcons(),
        forceShowAll: () => this.showAllIcons(),
        hideAll: (immediate = false) => this.hideAll(immediate),
        getActiveIconsCount: () => this.activeIcons.size,
        isEnabled: () => this.contentScript?.isEnabled || false,
        isAuthenticated: () => this.contentScript?.isAuthenticated || false,
        testCopyNotification: (
          title = "Teste",
          content = "Conteúdo de teste copiado!",
        ) => this.showCopyNotification(title, content),
      };
      console.log(
        "[QuickAccessIcon] Debug functions available at window.symplifikaDebug",
      );
    }
  }

  init() {
    if (this.isDestroyed) return;

    try {
      this.createTooltip();
      this.observeFields();
      this.setupGlobalListeners();
      this.startCleanupInterval();

      // Forçar processamento inicial após DOM estar pronto
      if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", () => {
          this.forceInitialScan();
        });
      } else {
        this.forceInitialScan();
      }
    } catch (error) {
      console.error("Error initializing QuickAccessIcon:", error);
    }
  }

  autoInitialize() {
    // Inicialização automática em múltiplos momentos para garantir cobertura
    const initTimes = [100, 500, 1000, 2000]; // ms

    initTimes.forEach((delay) => {
      setTimeout(() => {
        if (!this.isDestroyed) {
          this.forceInitialScan();
        }
      }, delay);
    });
  }

  forceInitialScan() {
    console.log("[QuickAccessIcon] Executando scan de campos...");

    // Buscar todos os campos visíveis
    const allFields = document.querySelectorAll(this.getFieldSelector());
    const visibleFields = Array.from(allFields).filter((field) =>
      this.isValidField(field),
    );

    console.log(
      `[QuickAccessIcon] Encontrados ${visibleFields.length} campos válidos`,
    );

    // Processar cada campo
    visibleFields.forEach((field) => {
      if (!this.activeIcons.has(field)) {
        this.attachToField(field);
      }
    });

    // Mostrar ícones imediatamente para campos focados
    const focusedField = document.activeElement;
    if (focusedField && this.isValidField(focusedField)) {
      const icon = this.activeIcons.get(focusedField);
      if (icon) {
        this.showIcon(focusedField, icon);
      }
    }
  }

  setupGlobalListeners() {
    // Listener para esconder tooltip ao sair com mouse
    this.tooltipElement.addEventListener("mouseenter", () =>
      this.cancelHideAll(),
    );
    this.tooltipElement.addEventListener("mouseleave", () =>
      this.scheduleHideAll(),
    );

    // Listener para scroll - esconder ícones ao rolar página
    document.addEventListener("scroll", () => this.hideAll(true), {
      passive: true,
      capture: true,
    });

    // Listener para cliques fora - esconder tooltip
    document.addEventListener("click", (e) => {
      if (
        this.tooltipElement &&
        !this.tooltipElement.contains(e.target) &&
        !Array.from(this.activeIcons.values()).some((icon) =>
          icon.contains(e.target),
        )
      ) {
        this.hideAll(true);
      }
    });

    // Listener para resize - reposicionar elementos
    window.addEventListener(
      "resize",
      () => {
        if (
          this.tooltipElement &&
          this.tooltipElement.classList.contains("visible")
        ) {
          this.hideAll(true);
        }
      },
      { passive: true },
    );

    // Listener para keyboard shortcuts globais
    document.addEventListener("keydown", (e) => {
      // Alt + S para mostrar tooltip no campo ativo
      if (e.altKey && e.key === "s" && document.activeElement) {
        const activeElement = document.activeElement;
        if (
          this.isValidField(activeElement) &&
          this.activeIcons.has(activeElement)
        ) {
          e.preventDefault();
          const icon = this.activeIcons.get(activeElement);
          this.showTooltip(activeElement, icon);
        }
      }

      // Escape para esconder tooltip
      if (e.key === "Escape") {
        this.hideAll(true);
      }
    });
  }

  createTooltip() {
    // Verificar se já existe para evitar duplicação
    const existing = document.querySelector(".symplifika-tooltip");
    if (existing) {
      this.tooltipElement = existing;
      return;
    }

    this.tooltipElement = document.createElement("div");
    this.tooltipElement.className = "symplifika-tooltip";
    this.tooltipElement.style.display = "none";
    this.tooltipElement.setAttribute("role", "tooltip");
    this.tooltipElement.setAttribute("aria-label", "Lista de atalhos rápidos");

    // Criar estrutura interna de forma segura
    const header = document.createElement("div");
    header.className = "symplifika-tooltip-header";
    header.textContent = "Atalhos Rápidos";

    const shortcuts = document.createElement("div");
    shortcuts.className = "symplifika-tooltip-shortcuts";
    shortcuts.setAttribute("role", "list");

    this.tooltipElement.appendChild(header);
    this.tooltipElement.appendChild(shortcuts);
    document.body.appendChild(this.tooltipElement);
  }

  getFieldSelector() {
    return [
      'input[type="text"]',
      'input[type="email"]',
      'input[type="search"]',
      'input[type="url"]',
      'input[type="tel"]',
      'input[type="number"]',
      "input:not([type])", // Input sem type definido
      "textarea",
      '[contenteditable="true"]',
      '[contenteditable=""]',
      '[role="textbox"]',
      'input[type="password"]', // Incluir password mas tratar diferente
      // Campos específicos do Google Workspace
      'div[contenteditable="true"]',
      'div[role="textbox"]',
      // Campos do Gmail, LinkedIn, etc.
      'div[aria-label*="compose"]',
      'div[aria-label*="message"]',
      'div[aria-label*="post"]',
      'div[aria-label*="comment"]',
      // Editores WYSIWYG comuns
      ".ql-editor", // Quill
      ".fr-element", // FroalaEditor
      ".note-editable", // Summernote
      ".cke_editable", // CKEditor
    ].join(", ");
  }

  isValidField(field) {
    if (!field) return false;

    // Priorizar campos de texto comum (textarea, text, email, etc.)
    const isTextInputField =
      field.type === "text" ||
      field.type === "email" ||
      field.type === "search" ||
      field.type === "tel" ||
      field.type === "url" ||
      field.tagName.toLowerCase() === "textarea";

    // Permitir password fields mas marcar como sensível
    const isSensitive =
      field.type === "password" ||
      field.autocomplete === "current-password" ||
      field.autocomplete === "new-password";

    // Campos explicitamente ignorados
    if (field.dataset.symplifikaIgnore === "true") return false;

    // Verificar visibilidade
    if (field.style.display === "none" || field.offsetParent === null)
      return false;

    // Verificar se é muito pequeno (provavelmente campo oculto)
    const rect = field.getBoundingClientRect();
    if (rect.width < 30 || rect.height < 20) return false;

    // Verificar se não está dentro de um elemento oculto
    let parent = field.parentElement;
    while (parent && parent !== document.body) {
      if (
        parent.style.display === "none" ||
        parent.style.visibility === "hidden" ||
        parent.hidden
      ) {
        return false;
      }
      parent = parent.parentElement;
    }

    // Campos sensíveis são válidos mas terão comportamento diferente
    field.dataset.symplifikaSensitive = isSensitive ? "true" : "false";

    // Ser mais permissivo para campos de texto comuns
    const minHeight = isTextInputField ? 25 : 20;
    const minWidth = isTextInputField ? 60 : 50;

    return rect.height >= minHeight && rect.width >= minWidth;
  }

  observeFields() {
    // Processar campos existentes imediatamente
    const existingFields = document.querySelectorAll(this.getFieldSelector());
    const validFields = Array.from(existingFields).filter((field) =>
      this.isValidField(field),
    );
    console.log(
      `[QuickAccessIcon] Processando ${validFields.length} campos existentes`,
    );
    this.processBatch(validFields);

    // Throttled handler para novos elementos
    let observerTimer = null;

    const processNewElements = (mutations) => {
      if (this.isDestroyed) return;

      clearTimeout(observerTimer);
      observerTimer = setTimeout(() => {
        const newFields = new Set(); // Use Set para evitar duplicatas

        mutations.forEach((mutation) => {
          mutation.addedNodes.forEach((node) => {
            if (node.nodeType === Node.ELEMENT_NODE) {
              if (node.matches && node.matches(this.getFieldSelector())) {
                newFields.add(node);
              } else if (node.querySelectorAll) {
                const childFields = node.querySelectorAll(
                  this.getFieldSelector(),
                );
                childFields.forEach((field) => newFields.add(field));
              }
            }
          });
        });

        if (newFields.size > 0) {
          this.processBatch(Array.from(newFields));
        }
      }, 150); // Debounce otimizado
    };

    this.mutationObserver = new MutationObserver(processNewElements);
    this.mutationObserver.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: false, // Otimização: não observar mudanças de atributos
      characterData: false, // Otimização: não observar mudanças de texto
    });
  }

  processBatch(fields) {
    // Processar elementos em batches para não bloquear a UI
    const BATCH_SIZE = 8;
    let index = 0;

    const processNextBatch = () => {
      if (this.isDestroyed) return;

      const endIndex = Math.min(index + BATCH_SIZE, fields.length);
      for (let i = index; i < endIndex; i++) {
        if (this.isValidField(fields[i])) {
          this.attachToField(fields[i]);
        }
      }
      index = endIndex;

      if (index < fields.length) {
        requestAnimationFrame(processNextBatch);
      }
    };

    if (fields.length > 0) {
      requestAnimationFrame(processNextBatch);
    }
  }

  attachToField(field) {
    if (this.isDestroyed) return;
    if (
      this.activeIcons.has(field) ||
      field.dataset.symplifikaAttached === "true"
    )
      return;
    if (!this.isValidField(field)) return;

    try {
      field.dataset.symplifikaAttached = "true";
      const icon = this.createIcon();
      this.activeIcons.set(field, icon);

      // Determinar se é um campo de texto comum
      const isTextInputField =
        field.type === "text" ||
        field.type === "email" ||
        field.type === "search" ||
        field.type === "tel" ||
        field.type === "url" ||
        field.tagName.toLowerCase() === "textarea";

      // Event listeners otimizados
      const mouseEnterHandler = () => {
        if (!this.isDestroyed) {
          this.cancelHideAll();
          this.showIcon(field, icon);
        }
      };

      const mouseLeaveHandler = () => {
        if (!this.isDestroyed && !field.matches(":focus")) {
          this.scheduleHideAll();
        }
      };

      const focusHandler = () => {
        if (
          !this.isDestroyed &&
          this.contentScript.isEnabled &&
          this.contentScript.isAuthenticated
        ) {
          this.showIcon(field, icon);
        }
      };

      const clickHandler = () => {
        if (
          !this.isDestroyed &&
          this.contentScript.isEnabled &&
          this.contentScript.isAuthenticated &&
          isTextInputField
        ) {
          // Para campos de texto, mostrar ícone imediatamente no click
          setTimeout(() => this.showIcon(field, icon), 100);
        }
      };

      field.addEventListener("mouseenter", mouseEnterHandler, {
        passive: true,
      });
      field.addEventListener("mouseleave", mouseLeaveHandler, {
        passive: true,
      });
      field.addEventListener("focus", focusHandler, { passive: true });
      field.addEventListener("click", clickHandler, { passive: true });

      // Para campos de texto, mostrar ícone em diferentes situações
      if (isTextInputField) {
        const inputHandler = () => {
          if (
            !this.isDestroyed &&
            this.contentScript.isEnabled &&
            this.contentScript.isAuthenticated
          ) {
            // Mostrar ícone após qualquer digitação ou quando há texto
            if (field.value.length > 0 || document.activeElement === field) {
              this.showIcon(field, icon);
            }
          }
        };

        const keydownHandler = (e) => {
          if (
            !this.isDestroyed &&
            this.contentScript.isEnabled &&
            this.contentScript.isAuthenticated &&
            (e.ctrlKey || e.metaKey || e.altKey || field.value.length > 1)
          ) {
            // Mostrar ícone quando usar atalhos de teclado ou há conteúdo
            setTimeout(() => this.showIcon(field, icon), 50);
          }
        };

        field.addEventListener("input", inputHandler, { passive: true });
        field.addEventListener("keydown", keydownHandler, { passive: true });

        // Armazenar referências adicionais para cleanup
        field._symplifikaTextHandlers = {
          input: inputHandler,
          keydown: keydownHandler,
        };
      }

      // Armazenar referências dos handlers para cleanup posterior
      field._symplifikaHandlers = {
        mouseEnter: mouseEnterHandler,
        mouseLeave: mouseLeaveHandler,
        focus: focusHandler,
        click: clickHandler,
      };
    } catch (error) {
      console.error("Error attaching to field:", error);
    }
  }

  createIcon() {
    const icon = document.createElement("button");
    icon.className = "symplifika-icon";
    icon.type = "button";
    icon.style.display = "none";

    // Acessibilidade completa
    icon.setAttribute("role", "button");
    icon.setAttribute("aria-label", "Mostrar atalhos rápidos disponíveis");
    icon.setAttribute("tabindex", "0");
    icon.title = "Clique para ver atalhos disponíveis (Alt+S)";

    // Criar SVG com ícone de expansão de texto mais intuitivo
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("width", "18");
    svg.setAttribute("height", "18");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("aria-hidden", "true");

    // Ícone que representa expansão/atalhos de texto
    const path1 = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "path",
    );
    path1.setAttribute("d", "M3 17h18v2H3zm0-6h12v2H3zm0-6h18v2H3z");
    path1.setAttribute("fill", "currentColor");
    path1.setAttribute("opacity", "0.8");

    const path2 = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "path",
    );
    path2.setAttribute("d", "M16 11l3-3-3-3v2H8v2h8v2z");
    path2.setAttribute("fill", "currentColor");

    svg.appendChild(path1);
    svg.appendChild(path2);
    icon.appendChild(svg);

    // Event listeners para o ícone
    icon.addEventListener(
      "mouseenter",
      () => {
        if (!this.isDestroyed) this.cancelHideAll();
      },
      { passive: true },
    );

    icon.addEventListener(
      "mouseleave",
      () => {
        if (!this.isDestroyed) this.scheduleHideAll();
      },
      { passive: true },
    );

    icon.addEventListener("click", (e) => {
      e.stopPropagation();
      e.preventDefault();
      if (this.isDestroyed) return;

      this.cancelHideAll();

      // Encontrar o campo associado ao ícone
      const field = this.findFieldForIcon(icon);
      if (field) {
        // Alternar visibilidade do tooltip
        if (
          this.tooltipElement.classList.contains("visible") &&
          this.currentField === field
        ) {
          this.hideAll(true);
        } else {
          this.showTooltip(field, icon);
        }
      }
    });

    // Suporte a keyboard
    icon.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        icon.click();
      }
    });

    document.body.appendChild(icon);
    return icon;
  }

  findFieldForIcon(icon) {
    for (const [field, fieldIcon] of this.activeIcons.entries()) {
      if (fieldIcon === icon) return field;
    }
    return null;
  }

  showIcon(field, icon) {
    if (this.isDestroyed) return;
    if (!this.contentScript.isEnabled || !this.contentScript.isAuthenticated)
      return;
    if (!this.isValidField(field)) return;

    try {
      const rect = field.getBoundingClientRect();
      const iconSize = 30;

      // Verificar se é campo de texto para mostrar de forma mais persistente
      const isTextInputField =
        field.type === "text" ||
        field.type === "email" ||
        field.type === "search" ||
        field.type === "tel" ||
        field.type === "url" ||
        field.tagName.toLowerCase() === "textarea";

      // Posicionamento inteligente
      const position = this.calculateIconPosition(rect, iconSize);

      // Aplicar estilos com animação suave e maior visibilidade
      icon.style.cssText = `
        position: fixed;
        top: ${position.top}px;
        left: ${position.left}px;
        display: flex;
        z-index: 999999;
        opacity: 0;
        transform: scale(0.8) translateY(5px);
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        pointer-events: auto;
        will-change: transform, opacity;
      `;

      // Animar entrada com efeito mais chamativo
      requestAnimationFrame(() => {
        icon.style.opacity = "1";
        icon.style.transform = "scale(1) translateY(0)";
      });

      // Garantir que esteja sempre visível quando necessário
      icon.dataset.visible = "true";
      icon.dataset.fieldType = isTextInputField ? "text" : "other";

      // Para campos de texto, manter visível por mais tempo
      if (isTextInputField) {
        icon.dataset.persistentShow = "true";
        clearTimeout(this.persistentTimer);
        this.persistentTimer = setTimeout(() => {
          if (!field.matches(":focus") && !field.matches(":hover")) {
            delete icon.dataset.persistentShow;
          }
        }, 3000); // Manter visível por 3 segundos em campos de texto
      }

      console.log(
        `[QuickAccessIcon] Ícone exibido para campo ${field.tagName} (${field.type || "N/A"}) em posição (${position.top}, ${position.left})`,
      );
    } catch (error) {
      console.error("Error showing icon:", error);
    }
  }

  calculateIconPosition(fieldRect, iconSize) {
    // Determinar o tipo de campo para posicionamento otimizado
    const isTextarea = fieldRect.height > 50;
    const isWideField = fieldRect.width > 200;

    // Posição inicial baseada no tipo de campo
    let top, left;

    if (isTextarea) {
      // Para textarea: canto superior direito, mais visível
      top = fieldRect.top + 6;
      left = fieldRect.right - iconSize - 6;
    } else {
      // Para campos de linha única: centro vertical, lado direito
      top = fieldRect.top + fieldRect.height / 2 - iconSize / 2;
      left = fieldRect.right - iconSize - 6;
    }

    // Se o campo for muito estreito, posicionar do lado externo
    if (fieldRect.width < iconSize + 24) {
      left = fieldRect.right + 8;
      // Garantir espaço mínimo à direita
      if (left + iconSize > window.innerWidth - 15) {
        left = fieldRect.left - iconSize - 8; // Lado esquerdo
      }
    }

    // Ajustes para viewport
    const viewport = {
      width: window.innerWidth,
      height: window.innerHeight,
    };

    const margin = 12;

    // Ajustar horizontalmente se necessário
    if (left < margin) {
      left = fieldRect.right + 8;
    }
    if (left + iconSize > viewport.width - margin) {
      left = Math.max(margin, fieldRect.left - iconSize - 8);
    }

    // Ajustar verticalmente se necessário
    if (top < margin) {
      top = margin;
    }
    if (top + iconSize > viewport.height - margin) {
      top = Math.max(margin, viewport.height - iconSize - margin);
    }

    // Para campos muito pequenos, usar posição externa mais visível
    if (fieldRect.width < 100 || fieldRect.height < 25) {
      left = fieldRect.right + 12;
      top = fieldRect.top + Math.max(0, (fieldRect.height - iconSize) / 2);
    }

    return { top: Math.round(top), left: Math.round(left) };
  }

  async showTooltip(field, icon) {
    if (this.isDestroyed) return;

    // Cancelar operação anterior para evitar race conditions
    if (this.showTooltipPromise && this.showTooltipController) {
      this.showTooltipController.abort();
    }

    this.showTooltipController = new AbortController();

    try {
      await this._showTooltipInternal(
        field,
        icon,
        this.showTooltipController.signal,
      );
    } catch (error) {
      if (error.name !== "AbortError") {
        console.error("Error showing tooltip:", error);
      }
    }
  }

  async _showTooltipInternal(field, icon, signal) {
    this.cancelHideAll();
    this.currentField = field;

    // Verificar se a operação foi cancelada
    if (signal.aborted)
      throw new DOMException("Operation aborted", "AbortError");

    // Verificar se é um campo sensível
    const isSensitive = field.dataset.symplifikaSensitive === "true";

    if (isSensitive) {
      this.showSensitiveFieldWarning();
      return;
    }

    // Mostrar estado de carregamento
    this.showLoadingState();

    try {
      // Buscar atalhos mais usados do backend
      const shortcuts = await this.getRelevantShortcuts();

      if (signal.aborted) return;

      if (shortcuts.length === 0) {
        this.showEmptyState();
        return;
      }

      // Limpar conteúdo anterior e criar novos elementos de forma segura
      this.createShortcutElements(shortcuts, signal);

      if (signal.aborted) return;

      // Posicionar tooltip
      this.positionTooltip(icon);

      // Mostrar tooltip com animação
      this.tooltipElement.style.display = "block";
      requestAnimationFrame(() => {
        if (!signal.aborted && !this.isDestroyed) {
          this.tooltipElement.classList.add("visible");
          this.tooltipElement.classList.remove("loading");
        }
      });
    } catch (error) {
      if (!signal.aborted) {
        console.error("Error loading shortcuts:", error);
        this.showErrorState();
      }
    }
  }

  createShortcutElements(shortcuts, signal) {
    const container = this.tooltipElement.querySelector(
      ".symplifika-tooltip-shortcuts",
    );

    // Limpar conteúdo anterior
    while (container.firstChild) {
      container.removeChild(container.firstChild);
    }

    // Adicionar cabeçalho se há atalhos contextuais
    const currentUrl = window.location.hostname.toLowerCase();
    const contextualShortcuts = shortcuts.filter((s) => s.relevanceScore > 50);

    if (contextualShortcuts.length > 0) {
      const header = document.createElement("div");
      header.className = "shortcuts-header";
      header.innerHTML = `
        <div style="display: flex; align-items: center; margin-bottom: 8px; padding-bottom: 6px; border-bottom: 1px solid #e5e7eb;">
          <svg width="12" height="12" viewBox="0 0 24 24" style="margin-right: 6px; color: #00c853;">
            <path fill="currentColor" d="M12 2L13.09 7.26L18 9L13.09 10.74L12 16L10.91 10.74L6 9L10.91 7.26L12 2Z"/>
          </svg>
          <span style="font-size: 11px; font-weight: 600; color: #00c853;">Sugeridos para ${currentUrl}</span>
        </div>
      `;
      container.appendChild(header);
    }

    // Adicionar header informativo sobre as ações
    const actionsHeader = document.createElement("div");
    actionsHeader.className = "actions-info-header";
    actionsHeader.innerHTML = `
      <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; padding: 8px 12px; background: rgba(0, 200, 83, 0.05); border-radius: 6px; border: 1px solid rgba(0, 200, 83, 0.1);">
        <div style="display: flex; align-items: center; gap: 8px;">
          <svg width="14" height="14" viewBox="0 0 24 24" style="color: #00c853;">
            <path fill="currentColor" d="M11,9H13V7H11M12,20C7.59,20 4,16.41 4,12C4,7.59 7.59,4 12,4C16.41,4 20,7.59 20,12C20,16.41 16.41,20 12,20M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M11,17H13V11H11V17Z"/>
          </svg>
          <span style="font-size: 11px; font-weight: 600; color: #00c853;">Como usar</span>
        </div>
        <div style="font-size: 10px; color: #6b7280; line-height: 1.3;">
          <div>🖱️ Clique: Copiar</div>
          <div>⌨️ Ctrl+Clique: Inserir</div>
        </div>
      </div>
    `;
    container.appendChild(actionsHeader);

    shortcuts.forEach((shortcut, index) => {
      if (signal && signal.aborted) return;

      // Validar dados do atalho vindo do backend
      if (!shortcut || !shortcut.id) return;

      const item = document.createElement("div");
      item.className = "shortcut-item";
      if (shortcut.relevanceScore > 50) {
        item.classList.add("contextual");
      }
      item.setAttribute("role", "listitem");
      item.setAttribute("tabindex", "0");
      item.dataset.shortcutId = String(shortcut.id);
      item.setAttribute(
        "aria-label",
        `Atalho: ${shortcut.trigger || shortcut.title} - ${shortcut.title}`,
      );

      // Criar container principal do item
      const mainContent = document.createElement("div");
      mainContent.style.cssText =
        "display: flex; align-items: center; width: 100%;";

      // Criar estrutura do item
      const trigger = document.createElement("span");
      trigger.className = "trigger";
      trigger.textContent = shortcut.trigger || `#${shortcut.id}`;
      trigger.setAttribute("aria-hidden", "true");

      // Adicionar indicador de contexto visual
      if (shortcut.relevanceScore > 50) {
        trigger.style.cssText += `
          background: linear-gradient(135deg, #00c853, #00ff57);
          border-color: #00c853;
          color: white;
          font-weight: 600;
        `;
      }

      const contentArea = document.createElement("div");
      contentArea.style.cssText = "flex: 1; margin-left: 12px; min-width: 0;";

      const title = document.createElement("div");
      title.className = "title";
      title.textContent = shortcut.title || "Atalho sem título";
      title.setAttribute("aria-hidden", "true");
      title.style.cssText += "display: flex; align-items: center;";

      // Adicionar badges informativos
      const badgesContainer = document.createElement("div");
      badgesContainer.style.cssText =
        "display: flex; gap: 4px; margin-left: 8px;";

      // Badge de categoria
      if (shortcut.category && shortcut.category.name) {
        const category = document.createElement("span");
        category.className = "category-badge";
        category.textContent = shortcut.category.name;
        category.style.cssText = `
          font-size: 9px;
          color: #6b7280;
          background: #f3f4f6;
          padding: 2px 4px;
          border-radius: 3px;
          font-weight: 500;
        `;
        badgesContainer.appendChild(category);
      }

      // Badge de uso frequente
      if (shortcut.use_count > 10) {
        const hotBadge = document.createElement("span");
        hotBadge.innerHTML = "🔥";
        hotBadge.style.cssText = "font-size: 10px;";
        hotBadge.title = `Usado ${shortcut.use_count} vezes`;
        badgesContainer.appendChild(hotBadge);
      }

      // Badge de tipo de expansão
      if (shortcut.expansion_type === "ai_enhanced") {
        const aiBadge = document.createElement("span");
        aiBadge.innerHTML = "✨";
        aiBadge.style.cssText = "font-size: 10px;";
        aiBadge.title = "IA Enhanced";
        badgesContainer.appendChild(aiBadge);
      } else if (shortcut.expansion_type === "dynamic") {
        const dynamicBadge = document.createElement("span");
        dynamicBadge.innerHTML = "⚡";
        dynamicBadge.style.cssText = "font-size: 10px;";
        dynamicBadge.title = "Dinâmico";
        badgesContainer.appendChild(dynamicBadge);
      }

      title.appendChild(badgesContainer);

      // Adicionar preview do conteúdo mais informativo
      if (shortcut.content) {
        const preview = document.createElement("div");
        preview.className = "content-preview";

        // Criar preview mais inteligente
        let previewText = shortcut.content.substring(0, 80);
        if (shortcut.content.length > 80) {
          previewText += "...";
        }

        // Destacar variáveis se for dinâmico
        if (shortcut.expansion_type === "dynamic") {
          previewText = previewText.replace(
            /\{([^}]+)\}/g,
            '<span style="color: #00c853; font-weight: 500;">{$1}</span>',
          );
          preview.innerHTML = previewText;
        } else {
          preview.textContent = previewText;
        }

        preview.style.cssText = `
          font-size: 11px;
          color: #6b7280;
          margin-top: 4px;
          line-height: 1.3;
          overflow: hidden;
          text-overflow: ellipsis;
        `;
        contentArea.appendChild(title);
        contentArea.appendChild(preview);
      } else {
        contentArea.appendChild(title);
      }

      mainContent.appendChild(trigger);
      mainContent.appendChild(contentArea);
      item.appendChild(mainContent);
      container.appendChild(item);

      // Adicionar indicador visual de que é clicável
      const actionIndicator = document.createElement("div");
      actionIndicator.style.cssText = `
        position: absolute;
        top: 8px;
        right: 8px;
        font-size: 10px;
        color: #9ca3af;
        opacity: 0;
        transition: opacity 0.2s ease;
        pointer-events: none;
        text-align: right;
        line-height: 1.2;
      `;
      actionIndicator.innerHTML = `
        <div>Clique: Copiar</div>
        <div>Ctrl+Clique: Inserir</div>
      `;
      item.appendChild(actionIndicator);

      // Event listener para clique - copia por padrão, insere com Ctrl/Cmd
      const clickHandler = async (e) => {
        e.preventDefault();
        e.stopPropagation();

        if (e.ctrlKey || e.metaKey) {
          // Ctrl/Cmd + Click: Inserir no campo
          await this.handleShortcutClick(shortcut);
        } else {
          // Click normal: Copiar para clipboard
          await this.copyShortcutToClipboard(shortcut, item);
        }
      };

      item.addEventListener("click", clickHandler);

      // Mostrar indicador no hover
      item.addEventListener("mouseenter", () => {
        actionIndicator.style.opacity = "1";
      });

      item.addEventListener("mouseleave", () => {
        actionIndicator.style.opacity = "0";
      });

      // Suporte a keyboard
      item.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          clickHandler(e);
        }
      });
    });
  }

  sanitizeShortcut(shortcut) {
    if (!shortcut || typeof shortcut !== "object") return null;

    // Validar campos obrigatórios
    if (!shortcut.id) return null;

    // Retornar objeto shortcut com campos padronizados
    return {
      id: parseInt(shortcut.id) || 0,
      trigger: shortcut.trigger || `#${shortcut.id}`,
      title: shortcut.title || "Atalho sem título",
      content: shortcut.content || "",
      category: shortcut.category || null,
    };
  }

  async handleShortcutClick(shortcut) {
    if (this.isDestroyed || !this.currentField) return;

    try {
      // Expandir atalho usando o backend
      const expandedContent = await this.expandShortcutWithVariables(shortcut);

      if (expandedContent) {
        // Inserir conteúdo expandido no campo
        this.insertTextIntoField(this.currentField, expandedContent);

        // Marcar como usado para analytics
        this.markShortcutAsUsed(shortcut.id);

        // Mostrar feedback de sucesso
        this.showSuccessFeedback();
      } else {
        // Fallback: inserir conteúdo bruto se expansão falhar
        const content = shortcut.content || shortcut.trigger || shortcut.title;
        this.insertTextIntoField(this.currentField, content);
        this.showErrorFeedback();
      }

      // Esconder tooltip após inserção
      this.hideAll(true);

      // Focar no campo após inserção
      if (this.currentField && typeof this.currentField.focus === "function") {
        this.currentField.focus();
      }
    } catch (error) {
      console.error("Error applying shortcut:", error);
      this.showErrorFeedback();
    }
  }

  async copyShortcutToClipboard(shortcut, cardElement) {
    if (!shortcut) return;

    try {
      // Adicionar classe visual temporária
      cardElement.classList.add("copying");

      // Expandir atalho usando o backend se possível
      let contentToCopy;
      try {
        contentToCopy = await this.expandShortcutWithVariables(shortcut);
      } catch (error) {
        console.warn("Failed to expand shortcut, using raw content:", error);
      }

      // Fallback para conteúdo bruto
      if (!contentToCopy) {
        contentToCopy = shortcut.content || shortcut.trigger || shortcut.title;
      }

      // Copiar para clipboard
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(contentToCopy);
      } else {
        // Fallback para navegadores mais antigos
        const textArea = document.createElement("textarea");
        textArea.value = contentToCopy;
        textArea.style.cssText =
          "position: fixed; top: -999px; left: -999px; opacity: 0;";
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        document.execCommand("copy");
        document.body.removeChild(textArea);
      }

      // Feedback visual no card
      cardElement.classList.remove("copying");
      cardElement.classList.add("copied");
      setTimeout(() => {
        cardElement.classList.remove("copied");
      }, 1500);

      // Mostrar notificação
      this.showCopyNotification(shortcut.title, contentToCopy);

      // Marcar como usado para analytics
      this.markShortcutAsUsed(shortcut.id);

      console.log(`[QuickAccessIcon] Atalho copiado: ${shortcut.title}`);

      // Não esconder tooltip ao copiar (apenas ao inserir)
    } catch (error) {
      console.error("Error copying to clipboard:", error);
      cardElement.classList.remove("copying");
      this.showCopyErrorNotification();
    }
  }

  showCopyNotification(title, content) {
    // Remover notificação anterior se existir
    const existingNotification = document.querySelector(".copy-notification");
    if (existingNotification) {
      existingNotification.remove();
    }

    // Criar nova notificação
    const notification = document.createElement("div");
    notification.className = "copy-notification";

    // Truncar conteúdo para exibição
    const displayContent =
      content.length > 50 ? content.substring(0, 47) + "..." : content;

    notification.innerHTML = `
      <svg class="icon" viewBox="0 0 24 24">
        <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
      </svg>
      <div class="message">
        <div style="font-weight: 600;">📋 ${title}</div>
        <div style="font-size: 12px; opacity: 0.9; margin-top: 2px;">Copiado: ${displayContent}</div>
      </div>
    `;

    document.body.appendChild(notification);

    // Animar entrada
    requestAnimationFrame(() => {
      notification.classList.add("show");
    });

    // Remover após 3 segundos
    setTimeout(() => {
      notification.classList.remove("show");
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
      }, 300);
    }, 3000);
  }

  showCopyErrorNotification() {
    // Remover notificação anterior se existir
    const existingNotification = document.querySelector(".copy-notification");
    if (existingNotification) {
      existingNotification.remove();
    }

    // Criar notificação de erro
    const notification = document.createElement("div");
    notification.className = "copy-notification";
    notification.style.background =
      "linear-gradient(135deg, #ef4444 0%, #f87171 100%)";
    notification.innerHTML = `
      <svg class="icon" viewBox="0 0 24 24">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
      </svg>
      <div class="message">
        <div style="font-weight: 600;">❌ Erro ao copiar</div>
        <div style="font-size: 12px; opacity: 0.9; margin-top: 2px;">Tente novamente</div>
      </div>
    `;

    document.body.appendChild(notification);

    // Animar entrada
    requestAnimationFrame(() => {
      notification.classList.add("show");
    });

    // Remover após 2 segundos
    setTimeout(() => {
      notification.classList.remove("show");
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
      }, 300);
    }, 2000);
  }

  positionTooltip(icon) {
    if (!icon || !this.tooltipElement) return;

    try {
      const iconRect = icon.getBoundingClientRect();

      // Força o tooltip a ser renderizado para obter suas dimensões reais
      this.tooltipElement.style.visibility = "hidden";
      this.tooltipElement.style.display = "block";
      const tooltipRect = this.tooltipElement.getBoundingClientRect();
      this.tooltipElement.style.visibility = "visible";

      const position = this.calculateOptimalPosition(iconRect, tooltipRect);

      this.tooltipElement.style.position = "fixed";
      this.tooltipElement.style.top = `${position.top}px`;
      this.tooltipElement.style.left = `${position.left}px`;
      this.tooltipElement.style.zIndex = "1000000";
    } catch (error) {
      console.error("Error positioning tooltip:", error);
    }
  }

  calculateOptimalPosition(iconRect, tooltipRect) {
    const viewport = {
      width: window.innerWidth,
      height: window.innerHeight,
    };

    const margin = 10;

    // Posições possíveis em ordem de preferência
    const positions = [
      // Esquerda do ícone (preferencial)
      {
        top: iconRect.top + iconRect.height / 2 - tooltipRect.height / 2,
        left: iconRect.left - tooltipRect.width - margin,
        priority: 1,
      },
      // Direita do ícone
      {
        top: iconRect.top + iconRect.height / 2 - tooltipRect.height / 2,
        left: iconRect.right + margin,
        priority: 2,
      },
      // Acima do ícone
      {
        top: iconRect.top - tooltipRect.height - margin,
        left: iconRect.left + iconRect.width / 2 - tooltipRect.width / 2,
        priority: 3,
      },
      // Abaixo do ícone
      {
        top: iconRect.bottom + margin,
        left: iconRect.left + iconRect.width / 2 - tooltipRect.width / 2,
        priority: 4,
      },
    ];

    // Filtrar posições que cabem na viewport
    const validPositions = positions.filter(
      (pos) =>
        pos.left >= margin &&
        pos.left + tooltipRect.width <= viewport.width - margin &&
        pos.top >= margin &&
        pos.top + tooltipRect.height <= viewport.height - margin,
    );

    // Retornar a melhor posição ou ajustar para caber na tela
    if (validPositions.length > 0) {
      return validPositions.sort((a, b) => a.priority - b.priority)[0];
    }

    // Fallback: centralizar o melhor possível
    const fallback = positions[0];
    fallback.left = Math.max(
      margin,
      Math.min(fallback.left, viewport.width - tooltipRect.width - margin),
    );
    fallback.top = Math.max(
      margin,
      Math.min(fallback.top, viewport.height - tooltipRect.height - margin),
    );

    return fallback;
  }

  scheduleHideAll() {
    if (this.isDestroyed) return;

    this.cancelHideAll();
    this.hideAllTimeout = setTimeout(() => {
      if (!this.isDestroyed) {
        this.hideAll();
      }
    }, 300);
  }

  cancelHideAll() {
    if (this.hideAllTimeout) {
      clearTimeout(this.hideAllTimeout);
      this.hideAllTimeout = null;
    }
  }

  hideAll(immediate = false) {
    if (this.isDestroyed) return;

    // Safety check for this binding
    if (!this.activeIcons || !this.tooltipElement) {
      console.warn("[QuickAccessIcon] hideAll called with invalid context");
      return;
    }

    try {
      // Esconder tooltip
      if (this.tooltipElement) {
        this.tooltipElement.classList.remove("visible");

        const hideTooltip = () => {
          if (
            !this.isDestroyed &&
            !this.tooltipElement.classList.contains("visible")
          ) {
            this.tooltipElement.style.display = "none";
          }
        };

        if (immediate) {
          hideTooltip();
        } else {
          setTimeout(hideTooltip, 200); // Aguarda animação CSS
        }
      }

      // Esconder ícones, respeitando persistência em campos de texto
      this.activeIcons.forEach((icon, field) => {
        if (icon && icon.style) {
          // Verificar se deve manter visível para campos de texto
          const shouldKeepVisible =
            !immediate &&
            icon.dataset.persistentShow === "true" &&
            (field.matches(":focus") ||
              field.matches(":hover") ||
              field.value.length > 0);

          if (!shouldKeepVisible) {
            icon.style.opacity = "0";
            icon.style.transform = "scale(0.8) translateY(5px)";
            setTimeout(
              () => {
                if (!this.isDestroyed && icon.style.opacity === "0") {
                  icon.style.display = "none";
                }
              },
              immediate ? 0 : 200,
            );
          } else {
            console.log(
              "[QuickAccessIcon] Mantendo ícone visível para campo de texto em foco",
            );
          }
        }
      });

      if (this.cancelHideAll && typeof this.cancelHideAll === "function") {
        this.cancelHideAll();
        if (immediate) {
          this.currentField = null;
        }

        console.log(
          `[QuickAccessIcon] Elements hidden (immediate: ${immediate})`,
        );
      }
    } catch (error) {
      console.error("Error hiding elements:", error);
    }
  }

  // Função para mostrar ícone imediatamente (para debugging)
  forceShowIcon(field) {
    if (!field) {
      console.log("Nenhum campo fornecido");
      return;
    }

    let icon = this.activeIcons.get(field);
    if (!icon) {
      console.log("Criando ícone para campo...");
      icon = this.createIcon();
      this.activeIcons.set(field, icon);
      field.dataset.fieldId = Date.now().toString();
      icon.dataset.fieldId = field.dataset.fieldId;
    }

    this.showIcon(field, icon);
    console.log("Ícone forçado para campo:", field);
  }

  // Função para testar ícones em todos os campos visíveis
  showAllIcons() {
    const fields = document.querySelectorAll(this.getFieldSelector());
    let count = 0;

    fields.forEach((field) => {
      if (this.isValidField(field)) {
        this.forceShowIcon(field);
        count++;
      }
    });

    console.log(`[QuickAccessIcon] Mostrando ícones em ${count} campos`);
    return count;
  }

  // Função para manter ícones visíveis em campos de texto ativos
  maintainActiveFieldIcons() {
    if (this.isDestroyed) return;

    // Verificar campos que estão em foco ou têm conteúdo
    this.activeIcons.forEach((icon, field) => {
      const isTextInputField =
        field.type === "text" ||
        field.type === "email" ||
        field.type === "search" ||
        field.type === "tel" ||
        field.type === "url" ||
        field.tagName.toLowerCase() === "textarea";

      if (isTextInputField) {
        const shouldMaintainVisible =
          field.matches(":focus") ||
          field.matches(":hover") ||
          field.value.length > 0 ||
          document.activeElement === field;

        if (shouldMaintainVisible && icon.style.display === "none") {
          // Reexibir ícone se necessário
          this.showIcon(field, icon);
        } else if (
          !shouldMaintainVisible &&
          icon.dataset.persistentShow !== "true"
        ) {
          // Esconder gradualmente se não há razão para manter visível
          setTimeout(() => {
            if (
              !field.matches(":focus") &&
              !field.matches(":hover") &&
              field.value.length === 0
            ) {
              icon.style.opacity = "0";
              icon.style.transform = "scale(0.8) translateY(5px)";
              setTimeout(() => {
                if (icon.style.opacity === "0") {
                  icon.style.display = "none";
                }
              }, 200);
            }
          }, 1000);
        }
      }
    });

    // Executar novamente em 2 segundos
    if (!this.isDestroyed) {
      setTimeout(() => this.maintainActiveFieldIcons(), 2000);
    }
  }

  // Funções de debug para testar o ícone
  debugShowIconsInTextFields() {
    const textFields = document.querySelectorAll(
      'input[type="text"], input[type="email"], input[type="search"], textarea',
    );
    let count = 0;

    textFields.forEach((field) => {
      if (this.isValidField(field)) {
        this.attachToField(field);
        this.forceShowIcon(field);
        count++;
      }
    });

    console.log(`[DEBUG] Showing icons in ${count} text fields`);
    return count;
  }

  debugListActiveIcons() {
    console.log(`[DEBUG] Active icons: ${this.activeIcons.size}`);
    this.activeIcons.forEach((icon, field) => {
      console.log(`- Field: ${field.tagName} (${field.type || "N/A"})`, {
        visible: icon.style.display !== "none",
        persistent: icon.dataset.persistentShow === "true",
        fieldValue:
          field.value.substring(0, 20) + (field.value.length > 20 ? "..." : ""),
        position: `${icon.style.top}, ${icon.style.left}`,
      });
    });
  }

  debugToggleAllIcons() {
    let hiddenCount = 0;
    let shownCount = 0;

    this.activeIcons.forEach((icon, field) => {
      if (icon.style.display === "none") {
        this.showIcon(field, icon);
        shownCount++;
      } else {
        icon.style.display = "none";
        hiddenCount++;
      }
    });

    console.log(
      `[DEBUG] Toggled icons: ${shownCount} shown, ${hiddenCount} hidden`,
    );
  }

  startCleanupInterval() {
    // Limpeza automática a cada 30 segundos
    this.cleanupInterval = setInterval(() => {
      if (!this.isDestroyed) {
        this.cleanupOrphanedElements();
      }
    }, 30000);
  }

  cleanupOrphanedElements() {
    if (this.isDestroyed) return;

    let cleanedCount = 0;

    // Limpar campos órfãos do Map
    this.activeIcons.forEach((icon, field) => {
      if (!document.body.contains(field)) {
        // Remover ícone do DOM
        if (icon && icon.parentNode) {
          icon.parentNode.removeChild(icon);
        }

        // Limpar event listeners se existirem
        if (field._symplifikaHandlers) {
          delete field._symplifikaHandlers;
        }

        // Remover do map
        this.activeIcons.delete(field);
        cleanedCount++;
      }
    });
  }

  // Método público para destruir a instância
  destroy() {
    if (this.isDestroyed) return;

    this.isDestroyed = true;

    try {
      // Parar observadores
      if (this.mutationObserver) {
        this.mutationObserver.disconnect();
        this.mutationObserver = null;
      }

      // Limpar intervalos
      if (this.cleanupInterval) {
        clearInterval(this.cleanupInterval);
        this.cleanupInterval = null;
      }

      // Cancelar operações pendentes
      this.cancelHideAll();
      if (this.showTooltipController) {
        this.showTooltipController.abort();
      }

      // Remover todos os ícones
      this.activeIcons.forEach((icon) => {
        if (icon && icon.parentNode) {
          icon.parentNode.removeChild(icon);
        }
      });
      this.activeIcons.clear();

      // Remover tooltip
      if (this.tooltipElement && this.tooltipElement.parentNode) {
        this.tooltipElement.parentNode.removeChild(this.tooltipElement);
      }
    } catch (error) {
      console.error("Error during destruction:", error);
    }
  }

  // Métodos públicos para controle externo
  enable() {
    // Extensão habilitada
  }

  disable() {
    this.hideAll(true);
  }

  // Método para refresh manual
  refresh() {
    if (this.isDestroyed) return;

    this.cleanupOrphanedElements();
    const existingFields = document.querySelectorAll(this.getFieldSelector());
    this.processBatch(Array.from(existingFields));
  }

  // Função de teste para debug - REMOVER EM PRODUÇÃO
  forceTestIcon() {
    // Bypass temporário das verificações de autenticação
    const originalIsEnabled = this.contentScript.isEnabled;
    const originalIsAuthenticated = this.contentScript.isAuthenticated;

    this.contentScript.isEnabled = true;
    this.contentScript.isAuthenticated = true;

    // Encontrar primeiro campo de texto válido
    const fields = document.querySelectorAll(this.getFieldSelector());

    if (fields.length > 0) {
      const field = fields[0];

      // Forçar anexar ícone
      if (!this.activeIcons.has(field)) {
        this.attachToField(field);
      }

      // Forçar mostrar ícone
      const icon = this.activeIcons.get(field);
      if (icon) {
        this.showIcon(field, icon);

        // Destacar o campo para facilitar identificação
        field.style.border = "2px solid red";
        field.style.backgroundColor = "#ffe6e6";

        setTimeout(() => {
          field.style.border = "";
          field.style.backgroundColor = "";
        }, 3000);
      }
    }

    // Restaurar valores originais após teste
    setTimeout(() => {
      this.contentScript.isEnabled = originalIsEnabled;
      this.contentScript.isAuthenticated = originalIsAuthenticated;
    }, 5000);
  }

  insertTextIntoField(field, text) {
    if (!field || !text) return;

    try {
      if (field.contentEditable === "true") {
        // Para elementos contenteditable
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
          const range = selection.getRangeAt(0);
          range.deleteContents();
          range.insertNode(document.createTextNode(text));
          range.collapse(false);
        } else {
          field.textContent += text;
        }
      } else {
        // Para inputs e textareas
        const startPos = field.selectionStart || 0;
        const endPos = field.selectionEnd || 0;
        const beforeText = field.value.substring(0, startPos);
        const afterText = field.value.substring(endPos);

        field.value = beforeText + text + afterText;
        field.selectionStart = field.selectionEnd = startPos + text.length;
      }

      // Disparar evento de input para notificar mudanças
      field.dispatchEvent(new Event("input", { bubbles: true }));
      field.dispatchEvent(new Event("change", { bubbles: true }));

      // Focar no campo
      field.focus();
    } catch (error) {
      console.error("Error inserting text:", error);
    }
  }

  showSuccessFeedback() {
    this.createFeedbackElement("✅ Atalho inserido!", "#10b981");
  }

  showErrorFeedback() {
    this.createFeedbackElement("❌ Erro ao inserir atalho", "#ef4444");
  }

  createFeedbackElement(message, color) {
    // Remover feedback anterior se existir
    const existingFeedback = document.querySelector(
      ".symplifika-feedback-toast",
    );
    if (existingFeedback) {
      existingFeedback.remove();
    }

    const feedback = document.createElement("div");
    feedback.className = "symplifika-feedback-toast";
    feedback.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: ${color};
      color: white;
      padding: 12px 16px;
      border-radius: 8px;
      font-size: 14px;
      font-family: system-ui, -apple-system, sans-serif;
      z-index: 2147483647;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      animation: slideIn 0.3s ease-out;
    `;
    feedback.textContent = message;

    // Adicionar animação se não existir
    if (!document.querySelector("#symplifika-feedback-animation")) {
      const style = document.createElement("style");
      style.id = "symplifika-feedback-animation";
      style.textContent = `
        @keyframes slideIn {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
      `;
      document.head.appendChild(style);
    }

    document.body.appendChild(feedback);

    // Remover após 3 segundos
    setTimeout(() => {
      if (feedback.parentNode) {
        feedback.style.animation = "slideIn 0.3s ease-out reverse";
        setTimeout(() => {
          feedback.remove();
        }, 300);
      }
    }, 3000);
  }

  async getRelevantShortcuts() {
    try {
      // Obter contexto da URL atual para sugestões contextuais
      const currentUrl = window.location.hostname.toLowerCase();

      // Buscar todos os atalhos ativos
      const response = await chrome.runtime.sendMessage({
        action: "getShortcuts",
      });

      if (!response || !response.shortcuts || response.shortcuts.length === 0) {
        return [];
      }

      let shortcuts = response.shortcuts
        .filter((shortcut) => shortcut.is_active !== false)
        .map((shortcut) => ({
          ...shortcut,
          relevanceScore: this.calculateRelevanceScore(shortcut, currentUrl),
        }))
        .sort((a, b) => b.relevanceScore - a.relevanceScore);

      // Se não temos atalhos contextuais, mostrar os mais usados
      if (shortcuts.every((s) => s.relevanceScore === 0)) {
        shortcuts = shortcuts.sort(
          (a, b) => (b.use_count || 0) - (a.use_count || 0),
        );
      }

      // Retornar os 8 mais relevantes para melhor experiência
      return shortcuts.slice(0, 8);
    } catch (error) {
      console.error("Erro ao buscar atalhos:", error);
      return [];
    }
  }

  calculateRelevanceScore(shortcut, currentUrl) {
    let score = 0;

    // Pontuação por contexto de URL
    if (shortcut.url_context) {
      const shortcutDomain = shortcut.url_context
        .replace(/^https?:\/\//, "")
        .replace(/^www\./, "")
        .split("/")[0]
        .toLowerCase();

      if (
        currentUrl.includes(shortcutDomain) ||
        shortcutDomain.includes(currentUrl)
      ) {
        score += 100; // Alta relevância por contexto
      }
    }

    // Pontuação por uso frequente
    const useCount = shortcut.use_count || 0;
    score += Math.min(useCount * 2, 50); // Máximo 50 pontos por uso

    // Pontuação por uso recente
    if (shortcut.last_used) {
      const daysSinceUsed =
        (Date.now() - new Date(shortcut.last_used)) / (1000 * 60 * 60 * 24);
      if (daysSinceUsed < 7) {
        score += 20 - daysSinceUsed * 2; // Máximo 20 pontos se usado na última semana
      }
    }

    return Math.max(0, score);
  }

  showSensitiveFieldWarning() {
    // Limpar conteúdo do tooltip
    const container = this.tooltipElement.querySelector(
      ".symplifika-tooltip-shortcuts",
    );
    while (container.firstChild) {
      container.removeChild(container.firstChild);
    }

    // Criar aviso para campo sensível
    const warning = document.createElement("div");
    warning.style.cssText = `
      padding: 20px;
      text-align: center;
      color: #dc2626;
      background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
    `;

    warning.innerHTML = `
      <div style="margin-bottom: 12px; font-size: 24px;">🔒</div>
      <div style="font-weight: 600; margin-bottom: 8px; font-size: 14px;">Campo Sensível Detectado</div>
      <div style="font-size: 12px; line-height: 1.4; color: #991b1b;">
        Por segurança, atalhos não são exibidos<br>em campos de senha ou similares.
      </div>
    `;

    container.appendChild(warning);

    // Posicionar e mostrar tooltip
    this.positionTooltip(
      document.querySelector(
        `button[data-field-id="${this.currentField.dataset.fieldId}"]`,
      ),
    );

    this.tooltipElement.style.display = "block";
    requestAnimationFrame(() => {
      if (!this.isDestroyed) {
        this.tooltipElement.classList.add("visible");
        this.tooltipElement.classList.remove("loading");
      }
    });

    // Auto-hide após 3 segundos
    setTimeout(() => {
      if (!this.isDestroyed) {
        this.hideAll(true);
      }
    }, 3000);
  }

  async expandShortcutWithVariables(shortcut) {
    try {
      const response = await chrome.runtime.sendMessage({
        action: "useShortcut",
        shortcutId: shortcut.id,
        variables: {}, // Por enquanto sem variáveis, implementar modal depois
      });

      return response && response.content ? response.content : null;
    } catch (error) {
      console.error("Error expanding shortcut:", error);
      return null;
    }
  }

  async markShortcutAsUsed(shortcutId) {
    try {
      // Marcar como usado no backend para analytics
      await chrome.runtime.sendMessage({
        action: "useShortcut",
        shortcutId: shortcutId,
        variables: {},
      });
    } catch (error) {
      console.error("Error marking shortcut as used:", error);
    }
  }

  showLoadingState() {
    const shortcutsContainer = this.tooltipElement.querySelector(
      ".symplifika-tooltip-shortcuts",
    );

    if (shortcutsContainer) {
      shortcutsContainer.innerHTML = `
        <div class="loading-state">
          <div class="loading-spinner"></div>
          <span>Carregando atalhos...</span>
        </div>
      `;
    }

    this.tooltipElement.classList.add("loading");
    this.tooltipElement.style.display = "block";
    this.positionTooltip(null);
  }

  showEmptyState() {
    const shortcutsContainer = this.tooltipElement.querySelector(
      ".symplifika-tooltip-shortcuts",
    );

    if (shortcutsContainer) {
      shortcutsContainer.innerHTML = `
        <div class="empty-state">
          <span>📝 Nenhum atalho encontrado</span>
          <small>Crie atalhos na plataforma Symplifika</small>
        </div>
      `;
    }

    this.tooltipElement.classList.remove("loading");
    this.tooltipElement.style.display = "block";

    // Auto-hide após 2 segundos
    setTimeout(() => {
      this.hideAll(true);
    }, 2000);
  }

  showErrorState() {
    const shortcutsContainer = this.tooltipElement.querySelector(
      ".symplifika-tooltip-shortcuts",
    );

    if (shortcutsContainer) {
      shortcutsContainer.innerHTML = `
        <div class="error-state">
          <span>❌ Erro ao carregar atalhos</span>
          <small>Verifique sua conexão</small>
        </div>
      `;
    }

    this.tooltipElement.classList.remove("loading");
    this.tooltipElement.style.display = "block";

    // Auto-hide após 3 segundos
    setTimeout(() => {
      this.hideAll(true);
    }, 3000);
  }
}
