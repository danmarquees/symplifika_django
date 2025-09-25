// Content Script para Symplifika Chrome Extension (Vue.js)
// Sistema híbrido: Triggers tradicionais + Ícone de Ação Rápida

console.log("🎯 Symplifika Content Script carregado");

// Estado do content script
let isActive = true;
let lastActiveElement = null;
let triggerBuffer = "";
let isExpanding = false;
let extensionInvalidated = false;
let useQuickActionMode = true; // Novo: controla modo de operação

// Configurações
const TRIGGER_PREFIX = "!";
const TRIGGER_TIMEOUT = 3000; // 3 segundos para completar o trigger
let triggerTimer = null;
let healthCheckInterval = null;

// Seletores de campos de texto
const TEXT_FIELD_SELECTORS = [
  'input[type="text"]',
  'input[type="email"]',
  'input[type="search"]',
  'input[type="url"]',
  "input:not([type])",
  "textarea",
  '[contenteditable="true"]',
  '[contenteditable=""]',
  ".ql-editor", // Quill editor
  ".note-editable", // Summernote
  ".fr-element", // Froala
  ".tox-edit-area", // TinyMCE
  ".CodeMirror-code", // CodeMirror
];

// Inicialização
function init() {
  // Adicionar listeners de eventos para triggers tradicionais
  if (!useQuickActionMode) {
    document.addEventListener("keydown", handleKeyDown, true);
    document.addEventListener("input", handleInput, true);
  }
  
  document.addEventListener("focusin", handleFocusIn, true);
  document.addEventListener("focusout", handleFocusOut, true);

  // Inicializar sistema de ícone de ação rápida
  if (useQuickActionMode && typeof initQuickActionSystem === 'function') {
    initQuickActionSystem();
    console.log("✅ Sistema de ícone de ação rápida ativado");
  }

  // Iniciar monitoramento de saúde da extensão
  startHealthCheck();

  console.log("✅ Event listeners adicionados");
}

// Monitoramento de saúde da extensão
function startHealthCheck() {
  // Verificar a cada 60 segundos se a extensão ainda está ativa (reduzido para evitar spam)
  healthCheckInterval = setInterval(async () => {
    if (extensionInvalidated) return;

    try {
      // Tentar fazer ping no background script
      if (!chrome.runtime?.id) {
        handleExtensionInvalidation();
        return;
      }

      const response = await sendMessageWithTimeout({ type: "PING" }, 5000); // Aumentado timeout
      
      if (!response || !response.success) {
        console.warn("⚠️ Background script não respondeu ao ping");
        // Não invalidar imediatamente - pode ser temporário
      } else {
        console.log("✅ Health check OK:", response.timestamp);
      }
    } catch (error) {
      console.warn("⚠️ Health check falhou:", error.message);
      if (error.message.includes("Extension context invalidated") || 
          error.message.includes("message port closed")) {
        handleExtensionInvalidation();
      }
      // Para timeouts, apenas log - não invalidar
    }
  }, 60000); // 60 segundos
}

// Lidar com invalidação da extensão
function handleExtensionInvalidation() {
  if (extensionInvalidated) return;
  
  extensionInvalidated = true;
  console.warn("🔄 Extensão foi invalidada - desabilitando funcionalidades");
  
  // Parar health check
  if (healthCheckInterval) {
    clearInterval(healthCheckInterval);
    healthCheckInterval = null;
  }
  
  // Limpar estado
  triggerBuffer = "";
  isExpanding = false;
  clearTimeout(triggerTimer);
  
  // Remover highlight se existir
  if (lastActiveElement) {
    removeHighlight(lastActiveElement);
  }
  
  // Mostrar notificação persistente
  showExtensionReloadNotification();
}

// Mostrar notificação de reload da extensão (REMOVIDA - não mostrar mais popup automático)
function showExtensionReloadNotification() {
  // Apenas log no console - não mostrar popup intrusivo
  console.log("🔄 Extensão Symplifika foi recarregada. Funcionalidades podem estar temporariamente indisponíveis.");
}

