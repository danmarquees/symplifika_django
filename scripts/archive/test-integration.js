/**
 * Symplifika API Integration Tests
 * Sistema de testes para verificar a integração com as APIs
 */

class SymphilikaAPITester {
    constructor() {
        this.baseUrl = '/shortcuts/api';
        this.results = {
            passed: 0,
            failed: 0,
            tests: []
        };
    }

    /**
     * Executa todos os testes
     */
    async runAllTests() {
        console.log('🚀 Iniciando testes de integração da API...');

        try {
            // Testes de categorias
            await this.testCategoriesAPI();

            // Testes de atalhos
            await this.testShortcutsAPI();

            // Testes de estatísticas
            await this.testStatsAPI();

            // Mostrar resultados
            this.showResults();

        } catch (error) {
            console.error('❌ Erro durante execução dos testes:', error);
        }
    }

    /**
     * Testa API de categorias
     */
    async testCategoriesAPI() {
        console.log('📁 Testando API de Categorias...');

        // Teste 1: Listar categorias
        await this.test('GET Categories', async () => {
            const response = await fetch(`${this.baseUrl}/categories/`);
            if (!response.ok) throw new Error(`Status: ${response.status}`);
            const data = await response.json();
            return Array.isArray(data.results || data);
        });

        // Teste 2: Criar categoria
        await this.test('POST Category', async () => {
            const categoryData = {
                name: 'Teste API',
                description: 'Categoria criada via teste',
                color: '#ff6b6b'
            };

            const response = await fetch(`${this.baseUrl}/categories/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(categoryData)
            });

            if (!response.ok) throw new Error(`Status: ${response.status}`);
            const data = await response.json();

            // Salvar ID para limpeza posterior
            this.testCategoryId = data.id;

            return data.name === categoryData.name;
        });
    }

    /**
     * Testa API de atalhos
     */
    async testShortcutsAPI() {
        console.log('⚡ Testando API de Atalhos...');

        // Teste 1: Listar atalhos
        await this.test('GET Shortcuts', async () => {
            const response = await fetch(`${this.baseUrl}/shortcuts/`);
            if (!response.ok) throw new Error(`Status: ${response.status}`);
            const data = await response.json();
            return Array.isArray(data.results || data);
        });

        // Teste 2: Criar atalho
        await this.test('POST Shortcut', async () => {
            const shortcutData = {
                trigger: 'teste-api',
                title: 'Teste API',
                content: 'Conteúdo de teste criado via API',
                expansion_type: 'static',
                is_active: true,
                category: this.testCategoryId || null
            };

            const response = await fetch(`${this.baseUrl}/shortcuts/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(shortcutData)
            });

            if (!response.ok) throw new Error(`Status: ${response.status}`);
            const data = await response.json();

            // Salvar ID para testes posteriores
            this.testShortcutId = data.id;

            return data.trigger === shortcutData.trigger;
        });

        // Teste 3: Usar atalho
        if (this.testShortcutId) {
            await this.test('Use Shortcut', async () => {
                const response = await fetch(`${this.baseUrl}/shortcuts/${this.testShortcutId}/use/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify({ context: 'test' })
                });

                if (!response.ok) throw new Error(`Status: ${response.status}`);
                const data = await response.json();

                return typeof data.content === 'string' && data.content.length > 0;
            });
        }

        // Teste 4: Buscar atalhos
        await this.test('Search Shortcuts', async () => {
            const response = await fetch(`${this.baseUrl}/shortcuts/search/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ query: 'teste' })
            });

            if (!response.ok) throw new Error(`Status: ${response.status}`);
            const data = await response.json();

