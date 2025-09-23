/**
 * Script de inicialização para teste local da extensão Symplifika
 * Este arquivo simula o carregamento da extensão para testes em páginas locais
 */

(function () {
  "use strict";

  console.log("[Symplifika Test] Iniciando simulação da extensão...");

  // Simular configurações da extensão
  const mockExtensionSettings = {
    isEnabled: true,
    isAuthenticated: true,
    debugMode: true,
    shortcuts: [
      {
        id: 1,
        trigger: "email",
        title: "E-mail Profissional",
        content: "Olá,\n\nEspero que esteja bem.\n\nAtenciosamente,\n[Nome]",
        category: { name: "Profissional" },
        use_count: 25,
        expansion_type: "static",
        relevanceScore: 80,
      },
      {
        id: 2,
        trigger: "addr",
        title: "Endereço Completo",
        content:
          "Rua das Flores, 123\nBairro Centro\nSão Paulo - SP\nCEP: 01234-567",
        category: { name: "Pessoal" },
        use_count: 15,
        expansion_type: "static",
        relevanceScore: 60,
      },
      {
        id: 3,
        trigger: "meet",
        title: "Convite para Reunião",
        content:
          "Olá {nome},\n\nGostaria de agendar uma reunião para discutir {assunto}.\n\nDisponibilidade: {data}\n\nAguardo retorno.",
        category: { name: "Reuniões" },
        use_count: 40,
        expansion_type: "dynamic",
        relevanceScore: 95,
      },
      {
        id: 4,
        trigger: "thanks",
        title: "Agradecimento",
        content:
          "Muito obrigado pela atenção e disponibilidade.\n\nTenha um ótimo dia!",
        category: { name: "Cortesia" },
        use_count: 60,
        expansion_type: "static",
        relevanceScore: 70,
      },
      {
        id: 5,
        trigger: "sig",
        title: "Assinatura E-mail",
        content: "---\n{nome}\n{cargo}\n{empresa}\n{telefone}\n{email}",
        category: { name: "Assinatura" },
        use_count: 100,
        expansion_type: "dynamic",
        relevanceScore: 85,
      },
    ],
  };

  // Simular API do Chrome (para teste local)
  if (typeof chrome === "undefined") {
    window.chrome = {
      storage: {
        local: {
          get: function (keys, callback) {
            const mockData = {
              settings: mockExtensionSettings,
              shortcuts: mockExtensionSettings.shortcuts,
              isAuthenticated: true,
              apiUrl: "http://localhost:8000",
            };
            callback(mockData);
          },
          set: function (data, callback) {
            console.log("[Mock Chrome Storage] Set:", data);
            if (callback) callback();
          },
        },
      },
      runtime: {
        sendMessage: function (message, callback) {
          console.log("[Mock Chrome Runtime] Message:", message);
          // Simular resposta baseada no tipo de mensagem
          const mockResponse = {
            success: true,
            data:
              message.action === "getShortcuts"
                ? mockExtensionSettings.shortcuts
                : null,
          };
          if (callback) {
            setTimeout(() => callback(mockResponse), 100);
          }
        },
        onMessage: {
          addListener: function (listener) {
            console.log("[Mock Chrome Runtime] Message listener added");
          },
        },
      },
    };
  }

  // Mock da classe SymphilikaContentScript para teste
  class MockContentScript {
    constructor() {
      this.isEnabled = true;
      this.isAuthenticated = true;
      this.shortcuts = mockExtensionSettings.shortcuts;
    }

    async expandShortcutWithVariables(shortcut) {
      console.log("[Mock] Expanding shortcut:", shortcut);

      if (shortcut.expansion_type === "dynamic") {
        // Simular substituição de variáveis
        let content = shortcut.content;
        content = content.replace(/{nome}/g, "João Silva");
        content = content.replace(/{cargo}/g, "Desenvolvedor");
        content = content.replace(/{empresa}/g, "Tech Corp");
        content = content.replace(/{telefone}/g, "(11) 99999-9999");
        content = content.replace(/{email}/g, "joao@techcorp.com");
        content = content.replace(/{assunto}/g, "novo projeto");
        content = content.replace(/{data}/g, "próxima terça-feira");
        return content;
      }

      return shortcut.content;
    }

    async markShortcutAsUsed(shortcutId) {
      console.log("[Mock] Marking shortcut as used:", shortcutId);
      return true;
    }
  }

  // Aguardar carregamento do DOM
  const initializeTest = () => {
    console.log("[Symplifika Test] DOM carregado, inicializando teste...");

    // Criar instância mock do ContentScript se não existir
    if (!window.symphilikaContentScript) {
      window.symphilikaContentScript = new MockContentScript();
      console.log("[Symplifika Test] Mock ContentScript criado");
    }

    // Aguardar QuickAccessIcon estar disponível
    const waitForQuickAccessIcon = (attempts = 0) => {
      if (typeof QuickAccessIcon !== "undefined") {
        console.log(
          "[Symplifika Test] QuickAccessIcon encontrado, inicializando...",
        );

        // Criar instância do QuickAccessIcon
        try {
          window.testQuickAccessIcon = new QuickAccessIcon(
            window.symphilikaContentScript,
          );
          console.log(
            "[Symplifika Test] ✅ QuickAccessIcon inicializado com sucesso!",
          );

          // Adicionar algumas funções de teste globais
          window.symplifikaTest = {
            showAllIcons: () => {
              const fields = document.querySelectorAll(
                'input[type="text"], input[type="email"], textarea, input[type="search"], input[type="tel"], input[type="url"]',
              );
              fields.forEach((field) => {
                window.testQuickAccessIcon.attachToField(field);
                window.testQuickAccessIcon.forceShowIcon(field);
              });
              console.log(`[Test] Showing icons on ${fields.length} fields`);
              return fields.length;
            },

            listActiveIcons: () => {
              console.log(
                "[Test] Active icons:",
                window.testQuickAccessIcon?.activeIcons,
              );
              window.testQuickAccessIcon?.activeIcons?.forEach(
                (icon, field) => {
                  console.log(
                    `- Field: ${field.tagName} (${field.type || "N/A"})`,
                    {
                      visible: icon.style.display !== "none",
                      id: field.id || "no-id",
                      placeholder: field.placeholder || "no-placeholder",
                    },
                  );
                },
              );
            },

            toggleAllIcons: () => {
              let hiddenCount = 0;
              let shownCount = 0;

              window.testQuickAccessIcon?.activeIcons?.forEach(
                (icon, field) => {
                  if (icon.style.display === "none") {
                    window.testQuickAccessIcon.showIcon(field, icon);
                    shownCount++;
                  } else {
                    icon.style.display = "none";
                    hiddenCount++;
                  }
                },
              );

              console.log(
                `[Test] Toggled icons: ${shownCount} shown, ${hiddenCount} hidden`,
              );
            },

            hideAll: (immediate = false) => {
              if (window.testQuickAccessIcon?.hideAll) {
                window.testQuickAccessIcon.hideAll(immediate);
                console.log(
                  `[Test] All icons hidden (immediate: ${immediate})`,
                );
              }
            },

            forceShowAll: () => {
              const fields = document.querySelectorAll(
                'input[type="text"], input[type="email"], textarea, input[type="search"], input[type="tel"], input[type="url"]',
              );
              let count = 0;
              fields.forEach((field) => {
                if (
                  window.testQuickAccessIcon.isValidField &&
                  window.testQuickAccessIcon.isValidField(field)
                ) {
                  window.testQuickAccessIcon.forceShowIcon(field);
                  count++;
                }
              });
              console.log(
                `[Test] Force showing icons on ${count} valid fields`,
              );
              return count;
            },

            testNotification: () => {
              if (window.testQuickAccessIcon.showCopyNotification) {
                window.testQuickAccessIcon.showCopyNotification(
                  "Teste de Notificação",
                  "Esta é uma notificação de teste para verificar o funcionamento!",
                );
              }
            },

            getStatus: () => {
              return {
                quickAccessIcon: !!window.testQuickAccessIcon,
                contentScript: !!window.symphilikaContentScript,
                activeIcons: window.testQuickAccessIcon?.activeIcons?.size || 0,
                shortcuts: mockExtensionSettings.shortcuts.length,
                isEnabled: true,
                isAuthenticated: true,
                debugMode: true,
              };
            },

            getActiveIconsCount: () => {
              return window.testQuickAccessIcon?.activeIcons?.size || 0;
            },
          };

          // Também disponibilizar como symplifikaDebug para compatibilidade
          window.symplifikaDebug = {
            showTextFieldIcons: () => window.symplifikaTest.showAllIcons(),
            listActiveIcons: () => window.symplifikaTest.listActiveIcons(),
            toggleAllIcons: () => window.symplifikaTest.toggleAllIcons(),
            forceShowAll: () => window.symplifikaTest.forceShowAll(),
            hideAll: (immediate = false) =>
              window.symplifikaTest.hideAll(immediate),
            getActiveIconsCount: () =>
              window.symplifikaTest.getActiveIconsCount(),
            isEnabled: () => true,
            isAuthenticated: () => true,
            testCopyNotification: (
              title = "Teste",
              content = "Conteúdo de teste copiado!",
            ) => {
              if (window.testQuickAccessIcon.showCopyNotification) {
                window.testQuickAccessIcon.showCopyNotification(title, content);
              }
            },
          };

          console.log(
            "[Symplifika Test] 🧪 Funções de teste disponíveis em window.symplifikaTest e window.symplifikaDebug",
          );
          console.log(
            "[Symplifika Test] 📊 Status:",
            window.symplifikaTest.getStatus(),
          );

          // Mostrar ícones automaticamente após 1 segundo
          setTimeout(() => {
            const count = window.symplifikaTest.showAllIcons();
            console.log(
              `[Symplifika Test] 🎯 Auto-showing icons on ${count} fields`,
            );
          }, 1000);
        } catch (error) {
          console.error(
            "[Symplifika Test] ❌ Erro ao inicializar QuickAccessIcon:",
            error,
          );
        }
      } else if (attempts < 20) {
        console.log(
          `[Symplifika Test] Aguardando QuickAccessIcon... (tentativa ${attempts + 1}/20)`,
        );
        setTimeout(() => waitForQuickAccessIcon(attempts + 1), 500);
      } else {
        console.error(
          "[Symplifika Test] ❌ QuickAccessIcon não encontrado após 20 tentativas",
        );
      }
    };

    // Iniciar verificação
    waitForQuickAccessIcon();
  };

  // Inicializar quando o DOM estiver pronto
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeTest);
  } else {
    initializeTest();
  }

  // Adicionar CSS de teste se necessário
  const addTestStyles = () => {
    const existingStyle = document.getElementById("symplifika-test-styles");
    if (existingStyle) return;

    const style = document.createElement("style");
    style.id = "symplifika-test-styles";
    style.textContent = `
            /* Estilos de teste para debug */
            .symplifika-test-field {
                border: 2px dashed #00c853 !important;
                background: rgba(0, 200, 83, 0.05) !important;
            }

            .symplifika-test-debug {
                position: fixed;
                bottom: 20px;
                left: 20px;
                background: #263238;
                color: #00ff57;
                padding: 10px;
                border-radius: 6px;
                font-family: monospace;
                font-size: 12px;
                z-index: 999999;
                max-width: 300px;
            }
        `;
    document.head.appendChild(style);
  };

  // Adicionar informações de debug na página
  const addDebugInfo = () => {
    setTimeout(() => {
      const debugDiv = document.createElement("div");
      debugDiv.className = "symplifika-test-debug";
      debugDiv.innerHTML = `
                <strong>🧪 Symplifika Test Mode</strong><br>
                <small>Extensão simulada carregada</small><br>
                <small>window.symplifikaTest disponível</small>
            `;
      document.body.appendChild(debugDiv);

      // Remover após 5 segundos
      setTimeout(() => {
        debugDiv.remove();
      }, 5000);
    }, 2000);
  };

  // Executar setup de teste
  addTestStyles();
  addDebugInfo();
})();
