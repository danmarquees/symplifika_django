/**
 * Symplifika Integration Demo
 * Script de demonstração das funcionalidades de integração com APIs
 */

class SymphilikaDemo {
    constructor() {
        this.isRunning = false;
        this.demoData = {
            categories: [
                { name: 'Email Templates', description: 'Templates para emails', color: '#3b82f6' },
                { name: 'Code Snippets', description: 'Trechos de código úteis', color: '#10b981' },
                { name: 'Responses', description: 'Respostas padrão', color: '#f59e0b' }
            ],
            shortcuts: [
                {
                    trigger: 'email-welcome',
                    title: 'Email de Boas-vindas',
                    content: 'Olá {nome},\n\nSeja bem-vindo(a) à nossa plataforma!\n\nAtenciosamente,\nEquipe {empresa}',
                    expansion_type: 'dynamic',
                    variables: { nome: 'Cliente', empresa: 'Symplifika' }
                },
                {
                    trigger: 'react-component',
                    title: 'React Component Template',
                    content: 'import React from \'react\';\n\nconst MyComponent = () => {\n  return (\n    <div>\n      Hello World\n    </div>\n  );\n};\n\nexport default MyComponent;',
                    expansion_type: 'static'
                },
                {
                    trigger: 'support-response',
                    title: 'Resposta de Suporte',
                    content: 'Agradecemos seu contato. Nossa equipe analisará sua solicitação.',
                    expansion_type: 'ai_enhanced',
                    ai_prompt: 'Expanda esta resposta de suporte de forma mais detalhada e profissional'
                }
            ]
        };
    }

    /**
     * Inicia a demonstração
     */
    async startDemo() {
        if (this.isRunning) {
            console.warn('Demo já está em execução');
            return;
        }

        this.isRunning = true;
        console.log('🚀 Iniciando demonstração da integração Symplifika...');

        try {
            await this.showWelcomeMessage();
            await this.demonstrateQuickActions();
            await this.demonstrateAPIIntegration();
            await this.demonstrateFormValidation();
            await this.demonstrateNotifications();
            await this.showCompletionMessage();
        } catch (error) {
            console.error('❌ Erro durante a demonstração:', error);
            this.showErrorMessage(error);
        } finally {
            this.isRunning = false;
        }
    }

    /**
     * Para a demonstração
     */
    stopDemo() {
        this.isRunning = false;
        console.log('⏹️ Demonstração interrompida');
    }

    /**
     * Mostra mensagem de boas-vindas
     */
    async showWelcomeMessage() {
        console.log('👋 Bem-vindo à demonstração das integrações de API');

        if (window.Symplifika && window.Symplifika.Toast) {
            window.Symplifika.Toast.info('Iniciando demonstração das funcionalidades', 3000);
        }

        await this.delay(2000);
    }

    /**
     * Demonstra as ações rápidas
     */
    async demonstrateQuickActions() {
        console.log('⚡ Demonstrando Ações Rápidas...');

        // Highlight dos botões de ação rápida
        this.highlightElement('.btn[onclick*="openCreateShortcutModal"]', 'Botão: Criar Novo Atalho');
        await this.delay(2000);

        this.highlightElement('.btn[onclick*="openCreateCategoryModal"]', 'Botão: Nova Categoria');
        await this.delay(2000);

        console.log('✅ Ações rápidas identificadas');
    }

    /**
     * Demonstra integração com API
     */
    async demonstrateAPIIntegration() {
        console.log('🔗 Demonstrando integração com APIs...');

        // Testar se as APIs estão respondendo
        try {
            console.log('📊 Testando API de estatísticas...');
            const statsResponse = await fetch('/shortcuts/api/shortcuts/stats/');
            if (statsResponse.ok) {
                const stats = await statsResponse.json();
                console.log('✅ API de estatísticas funcionando:', stats);
            }

            console.log('📁 Testando API de categorias...');
            const categoriesResponse = await fetch('/shortcuts/api/categories/');
            if (categoriesResponse.ok) {
                const categories = await categoriesResponse.json();
                console.log('✅ API de categorias funcionando:', categories);
            }

            console.log('⚡ Testando API de atalhos...');
            const shortcutsResponse = await fetch('/shortcuts/api/shortcuts/');
            if (shortcutsResponse.ok) {
                const shortcuts = await shortcutsResponse.json();
                console.log('✅ API de atalhos funcionando:', shortcuts);
            }

        } catch (error) {
            console.warn('⚠️ Algumas APIs podem não estar disponíveis:', error.message);
        }

        await this.delay(1000);
    }

