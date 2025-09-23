// Teste mínimo de carregamento - QuickAccessIcon
console.log("🔧 QuickAccessIcon-Test carregando...");

class QuickAccessIconTest {
  constructor(contentScript) {
    console.log("✅ QuickAccessIconTest construtor chamado");
    this.contentScript = contentScript || {
      isEnabled: true,
      isAuthenticated: true,
    };
    this.testElement = null;
    this.init();
  }

  init() {
    console.log("✅ QuickAccessIconTest.init() chamado");
    this.injectAggressiveCSS();
    this.createTestIndicator();
    this.createFixedTestIcon();
    this.attachToFirstField();
  }

  createTestIndicator() {
    // Criar indicador visual de que a classe carregou
    const indicator = document.createElement("div");
    indicator.id = "quickaccess-test-indicator";
    indicator.style.cssText = `
      position: fixed !important;
      top: 10px !important;
      right: 10px !important;
      background: #28a745 !important;
      color: white !important;
      padding: 10px !important;
      border-radius: 4px !important;
      z-index: 999999 !important;
      font-family: Arial, sans-serif !important;
      font-size: 14px !important;
    `;
    indicator.textContent = "✅ QuickAccessIcon carregado!";

    if (document.body) {
      document.body.appendChild(indicator);
      console.log("✅ Indicador visual criado");
    } else {
      // Se body não existe ainda, aguardar
      document.addEventListener("DOMContentLoaded", () => {
        document.body.appendChild(indicator);
        console.log("✅ Indicador visual criado (após DOMContentLoaded)");
      });
    }

    // Remover após 10 segundos
    setTimeout(() => {
      if (indicator.parentNode) {
        indicator.parentNode.removeChild(indicator);
        console.log("✅ Indicador visual removido");
      }
    }, 10000);

    this.testElement = indicator;
  }

  injectAggressiveCSS() {
    // Criar CSS agressivo para garantir que os ícones apareçam
    const style = document.createElement("style");
    style.id = "symplifika-aggressive-css";
    style.textContent = `
      .symplifika-test-icon {
        position: fixed !important;
        display: flex !important;
        width: 24px !important;
        height: 24px !important;
        background: #dc3545 !important;
        border: 2px solid white !important;
        border-radius: 50% !important;
        z-index: 2147483647 !important;
        align-items: center !important;
        justify-content: center !important;
        color: white !important;
        font-size: 12px !important;
        cursor: pointer !important;
        box-shadow: 0 0 10px rgba(220, 53, 69, 0.8) !important;
        font-weight: bold !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: all !important;
        transform: none !important;
        filter: none !important;
        clip: auto !important;
        overflow: visible !important;
      }
      .symplifika-test-icon:hover {
        background: #c82333 !important;
        transform: scale(1.1) !important;
      }
    `;

    if (document.head) {
      document.head.appendChild(style);
      console.log("✅ CSS agressivo injetado");
    } else {
      document.addEventListener("DOMContentLoaded", () => {
        document.head.appendChild(style);
        console.log("✅ CSS agressivo injetado (após DOMContentLoaded)");
      });
    }
  }

  createFixedTestIcon() {
    // Criar ícone fixo para testar se o problema é de posicionamento
    const fixedIcon = document.createElement("div");
    fixedIcon.id = "symplifika-fixed-test-icon";
    fixedIcon.className = "symplifika-test-icon";
    fixedIcon.style.cssText = `
      position: fixed !important;
      top: 100px !important;
      left: 100px !important;
      width: 40px !important;
      height: 40px !important;
      background: #28a745 !important;
      border: 3px solid white !important;
      border-radius: 50% !important;
      z-index: 2147483647 !important;
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      color: white !important;
      font-size: 20px !important;
      cursor: pointer !important;
      box-shadow: 0 0 20px rgba(40, 167, 69, 0.8) !important;
      font-weight: bold !important;
      visibility: visible !important;
      opacity: 1 !important;
      pointer-events: all !important;
    `;
    fixedIcon.textContent = "🔧";
    fixedIcon.title = "Ícone fixo de teste - se você vê isso, o CSS funciona!";

    fixedIcon.addEventListener("click", () => {
      alert("🎉 Ícone fixo funcionando! O problema não é do CSS.");
      console.log("✅ Ícone fixo clicado - CSS está funcionando");
    });

    if (document.body) {
      document.body.appendChild(fixedIcon);
      console.log("✅ Ícone fixo criado na posição (100, 100)");
    } else {
      document.addEventListener("DOMContentLoaded", () => {
        document.body.appendChild(fixedIcon);
        console.log("✅ Ícone fixo criado (após DOMContentLoaded)");
      });
    }

    // Remover após 30 segundos
    setTimeout(() => {
      if (fixedIcon.parentNode) {
        fixedIcon.parentNode.removeChild(fixedIcon);
        console.log("✅ Ícone fixo removido");
      }
    }, 30000);
  }

