# 🔧 Guia de Correções - Extensão Chrome Symplifika

## ✅ Problemas Resolvidos

### 1. **Popup "Symplifika foi atualizada" Removido** ✅

**Problema**: Popup intrusivo aparecia sempre que a extensão era recarregada.

**Solução**: 
- Arquivo: `src/content/content.js`
- Função `showExtensionReloadNotification()` modificada para apenas fazer log no console
- Removido HTML do popup que interrompia a experiência do usuário

```javascript
// ANTES: Popup intrusivo
function showExtensionReloadNotification() {
  // Código que criava popup HTML...
}

// DEPOIS: Apenas log
function showExtensionReloadNotification() {
  console.log("🔄 Extensão Symplifika foi recarregada. Funcionalidades podem estar temporariamente indisponíveis.");
}
```

### 2. **Função de Expansão de Texto Corrigida** ✅

**Problema**: Chamada incorreta para função `expandText` no background script.

**Solução**:
- Arquivo: `src/background/background.js`
- Corrigida chamada de `expandText()` para `handleTextExpansion()`

```javascript
// ANTES
case 'EXPAND_TEXT':
  response = await expandText(request.payload.trigger)
  break

// DEPOIS  
case 'EXPAND_TEXT':
  response = await handleTextExpansion(request.payload)
  break
```

### 3. **Função `markShortcutAsUsed` Implementada** ✅

**Problema**: Função estava sendo chamada mas não existia.

**Solução**:
- Arquivo: `src/background/background.js`
- Implementada função completa para marcar atalhos como usados

```javascript
async function markShortcutAsUsed(shortcutId) {
  if (!extensionState.isAuthenticated || !extensionState.token) {
    return { success: false, error: 'Não autenticado' }
  }
  
  try {
    const response = await fetch(`${API_BASE_URL}/shortcuts/api/shortcuts/${shortcutId}/use/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${extensionState.token}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (response.ok) {
      console.log(`✅ Atalho ${shortcutId} marcado como usado`)
      return { success: true }
    } else {
      console.error('❌ Erro ao marcar atalho como usado:', response.status)
      return { success: false, error: 'Erro na API' }
    }
  } catch (error) {
    console.error('❌ Erro de conexão ao marcar uso:', error)
    return { success: false, error: 'Erro de conexão' }
  }
}
```

### 4. **Inicialização do Background Script Melhorada** ✅

**Problema**: Estado não era restaurado imediatamente ao carregar a extensão.

**Solução**:
- Arquivo: `src/background/background.js`
- Adicionada inicialização imediata com IIFE (Immediately Invoked Function Expression)

```javascript
// Inicialização imediata do background script
(async () => {
  await restoreState()
  
  if (extensionState.isAuthenticated) {
    console.log('🔄 Sincronização na inicialização do background')
    await syncShortcuts()
  }
})()
```

### 5. **Logs de Debug Melhorados** ✅

**Problema**: Difícil diagnosticar problemas de login e conexão.

**Solução**:
- Arquivo: `src/background/background.js`
- Adicionados logs detalhados na função `handleLogin()`

```javascript
async function handleLogin(credentials) {
  try {
    console.log('🔐 Tentando login para:', credentials.login)
    console.log('🌐 URL da API:', `${API_BASE_URL}/api/token/`)
    
    const response = await fetch(`${API_BASE_URL}/api/token/`, {
      // ... código de requisição
    })
    
    console.log('📡 Status da resposta:', response.status, response.statusText)
    
    let data
    try {
      data = await response.json()
      console.log('📄 Dados da resposta:', data)
    } catch (jsonError) {
      console.error('❌ Erro ao parsear JSON:', jsonError)
      const textData = await response.text()
      console.log('📄 Resposta como texto:', textData)
      return {
        success: false,
        error: `Erro no servidor (${response.status}): ${textData.substring(0, 100)}`
      }
    }
    
    // ... resto da função
  } catch (error) {
    console.error('❌ Erro de conexão no login:', error)
    return {
      success: false,
      error: `Erro de conexão: ${error.message}. Verifique se o servidor Django está rodando em ${API_BASE_URL}`
    }
  }
}
```

## 🧪 Como Testar a Extensão

### Pré-requisitos
1. **Servidor Django rodando** em `http://127.0.0.1:8000`
2. **Usuário de teste criado** (username: test, password: test123)
3. **Extensão compilada** na pasta `dist/`

### Passos para Teste

1. **Compilar a extensão**:
   ```bash
   cd chrome_extension
   npm run build
   ```

2. **Carregar no Chrome**:
   - Abrir `chrome://extensions/`
   - Ativar "Modo do desenvolvedor"
   - Clicar "Carregar sem compactação"
   - Selecionar pasta `chrome_extension/dist/`

3. **Testar Login**:
   - Clicar no ícone da extensão
   - Usar credenciais: `test` / `test123`
   - Verificar se login é bem-sucedido

4. **Testar Funcionalidades**:
   - Abrir qualquer site com campo de texto
   - Digitar `!oi` + espaço para testar expansão
   - Verificar se atalhos são carregados no popup

### Debug no Console

Para diagnosticar problemas:

1. **Background Script**:
   - Ir em `chrome://extensions/`
   - Clicar "service worker" na extensão
   - Verificar logs no console

2. **Content Script**:
   - Abrir DevTools na página (F12)
   - Verificar logs no console
   - Procurar por mensagens do Symplifika

3. **Popup**:
   - Clicar com botão direito no ícone da extensão
   - Selecionar "Inspecionar popup"
   - Verificar logs no console

## 🔍 Problemas Conhecidos e Soluções

### Problema: "Extension context invalidated"
**Causa**: Extensão foi recarregada durante o uso
**Solução**: Recarregar a página onde estava sendo usada

### Problema: Login falha com "Erro de conexão"
**Causa**: Servidor Django não está rodando
**Solução**: 
```bash
cd symplifika_django
source venv/bin/activate
python manage.py runserver 127.0.0.1:8000
```

### Problema: "Atalho não encontrado"
**Causa**: Usuário não tem atalhos criados
**Solução**: Criar atalhos no dashboard Django ou usar script de teste

### Problema: CORS errors
**Causa**: Configuração CORS no Django
**Solução**: Verificar se `CORS_ALLOWED_ORIGINS` inclui `chrome-extension://*`

## 📁 Arquivos Modificados

- ✅ `src/background/background.js` - Correções principais
- ✅ `src/content/content.js` - Remoção do popup
- ✅ `src/popup/App.vue` - Mantido funcional
- ✅ `manifest.json` - Configuração correta

## 🎯 Status Final

- ✅ **Popup intrusivo removido**
- ✅ **Funções de background corrigidas**
- ✅ **Logs de debug implementados**
- ✅ **Inicialização melhorada**
- ✅ **Tratamento de erros robusto**

A extensão agora deve funcionar corretamente com o servidor Django rodando e um usuário de teste criado.

## 📞 Próximos Passos

1. **Testar em ambiente real** com usuários reais
2. **Implementar TrustedHTML policy** para compatibilidade futura
3. **Adicionar mais validações** de entrada
4. **Melhorar UX** do popup e notificações
5. **Implementar reconexão automática** em caso de falha
