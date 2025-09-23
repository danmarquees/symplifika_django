// Verificação Rápida - Symplifika Chrome Extension
// Execute este arquivo no console para diagnosticar problemas comuns

console.log("🔍 VERIFICAÇÃO RÁPIDA - Symplifika Extension");
console.log("=" .repeat(50));

// 1. Verificar se a extensão carregou
console.log("1️⃣ Verificando carregamento da extensão...");
const extensionLoaded = {
    quickAccessIcon: typeof QuickAccessIcon !== 'undefined',
    contentScript: typeof window.symphilikaContentScript !== 'undefined' && window.symphilikaContentScript !== null
};

console.log("   - QuickAccessIcon:", extensionLoaded.quickAccessIcon ? "✅ Carregado" : "❌ Não carregado");
console.log("   - ContentScript:", extensionLoaded.contentScript ? "✅ Carregado" : "❌ Não carregado");

// 2. Verificar storage
console.log("\n2️⃣ Verificando storage...");
chrome.storage.local.get(null).then(storage => {
    console.log("   - Token existe:", !!storage.token ? "✅ Sim" : "❌ Não");
    console.log("   - isEnabled:", storage.isEnabled !== false ? "✅ Habilitado" : "❌ Desabilitado");
    console.log("   - Shortcuts:", storage.shortcuts ? storage.shortcuts.length : 0);
    console.log("   - Base URL:", storage.baseURL || "http://localhost:8000");
});

// 3. Verificar campos detectados
console.log("\n3️⃣ Verificando detecção de campos...");
const fieldSelector = [
    'input[type="text"]',
    'input[type="email"]',
    'input[type="search"]',
    'input[type="url"]',
    'input[type="tel"]',
    'input[type="number"]',
    'textarea',
    '[contenteditable="true"]'
].join(', ');

const allFields = document.querySelectorAll(fieldSelector);
console.log("   - Campos encontrados:", allFields.length);

let validFields = 0;
allFields.forEach((field, index) => {
    const rect = field.getBoundingClientRect();
    const isValid = field.type !== 'password' &&
                   field.dataset.symplifikaIgnore !== 'true' &&
                   field.offsetParent !== null &&
                   rect.height >= 20 &&
                   rect.width >= 50;

    if (isValid) validFields++;

    if (index < 3) { // Mostrar apenas os 3 primeiros para não poluir o console
        console.log(`   - Campo ${index + 1}:`, {
            tag: field.tagName,
            type: field.type || 'N/A',
            valid: isValid ? "✅" : "❌",
            size: `${Math.round(rect.width)}x${Math.round(rect.height)}`
        });
    }
});

console.log("   - Campos válidos:", validFields);

// 4. Verificar ícones existentes
console.log("\n4️⃣ Verificando ícones criados...");
const existingIcons = document.querySelectorAll('.symplifika-icon');
console.log("   - Ícones no DOM:", existingIcons.length);

if (existingIcons.length > 0) {
    existingIcons.forEach((icon, index) => {
        console.log(`   - Ícone ${index + 1}:`, {
            display: icon.style.display || 'padrão',
            position: icon.style.position || 'padrão',
            zIndex: icon.style.zIndex || 'padrão'
        });
    });
}

// 5. Verificar estado da instância
console.log("\n5️⃣ Verificando estado da instância...");
if (window.symphilikaContentScript) {
    const cs = window.symphilikaContentScript;
    console.log("   - isEnabled:", cs.isEnabled ? "✅" : "❌");
    console.log("   - isAuthenticated:", cs.isAuthenticated ? "✅" : "❌");
    console.log("   - Shortcuts carregados:", cs.shortcuts ? cs.shortcuts.length : 0);

    if (cs.quickAccessIcon) {
        console.log("   - QuickAccessIcon instância:", "✅ Existe");
        console.log("   - Ícones ativos:", cs.quickAccessIcon.activeIcons ? cs.quickAccessIcon.activeIcons.size : 0);
    } else {
        console.log("   - QuickAccessIcon instância:", "❌ Não existe");
    }
} else {
    console.log("   - ContentScript não disponível para inspeção");
}

// 6. Teste de criação manual
console.log("\n6️⃣ Teste de criação manual...");
if (extensionLoaded.quickAccessIcon && validFields > 0) {
    console.log("   - Tentando criar instância de teste...");

    try {
        const testInstance = new QuickAccessIcon({
            isEnabled: true,
            isAuthenticated: true,
            shortcuts: []
        });
        console.log("   - Instância de teste:", "✅ Criada com sucesso");

        // Cleanup após teste
        setTimeout(() => {
            if (testInstance && typeof testInstance.destroy === 'function') {
                testInstance.destroy();
                console.log("   - Instância de teste destruída");
            }
        }, 2000);

    } catch (error) {
        console.log("   - Erro ao criar instância:", "❌", error.message);
    }
} else {
    console.log("   - Pré-requisitos não atendidos para teste manual");
}

// 7. Verificar CSS
console.log("\n7️⃣ Verificando CSS...");
const stylesheets = Array.from(document.styleSheets);
const hasSymplifikaCSS = stylesheets.some(sheet => {
    try {
        return Array.from(sheet.cssRules).some(rule =>
            rule.selectorText && rule.selectorText.includes('symplifika-icon')
        );
    } catch (e) {
        return false;
    }
});

console.log("   - CSS da extensão carregado:", hasSymplifikaCSS ? "✅ Sim" : "❌ Não");

// 8. Resumo e recomendações
console.log("\n📋 RESUMO E RECOMENDAÇÕES");
console.log("=" .repeat(50));

const issues = [];
const solutions = [];

if (!extensionLoaded.quickAccessIcon) {
    issues.push("QuickAccessIcon não carregou");
    solutions.push("Verificar se o arquivo quick-access-icon.js está incluído no manifest.json");
}

if (!extensionLoaded.contentScript) {
    issues.push("ContentScript não inicializou");
    solutions.push("Verificar se o content.js está carregando sem erros");
}

if (validFields === 0) {
    issues.push("Nenhum campo válido detectado");
    solutions.push("Verificar se existem campos de texto na página com tamanho adequado");
}

if (!hasSymplifikaCSS) {
    issues.push("CSS da extensão não carregou");
    solutions.push("Verificar se o content.css está incluído no manifest.json");
}

if (issues.length === 0) {
    console.log("✅ Nenhum problema óbvio detectado!");
    console.log("💡 Se o ícone ainda não aparece, pode ser um problema de:");
    console.log("   - Autenticação (token inválido)");
    console.log("   - Timing (aguardar alguns segundos)");
    console.log("   - CSP da página bloqueando scripts");
} else {
    console.log("❌ Problemas detectados:");
    issues.forEach((issue, index) => {
        console.log(`   ${index + 1}. ${issue}`);
    });

    console.log("\n💡 Soluções sugeridas:");
    solutions.forEach((solution, index) => {
        console.log(`   ${index + 1}. ${solution}`);
    });
}

console.log("\n🔧 Para executar teste forçado, execute no console:");
console.log("   window.symphilikaContentScript?.quickAccessIcon?.forceTestIcon();");

console.log("\n" + "=" .repeat(50));
console.log("Verificação concluída!");
