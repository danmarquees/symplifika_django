// Teste do Quick Action Icon - Symplifika Chrome Extension
// Script para validar funcionalidades do sistema de ação rápida

const DJANGO_SERVER = "http://127.0.0.1:8000";

class QuickActionTester {
    constructor() {
        this.testResults = [];
        this.shortcuts = [];
    }

    log(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const logMessage = `[${timestamp}] ${type.toUpperCase()}: ${message}`;
        console.log(logMessage);

        this.testResults.push({
            timestamp,
            type,
            message,
            success: type === 'success'
        });
    }

    async runAllTests() {
        console.log("🧪 Iniciando testes do Quick Action Icon - Symplifika");
        console.log("=" .repeat(60));

        try {
            await this.testExtensionConnection();
            await this.testShortcutsLoading();
            await this.testUserInterface();
            await this.testKeyboardShortcuts();
            await this.testFieldDetection();
            await this.testShortcutInsertion();
            await this.testSearchFunctionality();

            this.generateReport();
        } catch (error) {
            this.log(`Erro geral nos testes: ${error.message}`, 'error');
        }
    }

    async testExtensionConnection() {
        this.log("Testando conexão com a extensão...");

        try {
            // Verificar se o Chrome runtime está disponível
            if (typeof chrome === 'undefined' || !chrome.runtime) {
                throw new Error("Chrome runtime não disponível");
            }

            // Testar comunicação com background script
            const response = await this.sendMessage({ type: "PING" });

            if (response && response.success) {
                this.log(`Extensão conectada - Status: ${response.status}`, 'success');
                this.log(`Autenticado: ${response.authenticated}`, 'info');
                this.log(`Atalhos carregados: ${response.shortcuts}`, 'info');
            } else {
                throw new Error("Resposta inválida do background script");
            }

        } catch (error) {
            this.log(`Falha na conexão: ${error.message}`, 'error');
        }
    }

    async testShortcutsLoading() {
        this.log("Testando carregamento de atalhos...");

        try {
            const response = await this.sendMessage({ type: "GET_SHORTCUTS" });

            if (response && response.success) {
                this.shortcuts = response.shortcuts || [];
                this.log(`${this.shortcuts.length} atalhos carregados`, 'success');

                if (this.shortcuts.length > 0) {
                    this.log("Exemplos de atalhos encontrados:");
                    this.shortcuts.slice(0, 3).forEach(shortcut => {
                        this.log(`  - ${shortcut.trigger}: ${shortcut.title}`, 'info');
                    });
                } else {
                    this.log("Nenhum atalho encontrado - criar atalhos de teste", 'warning');
                }

            } else {
                throw new Error("Erro ao carregar atalhos");
            }

        } catch (error) {
            this.log(`Falha no carregamento: ${error.message}`, 'error');
        }
    }

    async testUserInterface() {
        this.log("Testando interface do usuário...");

        try {
            // Criar campo de teste
            const testField = this.createTestField();
            document.body.appendChild(testField);

            // Simular foco no campo
            testField.focus();

            // Aguardar um pouco para o ícone aparecer
            await this.sleep(500);

            // Verificar se o ícone apareceu
            const icon = document.querySelector('.symplifika-icon');
            if (icon) {
                this.log("Ícone de ação rápida criado com sucesso", 'success');

                if (icon.classList.contains('visible')) {
                    this.log("Ícone visível após foco no campo", 'success');
                } else {
                    this.log("Ícone não ficou visível", 'warning');
                }
            } else {
                throw new Error("Ícone não foi criado");
            }

            // Testar clique no ícone
            icon.click();
            await this.sleep(300);

            const dropdown = document.querySelector('.symplifika-dropdown');
            if (dropdown && dropdown.classList.contains('visible')) {
                this.log("Dropdown aberto com sucesso", 'success');

                // Verificar elementos do dropdown
                this.testDropdownElements(dropdown);
            } else {
                this.log("Dropdown não abriu corretamente", 'warning');
            }

            // Limpar
            testField.remove();

        } catch (error) {
            this.log(`Erro na interface: ${error.message}`, 'error');
        }
    }

