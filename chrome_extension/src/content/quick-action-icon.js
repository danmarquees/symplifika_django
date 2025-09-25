// Sistema de Ícone de Ação Rápida - Symplifika
let state = {
  currentField: null,
  iconElement: null,
  dropdownElement: null,
  shortcuts: [],
  filteredShortcuts: [],
  searchTerm: "",
  isLoading: false,
};

// Criar política TrustedHTML para segurança
let trustedHTMLPolicy = null;
try {
  if (window.trustedTypes && window.trustedTypes.createPolicy) {
    trustedHTMLPolicy = window.trustedTypes.createPolicy(
      "symplifika-quick-action",
      {
        createHTML: (string) => string,
      },
    );
  }
} catch (error) {
  console.warn("TrustedHTML policy não pôde ser criada:", error);
}

// Função helper para criar HTML seguro
function createTrustedHTML(htmlString) {
  if (trustedHTMLPolicy) {
    return trustedHTMLPolicy.createHTML(htmlString);
  }
  return htmlString;
}

// Inicializar
function initQuickActionSystem() {
  createStyles();
  document.addEventListener("focusin", handleFocus, true);
  document.addEventListener("focusout", handleBlur, true);
  document.addEventListener("click", handleDocumentClick, true);
  document.addEventListener("keydown", handleKeyDown, true);
  loadShortcuts();

  // Recarregar atalhos periodicamente
  setInterval(loadShortcuts, 30000); // A cada 30 segundos
}