// Verificar se elemento é um campo de texto
function isTextField(element) {
  if (!element) return false;

  // Verificar por seletores
  for (const selector of TEXT_FIELD_SELECTORS) {
    if (element.matches && element.matches(selector)) {
      return true;
    }
  }

  // Verificar se é editável
  if (element.isContentEditable) {
    return true;
  }

  // Verificar input types
  if (element.tagName === "INPUT") {
    const type = element.type.toLowerCase();
    return (
      ["text", "email", "search", "url", "password"].includes(type) ||
      !element.type
    );
  }

  return false;
}

// Handler para foco em elemento
function handleFocusIn(event) {
  const element = event.target;

  if (isTextField(element)) {
    lastActiveElement = element;
    console.log(
      "📝 Campo de texto focado:",
      element.tagName,
      element.type || "contenteditable",
    );
  }
}

// Handler para perda de foco
function handleFocusOut(event) {
  // Limpar buffer quando perder foco
  triggerBuffer = "";
  clearTimeout(triggerTimer);
}

// Handler para teclas pressionadas
function handleKeyDown(event) {
  if (!isActive || !lastActiveElement) return;

  // ESC para cancelar trigger
  if (event.key === "Escape") {
    triggerBuffer = "";
    clearTimeout(triggerTimer);
    return;
  }

  // Space ou Enter para tentar expandir
  if ((event.key === " " || event.key === "Enter") && triggerBuffer) {
    event.preventDefault();
    expandTrigger();
    return;
  }

  // Backspace para remover do buffer
  if (event.key === "Backspace" && triggerBuffer) {
    triggerBuffer = triggerBuffer.slice(0, -1);
    if (!triggerBuffer) {
      clearTimeout(triggerTimer);
    }
    return;
  }
}

// Handler para input de texto
function handleInput(event) {
  if (!isActive || !lastActiveElement || isExpanding) return;

  const element = event.target;
  if (!isTextField(element)) return;

  // Obter texto atual
  const text = getElementText(element);
  const cursorPos = getCursorPosition(element);

  // Procurar por trigger no final do texto
  const beforeCursor = text.substring(0, cursorPos);
  const triggerMatch = beforeCursor.match(/!([a-zA-Z0-9_-]+)$/);

  if (triggerMatch) {
    const newTrigger = triggerMatch[1];

    if (newTrigger !== triggerBuffer.replace("!", "")) {
      triggerBuffer = "!" + newTrigger;

      // Destacar visualmente o campo
      highlightField(element);

      // Timer para limpar buffer
      clearTimeout(triggerTimer);
      triggerTimer = setTimeout(() => {
        triggerBuffer = "";
        removeHighlight(element);
      }, TRIGGER_TIMEOUT);

      console.log("🎯 Trigger detectado:", triggerBuffer);
    }
  } else if (triggerBuffer) {
    // Perdeu o padrão do trigger
    triggerBuffer = "";
    clearTimeout(triggerTimer);
    removeHighlight(element);
  }
}

// Obter texto do elemento
function getElementText(element) {
  if (element.value !== undefined) {
    return element.value;
  } else if (element.textContent !== undefined) {
    return element.textContent;
  } else if (element.innerText !== undefined) {
    return element.innerText;
  }
  return "";
}

// Obter posição do cursor
function getCursorPosition(element) {
  if (element.selectionStart !== undefined) {
    return element.selectionStart;
  } else if (window.getSelection) {
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
      const range = selection.getRangeAt(0);
      return range.startOffset;
    }
  }
  return 0;
}