    testDropdownElements(dropdown) {
        const elements = [
            { selector: '.dropdown-header', name: 'Cabeçalho' },
            { selector: '.shortcuts-count', name: 'Contador de atalhos' },
            { selector: '.shortcuts-container', name: 'Container de atalhos' },
            { selector: '.dropdown-footer', name: 'Rodapé' }
        ];

        elements.forEach(({ selector, name }) => {
            const element = dropdown.querySelector(selector);
            if (element) {
                this.log(`✓ ${name} encontrado`, 'success');
            } else {
                this.log(`✗ ${name} não encontrado`, 'warning');
            }
        });

        // Verificar se tem campo de busca (só se tiver mais de 3 atalhos)
        if (this.shortcuts.length > 3) {
            const searchInput = dropdown.querySelector('.search-input');
            if (searchInput) {
                this.log("✓ Campo de busca presente", 'success');
            } else {
                this.log("✗ Campo de busca não encontrado", 'warning');
            }
        }

        // Verificar itens de atalhos
        const shortcutItems = dropdown.querySelectorAll('.shortcut-item');
        this.log(`${shortcutItems.length} itens de atalhos exibidos`, 'info');
    }

    async testKeyboardShortcuts() {
        this.log("Testando atalhos de teclado...");

        try {
            const testField = this.createTestField();
            document.body.appendChild(testField);
            testField.focus();

            // Testar Ctrl+Espaço
            const ctrlSpaceEvent = new KeyboardEvent('keydown', {
                key: ' ',
                code: 'Space',
                ctrlKey: true,
                bubbles: true
            });

            document.dispatchEvent(ctrlSpaceEvent);
            await this.sleep(300);

            const dropdown = document.querySelector('.symplifika-dropdown');
            if (dropdown && dropdown.classList.contains('visible')) {
                this.log("✓ Ctrl+Espaço abre dropdown", 'success');

                // Testar ESC para fechar
                const escEvent = new KeyboardEvent('keydown', {
                    key: 'Escape',
                    code: 'Escape',
                    bubbles: true
                });

                document.dispatchEvent(escEvent);
                await this.sleep(200);

                if (!dropdown.classList.contains('visible')) {
                    this.log("✓ ESC fecha dropdown", 'success');
                } else {
                    this.log("✗ ESC não fechou dropdown", 'warning');
                }
            } else {
                this.log("✗ Ctrl+Espaço não abriu dropdown", 'warning');
            }

            testField.remove();

        } catch (error) {
            this.log(`Erro nos atalhos de teclado: ${error.message}`, 'error');
        }
    }

    async testFieldDetection() {
        this.log("Testando detecção de campos de texto...");

        const fieldTypes = [
            { type: 'input[type="text"]', name: 'Input texto' },
            { type: 'input[type="email"]', name: 'Input email' },
            { type: 'textarea', name: 'Textarea' },
            { type: 'div[contenteditable="true"]', name: 'Div editável' }
        ];

        for (const { type, name } of fieldTypes) {
            try {
                const field = document.createElement(type.split('[')[0]);

                if (type.includes('[')) {
                    const attr = type.match(/\[(.+)="(.+)"\]/);
                    if (attr) {
                        field.setAttribute(attr[1], attr[2]);
                    }
                }

                field.style.cssText = 'width: 200px; height: 40px; margin: 10px;';
                document.body.appendChild(field);

                field.focus();
                await this.sleep(200);

                const icon = document.querySelector('.symplifika-icon.visible');
                if (icon) {
                    this.log(`✓ ${name} detectado corretamente`, 'success');
                } else {
                    this.log(`✗ ${name} não foi detectado`, 'warning');
                }

                field.remove();

            } catch (error) {
                this.log(`Erro testando ${name}: ${error.message}`, 'error');
            }
        }
    }

    async testShortcutInsertion() {
        this.log("Testando inserção de atalhos...");

        if (this.shortcuts.length === 0) {
            this.log("Sem atalhos para testar inserção", 'warning');
            return;
        }

        try {
            const testField = this.createTestField('input');
            document.body.appendChild(testField);
            testField.focus();

            // Simular inserção do primeiro atalho
            const shortcut = this.shortcuts[0];

            // Usar a função global insertShortcut
            if (typeof window.insertShortcut === 'function') {
                await window.insertShortcut(shortcut.id);

                await this.sleep(500);

                if (testField.value && testField.value.length > 0) {
                    this.log(`✓ Atalho inserido: "${testField.value.substring(0, 50)}..."`, 'success');
                } else {
                    this.log("✗ Nenhum conteúdo foi inserido", 'warning');
                }
            } else {
                this.log("✗ Função insertShortcut não encontrada", 'error');
            }

            testField.remove();

        } catch (error) {
            this.log(`Erro na inserção: ${error.message}`, 'error');
        }
    }