// Estilos CSS modernos - Alinhados com a aplicação principal
function createStyles() {
  const style = document.createElement("style");
  style.textContent = `
        /* Variáveis CSS do Symplifika */
        :root {
            --symplifika-primary: #00c853;
            --symplifika-secondary: #00ff57;
            --symplifika-accent: #4caf50;
            --gradient-primary: linear-gradient(135deg, #00ff57 0%, #00c853 100%);
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            --shadow-primary: 0 4px 12px rgba(0, 200, 83, 0.3);
            --shadow-primary-lg: 0 8px 20px rgba(0, 200, 83, 0.4);
        }
        
        .symplifika-icon {
            position: fixed;
            width: 32px;
            height: 32px;
            background: var(--gradient-primary);
            border-radius: 50%;
            cursor: pointer;
            z-index: 10000;
            opacity: 0;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            color: white;
            box-shadow: var(--shadow-primary);
            font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            font-weight: 700;
            text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
            border: 2px solid rgba(255, 255, 255, 0.2);
        }
        
        .symplifika-icon:hover {
            transform: scale(1.15) translateY(-2px);
            box-shadow: var(--shadow-primary-lg);
            border-color: rgba(255, 255, 255, 0.4);
        }
        
        .symplifika-icon.visible { 
            opacity: 1; 
            animation: bounceIn 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        }
        
        @keyframes bounceIn {
            0% {
                opacity: 0;
                transform: scale(0.3);
            }
            50% {
                opacity: 1;
                transform: scale(1.05);
            }
            70% {
                transform: scale(0.9);
            }
            100% {
                opacity: 1;
                transform: scale(1);
            }
        }

        .symplifika-dropdown {
            position: fixed;
            background: rgba(255, 255, 255, 0.98);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: 20px;
            box-shadow: var(--shadow-xl);
            z-index: 10001;
            min-width: 360px;
            max-width: 420px;
            max-height: 520px;
            opacity: 0;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid rgba(255, 255, 255, 0.3);
            font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            overflow: hidden;
            transform: translateY(10px) scale(0.95);
        }
        
        .symplifika-dropdown.visible { 
            opacity: 1; 
            transform: translateY(0) scale(1);
        }

        .dropdown-header {
            padding: 20px 24px;
            background: var(--gradient-primary);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            display: flex;
            align-items: center;
            gap: 12px;
            position: relative;
            overflow: hidden;
        }
        
        .dropdown-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
            pointer-events: none;
            opacity: 0.5;
        }
        .dropdown-title {
            font-size: 18px;
            font-weight: 700;
            color: white;
            margin: 0;
            text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
            letter-spacing: -0.025em;
            position: relative;
            z-index: 1;
        }
        
        .dropdown-subtitle {
            font-size: 13px;
            color: rgba(255, 255, 255, 0.9);
            margin: 4px 0 0 0;
            font-weight: 500;
            letter-spacing: 0.025em;
            position: relative;
            z-index: 1;
        }
        
        .dropdown-logo {
            width: 28px;
            height: 28px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 700;
            font-size: 14px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: var(--shadow-sm);
            position: relative;
            z-index: 1;
        }
        .shortcuts-count {
            background: #10b981;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 500;
        }

        .search-container {
            padding: 20px 24px;
            border-bottom: 1px solid rgba(0, 0, 0, 0.05);
            background: rgba(255, 255, 255, 0.5);
        }
        .search-input {
            width: 100%;
            padding: 16px 20px;
            border: 2px solid rgba(0, 0, 0, 0.1);
            border-radius: 12px;
            font-size: 15px;
            font-family: inherit;
            font-weight: 500;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            box-sizing: border-box;
        }
        .search-input:focus {
            outline: none;
            border-color: var(--symplifika-primary);
            background: white;
            box-shadow: 0 0 0 4px rgba(0, 200, 83, 0.1), var(--shadow-md);
            transform: translateY(-1px);
        }

        .shortcuts-container {
            max-height: 360px;
            overflow-y: auto;
            padding: 12px 0;
        }
        
        .shortcuts-container::-webkit-scrollbar {
            width: 6px;
        }
        
        .shortcuts-container::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.05);
            border-radius: 3px;
        }
        
        .shortcuts-container::-webkit-scrollbar-thumb {
            background: rgba(0, 200, 83, 0.3);
            border-radius: 3px;
        }
        
        .shortcuts-container::-webkit-scrollbar-thumb:hover {
            background: rgba(0, 200, 83, 0.5);
        }

        .shortcut-item {
            padding: 16px 24px;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border-bottom: 1px solid rgba(0, 0, 0, 0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 16px;
            position: relative;
        }
        
        .shortcut-item:active {
            background: rgba(0, 200, 83, 0.1);
            transform: translateX(3px) scale(0.98);
        }
        
        .shortcut-item:hover {
            background: rgba(0, 200, 83, 0.05);
            transform: translateX(6px);
            border-left: 3px solid var(--symplifika-primary);
            padding-left: 21px;
        }
        
        .shortcut-item:last-child {
            border-bottom: none;
        }
        
        .shortcut-info {
            flex: 1;
            min-width: 0;
        }

        .shortcut-trigger {
            background: var(--gradient-primary);
            color: white;
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 700;
            font-family: 'JetBrains Mono', 'SF Mono', 'Monaco', 'Courier New', monospace;
            text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
            box-shadow: var(--shadow-md);
            flex-shrink: 0;
            transition: all 0.2s ease;
        }
        
        .shortcut-trigger:hover {
            transform: scale(1.05);
            box-shadow: var(--shadow-lg);
        }
        
        .shortcut-title {
            font-weight: 700;
            color: #111827;
            font-size: 15px;
            margin-bottom: 6px;
            line-height: 1.4;
            letter-spacing: -0.025em;
        }
        
        .shortcut-preview {
            color: #6b7280;
            font-size: 11px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        .shortcut-meta {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-top: 6px;
        }
        
        .shortcut-category {
            background: #eff6ff;
            color: #1d4ed8;
            padding: 1px 6px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 500;
        }
        
        .shortcut-info {
            flex: 1;
            min-width: 0;
        }

        .no-shortcuts {
            padding: 32px 16px;
            text-align: center;
            color: #6b7280;
            font-size: 13px;
        }
        
        .empty-icon {
            font-size: 36px;
            margin-bottom: 16px;
            opacity: 0.7;
        }

        .loading-state {
            padding: 48px 24px;
            text-align: center;
            color: #6b7280;
        }
        
        .loading-spinner {
            width: 28px;
            height: 28px;
            border: 3px solid rgba(0, 0, 0, 0.1);
            border-top: 3px solid var(--symplifika-primary);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 16px;
        }

        .dropdown-footer {
            padding: 12px 16px;
            background: #f8fafc;
            border-top: 1px solid #e5e7eb;
            text-align: center;
        }
        .dropdown-footer-text {
            color: #6b7280;
            font-size: 11px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .shortcut-item.highlighted {
            background: #f0fdf4;
            border-left: 3px solid #10b981;
            padding-left: 13px;
        }
    `;
  document.head.appendChild(style);
}