// Enviar mensagem com timeout para evitar travamento
function sendMessageWithTimeout(message, timeoutMs = 5000) {
  return new Promise((resolve, reject) => {
    // Verificar se chrome.runtime está disponível
    if (!chrome.runtime || !chrome.runtime.sendMessage) {
      reject(new Error("Extension context invalidated - chrome.runtime não disponível"));
      return;
    }

    let timeoutId;
    let resolved = false;

    // Configurar timeout
    timeoutId = setTimeout(() => {
      if (!resolved) {
        resolved = true;
        reject(new Error(`timeout - Mensagem não respondida em ${timeoutMs}ms`));
      }
    }, timeoutMs);

    try {
      chrome.runtime.sendMessage(message, (response) => {
        if (resolved) return; // Já resolvido por timeout
        
        clearTimeout(timeoutId);
        resolved = true;
        
        // Verificar se houve erro de runtime
        if (chrome.runtime.lastError) {
          const errorMsg = chrome.runtime.lastError.message;
          if (errorMsg.includes("Receiving end does not exist") || 
              errorMsg.includes("message port closed") ||
              errorMsg.includes("Extension context invalidated")) {
            reject(new Error("Extension context invalidated: " + errorMsg));
          } else {
            reject(new Error("Runtime error: " + errorMsg));
          }
          return;
        }
        
        resolve(response);
      });
    } catch (error) {
      if (!resolved) {
        clearTimeout(timeoutId);
        resolved = true;
        reject(error);
      }
    }
  });
}

// Expandir trigger
async function expandTrigger() {
  if (!triggerBuffer || isExpanding || extensionInvalidated) return;

  // Verificação adicional de invalidação
  if (extensionInvalidated) {
    console.warn("⚠️ Tentativa de expansão com extensão invalidada");
    showErrorFeedback(lastActiveElement, "Extensão foi recarregada - recarregue a página");
    return;
  }

  isExpanding = true;
  const trigger = triggerBuffer;
  triggerBuffer = "";
  clearTimeout(triggerTimer);

  try {
    console.log("🚀 Expandindo trigger:", trigger);

    // Verificar se a extensão ainda está ativa
    if (!chrome.runtime?.id) {
      console.warn("⚠️ Extensão foi recarregada ou desabilitada");
      handleExtensionInvalidation();
      return;
    }

    // Enviar mensagem para background script com timeout
    const response = await sendMessageWithTimeout({
      type: "EXPAND_TEXT",
      payload: { trigger: trigger },
    }, 5000);

    if (response && response.success && response.expandedText) {
      // Substituir o trigger pelo texto expandido
      await replaceText(lastActiveElement, trigger, response.expandedText);

      // Feedback visual
      showExpansionFeedback(lastActiveElement, response.shortcut.title);

      console.log("✨ Texto expandido com sucesso");
    } else {
      console.log("❌ Atalho não encontrado:", trigger);

      // Feedback de erro
      showErrorFeedback(lastActiveElement, "Atalho não encontrado");
    }
  } catch (error) {
    console.error("❌ Erro na expansão:", error);
    
    // Tratar diferentes tipos de erro
    if (error.message && error.message.includes("Extension context invalidated")) {
      showErrorFeedback(lastActiveElement, "Extensão foi recarregada - recarregue a página");
    } else if (error.message && error.message.includes("timeout")) {
      showErrorFeedback(lastActiveElement, "Timeout - verifique sua conexão");
    } else {
      showErrorFeedback(lastActiveElement, "Erro na expansão");
    }
  } finally {
    isExpanding = false;
    removeHighlight(lastActiveElement);
  }
}

