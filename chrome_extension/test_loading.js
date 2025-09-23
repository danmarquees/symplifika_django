// Teste de Carregamento - Symplifika Chrome Extension
// Arquivo simples para verificar se os content scripts estão carregando

console.log("🔍 TESTE DE CARREGAMENTO INICIADO");
console.log("Timestamp:", new Date().toISOString());

// 1. Verificar se estamos em um content script
console.log("🔧 Contexto:", window === window.top ? "Top frame" : "Iframe");
console.log("🔧 URL:", window.location.href);

// 2. Verificar disponibilidade das APIs do Chrome
console.log("🔧 Chrome Runtime disponível:", typeof chrome !== 'undefined' && typeof chrome.runtime !== 'undefined');
console.log("🔧 Chrome Storage disponível:", typeof chrome !== 'undefined' && typeof chrome.storage !== 'undefined');

// 3. Verificar carregamento dos arquivos
console.log("🔧 QuickAccessIcon classe disponível:", typeof QuickAccessIcon !== 'undefined');
console.log("🔧 SymphilikaContentScript classe disponível:", typeof SymphilikaContentScript !== 'undefined');

// 4. Verificar DOM
console.log("🔧 DOM ready state:", document.readyState);
console.log("🔧 Body existe:", !!document.body);

// 5. Teste básico de criação de elemento
try {
    const testDiv = document.createElement('div');
    testDiv.id = 'symplifika-loading-test';
    testDiv.style.cssText = `
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        background: #4f46e5 !important;
        color: white !important;
        padding: 10px !important;
        border-radius: 4px !important;
        z-index: 999999 !important;
        font-family: Arial, sans-serif !important;
        font-size: 12px !important;
    `;
    testDiv.textContent = '🔧 Symplifika Test Loading OK';
    document.body.appendChild(testDiv);

    // Remover após 5 segundos
    setTimeout(() => {
        if (document.getElementById('symplifika-loading-test')) {
            document.getElementById('symplifika-loading-test').remove();
        }
    }, 5000);

    console.log("✅ Teste de DOM manipulation: OK");
} catch (error) {
    console.log("❌ Teste de DOM manipulation: ERRO", error.message);
}

// 6. Verificar se conseguimos acessar storage
if (typeof chrome !== 'undefined' && chrome.storage) {
    chrome.storage.local.get(['test'], (result) => {
        console.log("✅ Teste de Storage: OK", result);
    });
} else {
    console.log("❌ Teste de Storage: Chrome API não disponível");
}

// 7. Tentar criar instância básica do QuickAccessIcon (se disponível)
if (typeof QuickAccessIcon !== 'undefined') {
    try {
        // Mock básico do contentScript para teste
        const mockContentScript = {
            isEnabled: true,
            isAuthenticated: true,
            shortcuts: []
        };

        const testIcon = new QuickAccessIcon(mockContentScript);
        console.log("✅ Teste de instanciação QuickAccessIcon: OK");

        // Limpar após teste
        setTimeout(() => {
            if (testIcon && typeof testIcon.destroy === 'function') {
                testIcon.destroy();
            }
        }, 2000);

    } catch (error) {
        console.log("❌ Teste de instanciação QuickAccessIcon: ERRO", error.message);
    }
} else {
    console.log("❌ QuickAccessIcon não disponível para teste");
}

// 8. Tentar criar instância do ContentScript (se disponível)
if (typeof SymphilikaContentScript !== 'undefined') {
    try {
        // Não instanciar para não conflitar, apenas verificar se a classe existe
        console.log("✅ SymphilikaContentScript classe: OK");

        // Verificar se já existe uma instância global
        if (window.symphilikaContentScript) {
            console.log("✅ Instância global já existe");
            console.log("   - isEnabled:", window.symphilikaContentScript.isEnabled);
            console.log("   - isAuthenticated:", window.symphilikaContentScript.isAuthenticated);
            console.log("   - quickAccessIcon:", !!window.symphilikaContentScript.quickAccessIcon);
        } else {
            console.log("ℹ️ Instância global não existe ainda");
        }

    } catch (error) {
        console.log("❌ Teste SymphilikaContentScript: ERRO", error.message);
    }
} else {
    console.log("❌ SymphilikaContentScript não disponível para teste");
}

// 9. Verificar campos na página
const fieldSelector = 'input[type="text"], input[type="email"], input[type="search"], input[type="url"], input[type="tel"], input[type="number"], textarea, [contenteditable="true"]';
const fields = document.querySelectorAll(fieldSelector);
console.log("🔧 Campos de texto encontrados:", fields.length);

if (fields.length > 0) {
    console.log("🔧 Primeiro campo:", fields[0].tagName, fields[0].type || 'N/A');
}

// 10. Agendar verificações adicionais
setTimeout(() => {
    console.log("🔍 VERIFICAÇÃO APÓS 3 SEGUNDOS:");
    console.log("🔧 QuickAccessIcon agora:", typeof QuickAccessIcon !== 'undefined');
    console.log("🔧 ContentScript instância:", !!window.symphilikaContentScript);

    if (window.symphilikaContentScript && window.symphilikaContentScript.quickAccessIcon) {
        const qa = window.symphilikaContentScript.quickAccessIcon;
        console.log("🔧 QuickAccessIcon ativo:", !qa.isDestroyed);
        console.log("🔧 Ícones criados:", qa.activeIcons ? qa.activeIcons.size : 0);
    }
}, 3000);

setTimeout(() => {
    console.log("🔍 VERIFICAÇÃO FINAL APÓS 10 SEGUNDOS:");

    // Verificar se ícones aparecem no DOM
    const icons = document.querySelectorAll('.symplifika-icon');
    console.log("🔧 Ícones no DOM:", icons.length);

    if (icons.length > 0) {
        icons.forEach((icon, index) => {
            console.log(`🔧 Ícone ${index + 1}:`, {
                display: icon.style.display,
                position: icon.style.position,
                zIndex: icon.style.zIndex
            });
        });
    }

    console.log("🔍 TESTE DE CARREGAMENTO CONCLUÍDO");
}, 10000);

// 11. Disponibilizar função global para teste manual
window.symplifikaLoadingTest = {
    checkStatus: () => {
        console.log("📊 STATUS ATUAL:");
        console.log("- QuickAccessIcon:", typeof QuickAccessIcon !== 'undefined');
        console.log("- ContentScript:", !!window.symphilikaContentScript);
        console.log("- DOM ready:", document.readyState);
        console.log("- Campos:", document.querySelectorAll(fieldSelector).length);
        console.log("- Ícones:", document.querySelectorAll('.symplifika-icon').length);
    },

    forceTest: () => {
        console.log("🚀 TESTE FORÇADO:");
        if (window.symphilikaContentScript?.quickAccessIcon?.forceTestIcon) {
            window.symphilikaContentScript.quickAccessIcon.forceTestIcon();
        } else {
            console.log("❌ Função forceTestIcon não disponível");
        }
    }
};

console.log("💡 Use window.symplifikaLoadingTest.checkStatus() para verificar status a qualquer momento");
console.log("💡 Use window.symplifikaLoadingTest.forceTest() para teste forçado");