  attachToFirstField() {
    const findAndAttach = () => {
      const fields = document.querySelectorAll(
        'input[type="text"], input[type="email"], textarea, [contenteditable="true"]',
      );
      console.log(`🔧 Campos encontrados: ${fields.length}`);

      if (fields.length > 0) {
        const field = fields[0];
        console.log(
          `🔧 Primeiro campo: ${field.tagName} (${field.type || "contenteditable"})`,
        );

        // Criar ícone simples
        const icon = document.createElement("div");
        icon.className = "symplifika-test-icon";
        icon.id = "symplifika-test-icon-" + Date.now();
        icon.textContent = "⚡";
        icon.title = "Teste Symplifika";

        // Estilo inline como backup
        icon.style.cssText = `
          position: fixed !important;
          width: 24px !important;
          height: 24px !important;
          background: #dc3545 !important;
          border: 2px solid white !important;
          border-radius: 50% !important;
          z-index: 2147483647 !important;
          display: none !important;
          align-items: center !important;
          justify-content: center !important;
          color: white !important;
          font-size: 12px !important;
          cursor: pointer !important;
          box-shadow: 0 0 10px rgba(220, 53, 69, 0.8) !important;
          font-weight: bold !important;
          visibility: hidden !important;
          opacity: 0 !important;
        `;

        document.body.appendChild(icon);

        // Mostrar ícone no hover
        field.addEventListener("mouseenter", () => {
          const rect = field.getBoundingClientRect();

          // Múltiplas formas de mostrar o ícone
          icon.style.setProperty("display", "flex", "important");
          icon.style.setProperty("visibility", "visible", "important");
          icon.style.setProperty("opacity", "1", "important");
          icon.style.setProperty("top", `${rect.top + 2}px`, "important");
          icon.style.setProperty("left", `${rect.right - 26}px`, "important");

          // Adicionar classe para CSS
          icon.classList.add("visible");

          // Forçar reflow
          icon.offsetHeight;

          console.log("✅ Ícone mostrado no hover", {
            element: icon,
            computed: window.getComputedStyle(icon),
            display: icon.style.display,
            visibility: icon.style.visibility,
            opacity: icon.style.opacity,
            top: icon.style.top,
            left: icon.style.left,
            zIndex: icon.style.zIndex,
            rect: `${rect.width}x${rect.height} at (${rect.left}, ${rect.top})`,
            inDOM: document.contains(icon),
          });
        });

        field.addEventListener("mouseleave", () => {
          setTimeout(() => {
            icon.style.setProperty("display", "none", "important");
            icon.style.setProperty("visibility", "hidden", "important");
            icon.style.setProperty("opacity", "0", "important");
            icon.classList.remove("visible");
            console.log("✅ Ícone ocultado após mouse leave");
          }, 1000);
        });

        // Clique no ícone
        icon.addEventListener("click", (e) => {
          e.stopPropagation();
          e.preventDefault();
          alert("🎉 Symplifika QuickAccess funcionando!");
          console.log("✅ Ícone clicado - funcionando!");
        });

        // Debug adicional
        icon.addEventListener("mouseenter", () => {
          console.log("🔧 Mouse entrou no ícone");
        });

        icon.addEventListener("mouseleave", () => {
          console.log("🔧 Mouse saiu do ícone");
        });

        console.log("✅ Ícone anexado ao primeiro campo");
      } else {
        console.log("❌ Nenhum campo encontrado, tentando novamente em 2s...");
        setTimeout(findAndAttach, 2000);
      }
    };

    // Tentar imediatamente e também após DOM ready
    findAndAttach();

    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", findAndAttach);
    }
  }

  destroy() {
    console.log("✅ QuickAccessIconTest.destroy() chamado");
    if (this.testElement && this.testElement.parentNode) {
      this.testElement.parentNode.removeChild(this.testElement);
    }
  }
}

// Disponibilizar globalmente
window.QuickAccessIconTest = QuickAccessIconTest;

console.log("✅ QuickAccessIconTest classe definida");

// Auto-inicializar para teste
setTimeout(() => {
  if (document.body) {
    console.log("🚀 Auto-inicializando QuickAccessIconTest...");
    window.testInstance = new QuickAccessIconTest();
  }
}, 1000);
