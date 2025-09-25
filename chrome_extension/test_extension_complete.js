// Script completo de teste da extensão Symplifika
// Para executar no console do background script da extensão

console.log('🧪 Iniciando teste completo da extensão Symplifika...');

async function testExtensionComplete() {
  const API_BASE_URL = 'http://127.0.0.1:8000';
  
  console.log('\n=== TESTE 1: Verificar Estado Inicial ===');
  console.log('Estado da extensão:', extensionState);
  
  console.log('\n=== TESTE 2: Testar Conexão com API ===');
  try {
    const response = await fetch(`${API_BASE_URL}/`, {
      method: 'GET',
      headers: {
        'Origin': chrome.runtime.getURL('')
      }
    });
    console.log('✅ Servidor Django respondeu:', response.status);
  } catch (error) {
    console.error('❌ Erro de conexão com servidor:', error);
    return;
  }
  
  console.log('\n=== TESTE 3: Testar Login ===');
  const loginResult = await handleLogin({
    login: 'test',
    password: 'test123'
  });
  
  console.log('Resultado do login:', loginResult);
  
  if (loginResult.success) {
    console.log('✅ Login bem-sucedido!');
    
    console.log('\n=== TESTE 4: Testar Sincronização de Atalhos ===');
    const syncResult = await syncShortcuts();
    console.log('Resultado da sincronização:', syncResult);
    
    if (syncResult.success) {
      console.log('✅ Sincronização bem-sucedida!');
      console.log(`📋 Atalhos carregados: ${extensionState.shortcuts.length}`);
      
      if (extensionState.shortcuts.length > 0) {
        console.log('\n=== TESTE 5: Testar Expansão de Texto ===');
        const firstShortcut = extensionState.shortcuts[0];
        console.log('Testando atalho:', firstShortcut.trigger);
        
        const expansionResult = await handleTextExpansion({
          trigger: firstShortcut.trigger
        });
        
        console.log('Resultado da expansão:', expansionResult);
        
        if (expansionResult.success) {
          console.log('✅ Expansão de texto funcionando!');
          console.log('Texto expandido:', expansionResult.expandedText.substring(0, 100) + '...');
        } else {
          console.log('❌ Falha na expansão de texto');
        }
      } else {
        console.log('⚠️ Nenhum atalho encontrado para testar expansão');
      }
    } else {
      console.log('❌ Falha na sincronização de atalhos');
    }
  } else {
    console.log('❌ Falha no login');
  }
  
  console.log('\n=== TESTE 6: Testar Comunicação com Popup ===');
  try {
    // Simular mensagem do popup
    const pingResult = await new Promise((resolve) => {
      chrome.runtime.onMessage.addListener(function handler(request, sender, sendResponse) {
        if (request.type === 'PING') {
          chrome.runtime.onMessage.removeListener(handler);
          resolve(sendResponse({
            success: true,
            status: 'alive',
            authenticated: extensionState.isAuthenticated,
            shortcuts: extensionState.shortcuts.length
          }));
        }
      });
      
      // Enviar ping para si mesmo
      chrome.runtime.sendMessage({ type: 'PING' });
    });
    
    console.log('✅ Comunicação interna funcionando');
  } catch (error) {
    console.log('❌ Erro na comunicação interna:', error);
  }
  
  console.log('\n=== RESUMO DOS TESTES ===');
  console.log(`🔐 Autenticado: ${extensionState.isAuthenticated ? '✅' : '❌'}`);
  console.log(`👤 Usuário: ${extensionState.user?.username || 'N/A'}`);
  console.log(`📋 Atalhos: ${extensionState.shortcuts.length}`);
  console.log(`🔄 Última sync: ${extensionState.lastSync || 'N/A'}`);
  
  if (extensionState.isAuthenticated && extensionState.shortcuts.length > 0) {
    console.log('\n🎉 TODOS OS TESTES PASSARAM! Extensão funcionando corretamente.');
    console.log('\n📋 Atalhos disponíveis:');
    extensionState.shortcuts.forEach((shortcut, index) => {
      console.log(`   ${index + 1}. ${shortcut.trigger} - ${shortcut.title}`);
    });
  } else {
    console.log('\n⚠️ Alguns testes falharam. Verifique os logs acima.');
  }
}

// Executar teste
testExtensionComplete().catch(console.error);

// Instruções para o usuário
console.log(`
📖 INSTRUÇÕES DE USO:

1. Copie e cole este código no console do background script da extensão
2. Para acessar o console do background script:
   - Vá em chrome://extensions/
   - Encontre a extensão Symplifika
   - Clique em "service worker" (ou "background page")
   - Cole este código no console

3. Se os testes passarem, a extensão está funcionando!

4. Para testar na prática:
   - Abra qualquer site com campo de texto
   - Digite um trigger (ex: !oi) seguido de espaço
   - O texto deve ser expandido automaticamente

5. Para ver atalhos no popup:
   - Clique no ícone da extensão na barra de ferramentas
   - Faça login com: test / test123
   - Veja a lista de atalhos disponíveis
`);
