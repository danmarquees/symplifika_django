#!/usr/bin/env node

/**
 * Script de debug para Quick Action Icon - Symplifika
 * Testa comunicação entre content script e background script
 */

console.log('🔍 TESTE DE DEBUG - QUICK ACTION ICON');
console.log('=====================================');

// Simular teste no console do navegador
const testScript = `
// COLE ESTE CÓDIGO NO CONSOLE DO NAVEGADOR (F12)
console.log('🔍 Iniciando debug do Quick Action Icon...');

// 1. Verificar se a extensão está carregada
console.log('1. Verificando extensão...');
if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.id) {
    console.log('✅ Chrome runtime disponível');
    console.log('Extension ID:', chrome.runtime.id);
} else {
    console.log('❌ Chrome runtime não disponível');
}

// 2. Verificar estado do Quick Action
console.log('\\n2. Verificando Quick Action state...');
if (typeof state !== 'undefined') {
    console.log('✅ State encontrado:', state);
    console.log('Shortcuts carregados:', state.shortcuts.length);
    console.log('Shortcuts:', state.shortcuts);
} else {
    console.log('❌ State não encontrado - Quick Action pode não estar carregado');
}

// 3. Testar comunicação com background
console.log('\\n3. Testando comunicação com background...');
if (typeof chrome !== 'undefined' && chrome.runtime) {
    chrome.runtime.sendMessage({ type: 'PING' }, (response) => {
        if (chrome.runtime.lastError) {
            console.log('❌ Erro na comunicação:', chrome.runtime.lastError.message);
        } else {
            console.log('✅ Comunicação OK:', response);
        }
    });
    
    // Testar GET_SHORTCUTS
    chrome.runtime.sendMessage({ type: 'GET_SHORTCUTS' }, (response) => {
        if (chrome.runtime.lastError) {
            console.log('❌ Erro ao buscar shortcuts:', chrome.runtime.lastError.message);
        } else {
            console.log('📋 Resposta GET_SHORTCUTS:', response);
            if (response && response.shortcuts) {
                console.log('Total de shortcuts:', response.shortcuts.length);
                response.shortcuts.forEach((s, i) => {
                    console.log(\`Shortcut \${i+1}: \${s.trigger} - \${s.title}\`);
                });
            }
        }
    });
} else {
    console.log('❌ Não é possível testar comunicação');
}

// 4. Verificar se há campos de texto na página
console.log('\\n4. Verificando campos de texto...');
const textFields = document.querySelectorAll('input[type="text"], input[type="email"], textarea, [contenteditable="true"]');
console.log(\`Campos de texto encontrados: \${textFields.length}\`);

// 5. Verificar se o ícone está sendo criado
console.log('\\n5. Verificando ícone Quick Action...');
const icon = document.querySelector('.symplifika-icon');
if (icon) {
    console.log('✅ Ícone encontrado:', icon);
} else {
    console.log('❌ Ícone não encontrado');
}

// 6. Forçar carregamento de shortcuts
console.log('\\n6. Forçando carregamento de shortcuts...');
if (typeof loadShortcuts === 'function') {
    loadShortcuts().then(() => {
        console.log('✅ loadShortcuts executado');
        console.log('Shortcuts após reload:', state.shortcuts.length);
    }).catch(err => {
        console.log('❌ Erro no loadShortcuts:', err);
    });
} else {
    console.log('❌ Função loadShortcuts não encontrada');
}

console.log('\\n🔍 Debug concluído. Verifique os resultados acima.');
`;

console.log('INSTRUÇÕES:');
console.log('1. Abra o Chrome e vá para uma página com campos de texto');
console.log('2. Abra o DevTools (F12)');
console.log('3. Vá para a aba Console');
console.log('4. Cole e execute o código abaixo:');
console.log('');
console.log(testScript);