    async testSearchFunctionality() {
        this.log("Testando funcionalidade de busca...");

        if (this.shortcuts.length <= 3) {
            this.log("Poucos atalhos para testar busca", 'info');
            return;
        }

        try {
            const testField = this.createTestField();
            document.body.appendChild(testField);
            testField.focus();

            // Abrir dropdown
            testField.focus();
            await this.sleep(200);

            const icon = document.querySelector('.symplifika-icon');
            if (icon) {
                icon.click();
                await this.sleep(300);

                const searchInput = document.querySelector('.search-input');
                if (searchInput) {
                    // Testar busca
                    const searchTerm = this.shortcuts[0].title.substring(0, 3);
                    searchInput.value = searchTerm;
                    searchInput.dispatchEvent(new Event('input', { bubbles: true }));

                    await this.sleep(300);

                    const visibleItems = document.querySelectorAll('.shortcut-item:not([style*="display: none"])');
                    this.log(`Busca por "${searchTerm}" retornou ${visibleItems.length} resultados`, 'info');

                    if (visibleItems.length > 0) {
                        this.log("✓ Funcionalidade de busca operacional", 'success');
                    } else {
                        this.log("✗ Busca não retornou resultados", 'warning');
                    }
                } else {
                    this.log("Campo de busca não encontrado", 'warning');
                }
            }

            testField.remove();

        } catch (error) {
            this.log(`Erro na busca: ${error.message}`, 'error');
        }
    }

    createTestField(type = 'input') {
        const field = document.createElement(type);

        if (type === 'input') {
            field.type = 'text';
            field.placeholder = 'Campo de teste';
        } else if (type === 'textarea') {
            field.placeholder = 'Textarea de teste';
        }

        field.style.cssText = `
            width: 300px;
            height: 40px;
            margin: 10px;
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
        `;

        return field;
    }

    async sendMessage(message, timeout = 3000) {
        return new Promise((resolve, reject) => {
            if (!chrome.runtime) {
                reject(new Error('Chrome runtime não disponível'));
                return;
            }

            const timeoutId = setTimeout(() => {
                reject(new Error('Timeout na mensagem'));
            }, timeout);

            chrome.runtime.sendMessage(message, (response) => {
                clearTimeout(timeoutId);

                if (chrome.runtime.lastError) {
                    reject(new Error(chrome.runtime.lastError.message));
                    return;
                }

                resolve(response);
            });
        });
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    generateReport() {
        console.log("\n" + "=".repeat(60));
        console.log("📊 RELATÓRIO DOS TESTES");
        console.log("=".repeat(60));

        const totalTests = this.testResults.length;
        const successCount = this.testResults.filter(r => r.type === 'success').length;
        const warningCount = this.testResults.filter(r => r.type === 'warning').length;
        const errorCount = this.testResults.filter(r => r.type === 'error').length;

        console.log(`Total de verificações: ${totalTests}`);
        console.log(`✅ Sucessos: ${successCount}`);
        console.log(`⚠️  Avisos: ${warningCount}`);
        console.log(`❌ Erros: ${errorCount}`);

        const successRate = ((successCount / totalTests) * 100).toFixed(1);
        console.log(`📈 Taxa de sucesso: ${successRate}%`);

        if (errorCount > 0) {
            console.log("\n❌ ERROS ENCONTRADOS:");
            this.testResults
                .filter(r => r.type === 'error')
                .forEach(r => console.log(`  - ${r.message}`));
        }

        if (warningCount > 0) {
            console.log("\n⚠️  AVISOS:");
            this.testResults
                .filter(r => r.type === 'warning')
                .forEach(r => console.log(`  - ${r.message}`));
        }

        console.log("\n" + "=".repeat(60));

        if (successRate >= 80) {
            console.log("🎉 Quick Action Icon funcionando bem!");
        } else if (successRate >= 60) {
            console.log("⚠️  Quick Action Icon com problemas menores");
        } else {
            console.log("❌ Quick Action Icon com problemas sérios");
        }
    }
}

// Função para executar os testes
async function testQuickAction() {
    const tester = new QuickActionTester();
    await tester.runAllTests();
}

// Auto-executar se não estiver sendo importado
if (typeof window !== 'undefined') {
    // Aguardar carregamento completo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(testQuickAction, 1000);
        });
    } else {
        setTimeout(testQuickAction, 1000);
    }
}

// Exportar para uso manual
window.testQuickAction = testQuickAction;

console.log("🧪 Teste do Quick Action Icon carregado. Execute testQuickAction() para iniciar.");