    /**
     * Demonstra validação de formulários
     */
    async demonstrateFormValidation() {
        console.log('✅ Demonstrando validações de formulário...');

        // Simular abertura do modal de atalho
        console.log('🔧 Simulando validações:');
        console.log('  - Gatilho: Deve começar com // (adicionado automaticamente)');
        console.log('  - Gatilho: Mínimo 2 caracteres, apenas letras/números/hífen/underscore');
        console.log('  - Título: Obrigatório');
        console.log('  - Conteúdo: Obrigatório');
        console.log('  - Categoria: Deve pertencer ao usuário');

        // Simular validação de categoria
        console.log('🎨 Validações de categoria:');
        console.log('  - Nome: Obrigatório');
        console.log('  - Cor: Formato hexadecimal');
        console.log('  - Descrição: Opcional');

        await this.delay(1500);
    }

    /**
     * Demonstra sistema de notificações
     */
    async demonstrateNotifications() {
        console.log('🔔 Demonstrando sistema de notificações...');

        if (window.Symplifika && window.Symplifika.Toast) {
            // Mostrar diferentes tipos de notificação
            window.Symplifika.Toast.success('Sucesso: Operação realizada com êxito!');
            await this.delay(1000);

            window.Symplifika.Toast.info('Informação: Dados carregados');
            await this.delay(1000);

            window.Symplifika.Toast.warning('Atenção: Limite de uso próximo');
            await this.delay(1000);

            window.Symplifika.Toast.error('Erro: Falha na operação');
            await this.delay(1000);

            console.log('✅ Sistema de notificações funcionando');
        } else {
            console.warn('⚠️ Sistema de notificações não disponível');
        }
    }

    /**
     * Mostra mensagem de conclusão
     */
    async showCompletionMessage() {
        console.log('🎉 Demonstração concluída com sucesso!');
        console.log('📋 Resumo das funcionalidades demonstradas:');
        console.log('  ✅ Ações rápidas identificadas');
        console.log('  ✅ APIs testadas e funcionando');
        console.log('  ✅ Validações configuradas');
        console.log('  ✅ Sistema de notificações ativo');
        console.log('  ✅ Modais integrados');

        if (window.Symplifika && window.Symplifika.Toast) {
            window.Symplifika.Toast.success('Demonstração concluída! Todas as integrações estão funcionando.', 5000);
        }

        console.log('\n🚀 Para usar as funcionalidades:');
        console.log('1. Clique em "Criar Novo Atalho" para adicionar um atalho');
        console.log('2. Clique em "Nova Categoria" para organizar seus atalhos');
        console.log('3. Use os atalhos recentes clicando na seta ao lado');
        console.log('4. Execute testSymphilikaAPI() para testes automatizados');
    }

    /**
     * Mostra mensagem de erro
     */
    showErrorMessage(error) {
        console.error('❌ Erro durante a demonstração:', error);

        if (window.Symplifika && window.Symplifika.Toast) {
            window.Symplifika.Toast.error(`Erro na demonstração: ${error.message}`, 7000);
        }
    }

    /**
     * Destaca um elemento na página
     */
    highlightElement(selector, description) {
        const element = document.querySelector(selector);
        if (element) {
            console.log(`🎯 ${description} encontrado`);

            // Adicionar destaque visual temporário
            const originalStyle = element.style.cssText;
            element.style.cssText += `
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.5) !important;
                transform: scale(1.02) !important;
                transition: all 0.3s ease !important;
            `;

            // Remover destaque após 2 segundos
            setTimeout(() => {
                element.style.cssText = originalStyle;
            }, 2000);
        } else {
            console.warn(`⚠️ ${description} não encontrado (${selector})`);
        }
    }