            return Array.isArray(data.results || data);
        });
    }

    /**
     * Testa API de estatísticas
     */
    async testStatsAPI() {
        console.log('📊 Testando API de Estatísticas...');

        // Teste 1: Estatísticas gerais
        await this.test('GET Stats', async () => {
            const response = await fetch(`${this.baseUrl}/shortcuts/stats/`);
            if (!response.ok) throw new Error(`Status: ${response.status}`);
            const data = await response.json();

            return typeof data === 'object' &&
                   typeof data.total_shortcuts === 'number';
        });

        // Teste 2: Atalhos mais usados
        await this.test('GET Most Used', async () => {
            const response = await fetch(`${this.baseUrl}/shortcuts/most-used/`);
            if (!response.ok) throw new Error(`Status: ${response.status}`);
            const data = await response.json();

            return Array.isArray(data.results || data);
        });
    }

    /**
     * Executa um teste individual
     */
    async test(name, testFunction) {
        try {
            const result = await testFunction();
            if (result) {
                console.log(`✅ ${name} - PASSOU`);
                this.results.passed++;
                this.results.tests.push({ name, status: 'PASSOU', error: null });
            } else {
                console.log(`❌ ${name} - FALHOU (resultado falso)`);
                this.results.failed++;
                this.results.tests.push({ name, status: 'FALHOU', error: 'Resultado falso' });
            }
        } catch (error) {
            console.log(`❌ ${name} - ERRO: ${error.message}`);
            this.results.failed++;
            this.results.tests.push({ name, status: 'ERRO', error: error.message });
        }
    }

    /**
     * Obtém token CSRF
     */
    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    /**
     * Mostra resultados dos testes
     */
    showResults() {
        console.log('\n📋 RESULTADOS DOS TESTES:');
        console.log(`✅ Passou: ${this.results.passed}`);
        console.log(`❌ Falhou: ${this.results.failed}`);
        console.log(`📊 Total: ${this.results.tests.length}`);

        if (this.results.failed > 0) {
            console.log('\n❌ TESTES FALHARAM:');
            this.results.tests
                .filter(test => test.status !== 'PASSOU')
                .forEach(test => {
                    console.log(`  - ${test.name}: ${test.error}`);
                });
        }

        // Limpar dados de teste
        this.cleanup();

        // Mostrar na interface se disponível
        this.showResultsInUI();
    }

    /**
     * Limpa dados criados durante os testes
     */
    async cleanup() {
        console.log('🧹 Limpando dados de teste...');

        try {
            // Deletar atalho de teste
            if (this.testShortcutId) {
                await fetch(`${this.baseUrl}/shortcuts/${this.testShortcutId}/`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': this.getCSRFToken()
                    }
                });
            }

            // Deletar categoria de teste
            if (this.testCategoryId) {
                await fetch(`${this.baseUrl}/categories/${this.testCategoryId}/`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': this.getCSRFToken()
                    }
                });
            }

            console.log('✅ Limpeza concluída');
        } catch (error) {
            console.warn('⚠️ Erro durante limpeza:', error);
        }
    }

    /**
     * Mostra resultados na interface (se estiver no dashboard)
     */
    showResultsInUI() {
        if (window.Symplifika && window.Symplifika.Toast) {
            const message = `Testes: ${this.results.passed} passou, ${this.results.failed} falhou`;
            const type = this.results.failed > 0 ? 'warning' : 'success';
            window.Symplifika.Toast.show(message, type, 8000);
        }

        // Criar elemento de resultados se não existir
        let resultsContainer = document.getElementById('test-results');
        if (!resultsContainer) {
            resultsContainer = document.createElement('div');
            resultsContainer.id = 'test-results';
            resultsContainer.className = 'fixed bottom-4 left-4 z-50 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg p-4 shadow-lg max-w-md';
            document.body.appendChild(resultsContainer);
        }

        const successRate = Math.round((this.results.passed / this.results.tests.length) * 100);
        const statusColor = successRate === 100 ? 'text-green-600' : successRate >= 80 ? 'text-yellow-600' : 'text-red-600';

        resultsContainer.innerHTML = `
            <div class="flex justify-between items-center mb-2">
                <h3 class="font-semibold text-gray-900 dark:text-white">Testes de API</h3>
                <button onclick="this.parentElement.parentElement.remove()" class="text-gray-400 hover:text-gray-600">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
                    </svg>
                </button>
            </div>
            <div class="space-y-1 text-sm">
                <div class="flex justify-between">
                    <span class="text-gray-600 dark:text-gray-300">Taxa de sucesso:</span>
                    <span class="${statusColor} font-medium">${successRate}%</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-600 dark:text-gray-300">Passou:</span>
                    <span class="text-green-600 font-medium">${this.results.passed}</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-600 dark:text-gray-300">Falhou:</span>
                    <span class="text-red-600 font-medium">${this.results.failed}</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-600 dark:text-gray-300">Total:</span>
                    <span class="text-gray-900 dark:text-white font-medium">${this.results.tests.length}</span>
                </div>
            </div>
            ${this.results.failed > 0 ? `
                <div class="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
                    <button onclick="this.nextElementSibling.classList.toggle('hidden')" class="text-xs text-blue-600 hover:text-blue-800">
                        Ver detalhes dos erros
                    </button>
                    <div class="hidden mt-2 text-xs space-y-1">
                        ${this.results.tests
                            .filter(test => test.status !== 'PASSOU')
                            .map(test => `<div class="text-red-600">• ${test.name}: ${test.error}</div>`)
                            .join('')}
                    </div>
                </div>
            ` : ''}
        `;

        // Auto remover após 15 segundos
        setTimeout(() => {
            if (resultsContainer.parentNode) {
                resultsContainer.remove();
            }
        }, 15000);
    }
}

// Função para executar testes manualmente
window.testSymphilikaAPI = async function() {
    const tester = new SymphilikaAPITester();
    await tester.runAllTests();
};

// Auto executar testes se parâmetro estiver presente na URL
if (window.location.search.includes('test-api')) {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(() => {
            window.testSymphilikaAPI();
        }, 2000);
    });
}

// Exportar para console
if (typeof window !== 'undefined') {
    window.SymphilikaAPITester = SymphilikaAPITester;
    console.log('🧪 Tester de API disponível. Execute testSymphilikaAPI() para testar as APIs.');
}