// Handlers
function handleFocus(e) {
  if (isTextField(e.target)) {
    state.currentField = e.target;
    showIcon(e.target);
  }
}

function handleBlur() {
  setTimeout(() => {
    if (!state.dropdownElement || !state.dropdownElement.matches(":hover")) {
      hideIcon();
    }
  }, 200);
}

function handleDocumentClick(e) {
  if (
    state.iconElement &&
    !state.iconElement.contains(e.target) &&
    state.dropdownElement &&
    !state.dropdownElement.contains(e.target)
  ) {
    hideIcon();
  }
}

function handleKeyDown(e) {
  // Atalho para abrir dropdown: Ctrl + Espaço
  if (e.ctrlKey && e.code === "Space" && state.currentField) {
    e.preventDefault();
    if (!state.dropdownElement) {
      showIcon(state.currentField);
      setTimeout(() => toggleDropdown(), 100);
    } else {
      toggleDropdown();
    }
  }

  // ESC para fechar dropdown
  if (
    e.key === "Escape" &&
    state.dropdownElement &&
    state.dropdownElement.classList.contains("visible")
  ) {
    hideDropdown();
    if (state.currentField) {
      state.currentField.focus();
    }
  }
}

function isTextField(el) {
  if (!el.matches) return false;
  return (
    el.matches('input[type="text"]') ||
    el.matches('input[type="email"]') ||
    el.matches('input[type="search"]') ||
    el.matches("input:not([type])") ||
    el.matches("textarea") ||
    el.matches('[contenteditable="true"]') ||
    el.matches("[contenteditable]")
  );
}

// Mostrar ícone
function showIcon(field) {
  if (!state.iconElement) createIcon();
  const rect = field.getBoundingClientRect();
  const scrollX = window.pageXOffset || document.documentElement.scrollLeft;
  const scrollY = window.pageYOffset || document.documentElement.scrollTop;

  state.iconElement.style.left = `${rect.right - 36 + scrollX}px`;
  state.iconElement.style.top = `${rect.top + 4 + scrollY}px`;
  state.iconElement.classList.add("visible");
}

function hideIcon() {
  if (state.iconElement) state.iconElement.classList.remove("visible");
  hideDropdown();
}

// Criar ícone de ação rápida
function createIcon() {
  const icon = document.createElement("div");
  icon.className = "symplifika-icon";
  icon.innerHTML = createTrustedHTML("✨");
  icon.title = "Atalhos Symplifika (Ctrl+Espaço)";
  icon.onclick = toggleDropdown;
  document.body.appendChild(icon);
  state.iconElement = icon;
}

// Dropdown
function toggleDropdown() {
  if (!state.dropdownElement) {
    createDropdown();
  } else {
    state.dropdownElement.classList.toggle("visible");
  }
}

function hideDropdown() {
  if (state.dropdownElement) {
    state.dropdownElement.classList.remove("visible");
  }
}