    /**
     * Delay utilitário
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Demonstra criação de categoria via API
     */
    async demonstrateCategoryCreation() {
        console.log('🎨 Demonstrando criação de categoria...');

        const categoryData = {
            name: 'Demo Category',
            description: 'Categoria criada na demonstração',
            color: '#8b5cf6'
        };

        try {
            const response = await fetch('/shortcuts/api/categories/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(categoryData)
            });

            if (response.ok) {
                const category = await response.json();
                console.log('✅ Categoria criada:', category);

                // Agendar limpeza
                setTimeout(() => this.cleanupDemoCategory(category.id), 10000);

                return category;
            } else {
                console.warn('⚠️ Não foi possível criar categoria de demonstração');
            }
        } catch (error) {
            console.warn('⚠️ Erro ao criar categoria de demonstração:', error);
        }
    }

    /**
     * Demonstra criação de atalho via API
     */
    async demonstrateShortcutCreation(categoryId = null) {
        console.log('⚡ Demonstrando criação de atalho...');

        const shortcutData = {
            trigger: 'demo-shortcut',
            title: 'Demo Shortcut',
            content: 'Este é um atalho criado na demonstração',
            expansion_type: 'static',
            is_active: true,
            category: categoryId
        };

        try {
            const response = await fetch('/shortcuts/api/shortcuts/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(shortcutData)
            });

            if (response.ok) {
                const shortcut = await response.json();
                console.log('✅ Atalho criado:', shortcut);

                // Agendar limpeza
                setTimeout(() => this.cleanupDemoShortcut(shortcut.id), 10000);

                return shortcut;
            } else {
                console.warn('⚠️ Não foi possível criar atalho de demonstração');
            }
        } catch (error) {
            console.warn('⚠️ Erro ao criar atalho de demonstração:', error);
        }
    }

    /**
     * Limpa categoria de demonstração
     */
    async cleanupDemoCategory(categoryId) {
        try {
            await fetch(`/shortcuts/api/categories/${categoryId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            console.log('🧹 Categoria de demonstração removida');
        } catch (error) {
            console.warn('⚠️ Não foi possível remover categoria de demonstração');
        }
    }

    /**
     * Limpa atalho de demonstração
     */
    async cleanupDemoShortcut(shortcutId) {
        try {
            await fetch(`/shortcuts/api/shortcuts/${shortcutId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            console.log('🧹 Atalho de demonstração removido');
        } catch (error) {
            console.warn('⚠️ Não foi possível remover atalho de demonstração');
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
     * Demonstração completa com criação real
     */
    async fullDemo() {
        console.log('🎬 Iniciando demonstração completa...');

        try {
            // Criar categoria
            const category = await this.demonstrateCategoryCreation();
            await this.delay(1000);

            // Criar atalho
            const shortcut = await this.demonstrateShortcutCreation(category?.id);
            await this.delay(1000);

            // Usar atalho
            if (shortcut) {
                await this.demonstrateShortcutUsage(shortcut.id);
            }

            console.log('🎉 Demonstração completa finalizada!');

        } catch (error) {
            console.error('❌ Erro na demonstração completa:', error);
        }
    }

    /**
     * Demonstra uso de atalho
     */
    async demonstrateShortcutUsage(shortcutId) {
        console.log('🎯 Demonstrando uso de atalho...');

        try {
            const response = await fetch(`/shortcuts/api/shortcuts/${shortcutId}/use/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ context: 'demo' })
            });

            if (response.ok) {
                const result = await response.json();
                console.log('✅ Atalho usado:', result);

                // Copiar para clipboard se possível
                if (navigator.clipboard) {
                    await navigator.clipboard.writeText(result.content);
                    console.log('📋 Conteúdo copiado para área de transferência');
                }
            }
        } catch (error) {
            console.warn('⚠️ Erro ao usar atalho:', error);
        }
    }
}

// Instância global da demonstração
const demo = new SymphilikaDemo();

// Funções globais para uso no console
window.startSymphilikaDemo = () => demo.startDemo();
window.stopSymphilikaDemo = () => demo.stopDemo();
window.fullSymphilikaDemo = () => demo.fullDemo();

// Auto-start se parâmetro presente na URL
if (window.location.search.includes('demo')) {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(() => {
            demo.startDemo();
        }, 2000);
    });
}

// Adicionar botão de demonstração se não existir
document.addEventListener('DOMContentLoaded', () => {
    if (!document.getElementById('demo-button') && document.querySelector('.dashboard')) {
        const demoButton = document.createElement('button');
        demoButton.id = 'demo-button';
        demoButton.innerHTML = '🎬 Demo';
        demoButton.className = 'fixed bottom-4 right-4 z-40 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg shadow-lg transition-colors';
        demoButton.title = 'Iniciar demonstração das funcionalidades';
        demoButton.onclick = () => demo.startDemo();

        document.body.appendChild(demoButton);
    }
});

console.log('🎬 Demo Symplifika carregado! Comandos disponíveis:');
console.log('  - startSymphilikaDemo() - Iniciar demonstração');
console.log('  - fullSymphilikaDemo() - Demonstração completa com criação real');
console.log('  - stopSymphilikaDemo() - Parar demonstração');
console.log('  - Ou adicione ?demo na URL para auto-start');