// Substituir texto no elemento
async function replaceText(element, trigger, expandedText) {
  if (!element) return;

  if (element.value !== undefined) {
    // Input/textarea
    const text = element.value;
    const cursorPos = element.selectionStart || text.length;
    const beforeCursor = text.substring(0, cursorPos);
    const afterCursor = text.substring(cursorPos);

    // Encontrar e substituir o trigger
    const triggerIndex = beforeCursor.lastIndexOf(trigger);
    if (triggerIndex !== -1) {
      const newText =
        beforeCursor.substring(0, triggerIndex) + expandedText + afterCursor;

      element.value = newText;

      // Posicionar cursor após o texto expandido
      const newCursorPos = triggerIndex + expandedText.length;
      element.setSelectionRange(newCursorPos, newCursorPos);

      // Disparar evento de input
      element.dispatchEvent(new Event("input", { bubbles: true }));
    }
  } else if (element.isContentEditable) {
    // Elemento contenteditable
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
      const range = selection.getRangeAt(0);
      const textNode = range.startContainer;

      if (textNode.nodeType === Node.TEXT_NODE) {
        const text = textNode.textContent;
        const triggerIndex = text.lastIndexOf(trigger);

        if (triggerIndex !== -1) {
          // Criar novo range para substituir
          const newRange = document.createRange();
          newRange.setStart(textNode, triggerIndex);
          newRange.setEnd(textNode, triggerIndex + trigger.length);

          // Substituir texto
          newRange.deleteContents();
          newRange.insertNode(document.createTextNode(expandedText));

          // Posicionar cursor
          newRange.collapse(false);
          selection.removeAllRanges();
          selection.addRange(newRange);
        }
      }
    }
  }
}

// Destacar campo visualmente
function highlightField(element) {
  if (!element) return;

  element.style.outline = "2px solid #10b981";
  element.style.outlineOffset = "2px";
  element.style.transition = "outline 0.2s ease";
}

// Remover destaque
function removeHighlight(element) {
  if (!element) return;

  element.style.outline = "";
  element.style.outlineOffset = "";
}

// Mostrar feedback de expansão bem-sucedida
function showExpansionFeedback(element, title) {
  if (!element) return;

  const feedback = document.createElement("div");
  feedback.textContent = `✨ ${title}`;
  feedback.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: #10b981;
    color: white;
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    z-index: 10000;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
    animation: slideIn 0.3s ease;
  `;

  // Adicionar animação CSS
  if (!document.getElementById("symplifika-animations")) {
    const style = document.createElement("style");
    style.id = "symplifika-animations";
    style.textContent = `
      @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
      }
      @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
      }
    `;
    document.head.appendChild(style);
  }

  document.body.appendChild(feedback);

  // Remover após 3 segundos
  setTimeout(() => {
    feedback.style.animation = "slideOut 0.3s ease";
    setTimeout(() => {
      if (feedback.parentNode) {
        feedback.parentNode.removeChild(feedback);
      }
    }, 300);
  }, 3000);
}

// Listener para mensagens do background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  try {
    // Verificar se a extensão ainda está ativa
    if (!chrome.runtime?.id) {
      console.warn("⚠️ Extensão foi invalidada durante processamento de mensagem");
      return false;
    }

    switch (request.type) {
      case "TOGGLE_ACTIVE":
        isActive = request.payload.active;
        console.log("🔄 Estado alterado:", isActive ? "Ativo" : "Inativo");
        sendResponse({ success: true });
        break;

      case "TOGGLE_MODE":
        useQuickActionMode = request.payload.quickActionMode;
        console.log("🔄 Modo alterado:", useQuickActionMode ? "Ícone de Ação" : "Triggers Tradicionais");
        // Reinicializar sistema
        location.reload();
        sendResponse({ success: true });
        break;

      case "PING":
        // Resposta para verificação de saúde
        sendResponse({ success: true, status: "alive", mode: useQuickActionMode ? "quick-action" : "traditional" });
        break;

      default:
        sendResponse({ success: false, error: "Comando desconhecido" });
    }
  } catch (error) {
    console.error("❌ Erro no listener de mensagens:", error);
    sendResponse({ success: false, error: error.message });
  }
  
  // Retornar true para manter o canal de comunicação aberto
  return true;
});

// Inicializar quando DOM estiver pronto
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}

console.log("✅ Symplifika Content Script inicializado");

// Carregar sistema de ícone de ação rápida
(function loadQuickActionSystem() {
  const script = document.createElement('script');
  script.src = chrome.runtime.getURL('content/quick-action-icon.js');
  script.onload = function() {
    console.log("✅ Quick Action System carregado");
  };
  (document.head || document.documentElement).appendChild(script);
})();