function createDropdown() {
  const dropdown = document.createElement("div");
  dropdown.className = "symplifika-dropdown";

  // Posicionar dropdown
  const icon = state.iconElement;
  const iconRect = icon.getBoundingClientRect();
  const scrollX = window.pageXOffset || document.documentElement.scrollLeft;
  const scrollY = window.pageYOffset || document.documentElement.scrollTop;

  let left = Math.max(10, iconRect.left - 300 + scrollX);
  let top = iconRect.bottom + 8 + scrollY;

  // Verificar se o dropdown caberia na tela
  if (left + 320 > window.innerWidth) {
    left = window.innerWidth - 330;
  }

  if (top + 400 > window.innerHeight + scrollY) {
    top = iconRect.top - 408 + scrollY;
  }

  dropdown.style.left = `${left}px`;
  dropdown.style.top = `${top}px`;

  document.body.appendChild(dropdown);
  state.dropdownElement = dropdown;

  renderDropdown();

  // Mostrar dropdown
  requestAnimationFrame(() => {
    dropdown.classList.add("visible");
  });

  // Focar no campo de busca
  setTimeout(() => {
    const searchInput = dropdown.querySelector(".search-input");
    if (searchInput) searchInput.focus();
  }, 300);
}

function renderDropdown() {
  if (!state.dropdownElement) return;

  const activeShortcuts = state.shortcuts.filter((s) => s.is_active !== false);

  state.dropdownElement.innerHTML = createTrustedHTML(`
        <div class="dropdown-header">
            <div class="dropdown-title">✨ Atalhos Disponíveis</div>
            <div class="shortcuts-count">${activeShortcuts.length}</div>
        </div>

        ${
          activeShortcuts.length > 3
            ? `
        <div class="search-container">
            <input type="text" class="search-input" placeholder="Buscar atalhos..." value="${escapeHtml(state.searchTerm)}">
        </div>
        `
            : ""
        }

        <div class="shortcuts-container" id="shortcuts-list">
            ${state.isLoading ? renderLoadingState() : renderShortcuts()}
        </div>

        <div class="dropdown-footer">
            <div class="dropdown-footer-text">Ctrl+Espaço para abrir • ESC para fechar</div>
        </div>
    `);

  // Adicionar event listeners
  const searchInput = state.dropdownElement.querySelector(".search-input");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      state.searchTerm = e.target.value;
      filterAndRenderShortcuts();
    });

    searchInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        const firstShortcut = state.filteredShortcuts[0];
        if (firstShortcut) {
          insertShortcut(firstShortcut.id);
        }
      }
    });
  }
}

function renderLoadingState() {
  return `
        <div class="loading-state">
            <div class="loading-spinner"></div>
            Carregando atalhos...
        </div>
    `;
}

function renderShortcuts() {
  const activeShortcuts = state.shortcuts.filter((s) => s.is_active !== false);

  if (activeShortcuts.length === 0) {
    return `
            <div class="no-shortcuts">
                <div class="no-shortcuts-icon">📝</div>
                <div>Nenhum atalho disponível</div>
                <div style="margin-top: 4px; font-size: 11px;">Crie seus atalhos no painel Symplifika</div>
            </div>
        `;
  }

  // Filtrar e ordenar atalhos
  let filteredShortcuts = activeShortcuts;

  if (state.searchTerm) {
    const searchLower = state.searchTerm.toLowerCase();
    filteredShortcuts = activeShortcuts.filter(
      (s) =>
        s.title.toLowerCase().includes(searchLower) ||
        s.trigger.toLowerCase().includes(searchLower) ||
        (s.content && s.content.toLowerCase().includes(searchLower)),
    );
  }

  // Ordenar por uso e alfabéticamente
  filteredShortcuts.sort((a, b) => {
    if (a.use_count !== b.use_count) {
      return (b.use_count || 0) - (a.use_count || 0);
    }
    return (a.trigger || "").localeCompare(b.trigger || "");
  });

  state.filteredShortcuts = filteredShortcuts;

  if (filteredShortcuts.length === 0) {
    return `
            <div class="no-shortcuts">
                <div class="no-shortcuts-icon">🔍</div>
                <div>Nenhum atalho encontrado</div>
                <div style="margin-top: 4px; font-size: 11px;">Tente outros termos de busca</div>
            </div>
        `;
  }

  return filteredShortcuts
    .map(
      (s) => `
        <div class="shortcut-item" onclick="insertShortcut('${s.id}')" data-shortcut-id="${s.id}">
            <div class="shortcut-trigger">${escapeHtml(s.trigger || "")}</div>
            <div class="shortcut-title">${escapeHtml(s.title || "Sem título")}</div>
            ${s.content ? `<div class="shortcut-preview">${escapeHtml(truncateText(s.content, 80))}</div>` : ""}
            <div class="shortcut-meta">
                ${s.category ? `<div class="shortcut-category">${escapeHtml(s.category.name || s.category)}</div>` : ""}
                ${s.use_count ? `<div class="shortcut-usage">Usado ${s.use_count}x</div>` : ""}
            </div>
        </div>
    `,
    )
    .join("");
}

function filterAndRenderShortcuts() {
  const shortcutsList = document.getElementById("shortcuts-list");
  if (shortcutsList) {
    shortcutsList.innerHTML = createTrustedHTML(renderShortcuts());
  }
}

function truncateText(text, maxLength) {
  if (!text || text.length <= maxLength) return text;
  return text.substring(0, maxLength) + "...";
}

// Função para escapar HTML
function escapeHtml(text) {
  if (!text) return "";
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// Inserir atalho
window.insertShortcut = async function (id) {
  const shortcut = state.shortcuts.find((s) => s.id == id);
  if (!shortcut || !state.currentField) return;

  try {
    let content = shortcut.content;

    // Tentar expandir texto via background script se disponível
    if (isChromeRuntimeAvailable()) {
      try {
        const response = await sendSafeMessage({
          type: "EXPAND_TEXT",
          payload: { trigger: shortcut.trigger },
        });

        if (response && response.success && response.expandedText) {
          content = response.expandedText;
        }

        // Marcar atalho como usado
        sendSafeMessage({
          type: "USE_SHORTCUT",
          payload: { shortcutId: shortcut.id },
        }).catch((err) => console.warn("Erro ao marcar uso:", err));
      } catch (expandError) {
        console.warn(
          "Erro na expansão, usando conteúdo original:",
          expandError,
        );
      }
    }

    // Inserir conteúdo no campo
    insertTextIntoField(state.currentField, content);
    hideDropdown();
    showSuccessFeedback(shortcut.title || shortcut.trigger);

    // Atualizar contador local
    if (shortcut.use_count !== undefined) {
      shortcut.use_count++;
    }
  } catch (error) {
    console.error("Erro ao inserir atalho:", error);
    insertTextIntoField(state.currentField, shortcut.content);
    hideDropdown();
  }
};

// Inserir texto no campo (suporta diferentes tipos)
function insertTextIntoField(field, text) {
  if (!field || !text) return;

  try {
    if (field.value !== undefined) {
      // Input/textarea padrão
      const currentValue = field.value || "";
      const cursorPos = field.selectionStart || currentValue.length;

      const newValue =
        currentValue.substring(0, cursorPos) +
        text +
        currentValue.substring(cursorPos);
      field.value = newValue;

      // Posicionar cursor após o texto inserido
      const newCursorPos = cursorPos + text.length;
      field.setSelectionRange(newCursorPos, newCursorPos);

      // Disparar eventos
      field.dispatchEvent(new Event("input", { bubbles: true }));
      field.dispatchEvent(new Event("change", { bubbles: true }));
    } else if (field.isContentEditable || field.contentEditable === "true") {
      // Elemento contenteditable
      field.focus();

      if (window.getSelection && document.execCommand) {
        // Usar execCommand se disponível (mais compatível)
        document.execCommand("insertText", false, text);
      } else if (window.getSelection) {
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
          const range = selection.getRangeAt(0);
          const textNode = document.createTextNode(text);
          range.insertNode(textNode);

          // Posicionar cursor após o texto
          range.setStartAfter(textNode);
          range.collapse(true);
          selection.removeAllRanges();
          selection.addRange(range);
        }
      } else {
        // Fallback: adicionar no final
        field.innerHTML += escapeHtml(text);
      }

      // Disparar eventos
      field.dispatchEvent(new Event("input", { bubbles: true }));
      field.dispatchEvent(new Event("change", { bubbles: true }));
    }

    // Focar no campo após inserção
    setTimeout(() => {
      if (field.focus) field.focus();
    }, 50);
  } catch (error) {
    console.error("Erro ao inserir texto:", error);
  }
}

// Mostrar feedback de sucesso usando Toast Notifications
function showSuccessFeedback(title) {
  if (window.SymplifIkaToast) {
    window.SymplifIkaToast.success(
      "✨ Atalho Inserido",
      `${title} foi inserido com sucesso!`,
      {
        duration: 3000
      }
    );
  } else {
    // Fallback para o método antigo
    showSuccessFeedbackFallback(title);
  }
}

// Fallback para quando o toast não estiver disponível
function showSuccessFeedbackFallback(title) {
  // Remover feedback anterior se existir
  const existingFeedback = document.querySelector(".symplifika-success-feedback");
  if (existingFeedback) {
    existingFeedback.remove();
  }

  const feedback = document.createElement("div");
  feedback.className = "symplifika-success-feedback";
  feedback.innerHTML = createTrustedHTML(`✨ ${escapeHtml(title)} inserido!`);
  feedback.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 10002;
    background: var(--gradient-primary);
    color: white;
    padding: 16px 20px;
    border-radius: 16px;
    font-size: 14px;
    font-weight: 500;
    box-shadow: var(--shadow-xl);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    animation: slideInRight 0.3s ease-out;
    font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  `;

  document.body.appendChild(feedback);

  setTimeout(() => {
    if (feedback.parentNode) {
      feedback.style.animation = "slideOutRight 0.3s ease-out";
      setTimeout(() => {
        if (feedback.parentNode) {
          feedback.parentNode.removeChild(feedback);
        }
      }, 300);
    }
  }, 3000);
}

// Verificar se chrome.runtime está disponível
function isChromeRuntimeAvailable() {
  return (
    typeof chrome !== "undefined" &&
    chrome.runtime &&
    chrome.runtime.sendMessage &&
    chrome.runtime.id
  );
}

// Enviar mensagem segura
async function sendSafeMessage(message, timeout = 5000) {
  return new Promise((resolve, reject) => {
    if (!isChromeRuntimeAvailable()) {
      reject(new Error("Chrome runtime não disponível"));
      return;
    }

    const timeoutId = setTimeout(() => {
      reject(new Error("Timeout na mensagem"));
    }, timeout);

    try {
      chrome.runtime.sendMessage(message, (response) => {
        clearTimeout(timeoutId);

        if (chrome.runtime.lastError) {
          reject(new Error(chrome.runtime.lastError.message));
          return;
        }

        resolve(response);
      });
    } catch (error) {
      clearTimeout(timeoutId);
      reject(error);
    }
  });
}

// Carregar atalhos
async function loadShortcuts() {
  if (state.isLoading) return;

  state.isLoading = true;

  try {
    if (!isChromeRuntimeAvailable()) {
      console.warn("Chrome runtime não disponível - usando atalhos em cache");
      state.isLoading = false;
      return;
    }

    const response = await sendSafeMessage({ type: "GET_SHORTCUTS" });

    if (response && response.success) {
      const newShortcuts = response.shortcuts || [];

      // Verificar se houve mudanças
      const shortcutsChanged =
        JSON.stringify(state.shortcuts) !== JSON.stringify(newShortcuts);

      state.shortcuts = newShortcuts;
      console.log(`✅ ${state.shortcuts.length} atalhos carregados`);

      // Atualizar dropdown se estiver visível e houve mudanças
      if (
        shortcutsChanged &&
        state.dropdownElement &&
        state.dropdownElement.classList.contains("visible")
      ) {
        renderDropdown();
      }
    } else {
      console.warn("Resposta inválida ao carregar atalhos:", response);
    }
  } catch (error) {
    console.error("Erro ao carregar atalhos:", error);
    // Tentar novamente em 10 segundos
    setTimeout(loadShortcuts, 10000);
  } finally {
    state.isLoading = false;
  }
}

// Inicializar
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initQuickActionSystem);
} else {
  initQuickActionSystem();
}

console.log("✅ Quick Action System v2.0 carregado - Symplifika");
