# 🔍 DEBUG - Quick Action Icon Não Mostra Atalhos

## Problema
O Quick Action Icon não está mostrando os atalhos criados na conta do usuário.

## Passos para Debug

### 1. Verificar se a Extensão Está Carregada
1. Abra o Chrome
2. Vá para `chrome://extensions/`
3. Verifique se a extensão "Symplifika" está ativa
4. Se não estiver, clique em "Carregar sem compactação" e selecione a pasta `dist/`

### 2. Verificar Logs da Extensão
1. Na página `chrome://extensions/`
2. Clique em "Inspecionar visualizações" → "service worker" (para o background script)
3. Vá para a aba Console
4. Procure por logs como:
   - `🎯 Background script carregado - Symplifika v2.0.0`
   - `📦 Estado restaurado: {authenticated: true/false}`
   - `✅ X atalhos sincronizados`

### 3. Testar em uma Página Web
1. Vá para qualquer site (ex: gmail.com, google.com)
2. Clique em um campo de texto
3. Abra o DevTools (F12) → Console
4. Procure por logs:
   - `✅ Quick Action System v2.0 carregado - Symplifika`
   - `🔄 Iniciando carregamento de atalhos...`
   - `✅ X atalhos carregados no state`

### 4. Verificar Comunicação Background ↔ Content
No console da página (F12), execute:
```javascript
// Testar comunicação
chrome.runtime.sendMessage({type: 'PING'}, (response) => {
    console.log('PING Response:', response);
});

// Testar busca de atalhos
chrome.runtime.sendMessage({type: 'GET_SHORTCUTS'}, (response) => {
    console.log('GET_SHORTCUTS Response:', response);
});
```

### 5. Verificar Estado da Extensão
No console da página, execute:
```javascript
// Verificar estado do Quick Action
if (typeof state !== 'undefined') {
    console.log('State:', state);
    console.log('Shortcuts:', state.shortcuts);
} else {
    console.log('State não encontrado');
}
```

### 6. Forçar Carregamento
1. Clique em um campo de texto para aparecer o ícone ✨
2. Clique no ícone para abrir o dropdown
3. Clique no botão "🔄 Recarregar Atalhos"
4. Verifique os logs no console

### 7. Verificar Autenticação
1. Faça login no dashboard Django (127.0.0.1:8000)
2. Abra a extensão (clique no ícone na barra do Chrome)
3. Verifique se está logado
4. Se não estiver, faça login na extensão

### 8. Verificar se Há Atalhos na Conta
1. Acesse o dashboard: http://127.0.0.1:8000
2. Vá para a seção de atalhos
3. Verifique se há atalhos criados
4. Verifique se os atalhos estão marcados como "ativos"

## Possíveis Causas

### ❌ Extensão não está autenticada
**Solução**: Fazer login na extensão

### ❌ Token JWT expirado
**Solução**: Fazer logout e login novamente na extensão

### ❌ Atalhos não estão marcados como ativos
**Solução**: No dashboard, editar os atalhos e marcar como ativos

### ❌ Erro de comunicação entre scripts
**Solução**: Recarregar a extensão em chrome://extensions/

### ❌ Servidor Django não está rodando
**Solução**: Iniciar o servidor: `python manage.py runserver 127.0.0.1:8000`

### ❌ CORS ou problemas de API
**Solução**: Verificar logs do servidor Django

## Logs Esperados (Funcionamento Normal)

### Background Script:
```
🎯 Background script carregado - Symplifika v2.0.0
📦 Estado restaurado: {authenticated: true, user: "username", shortcuts: 5}
🔄 Sincronização na inicialização do background
✅ 5 atalhos sincronizados
```

### Content Script:
```
✅ Quick Action System v2.0 carregado - Symplifika
🔄 Iniciando carregamento de atalhos...
📡 Enviando mensagem GET_SHORTCUTS para background...
📄 Resposta recebida: {success: true, shortcuts: [...]}
📋 Processando 5 atalhos recebidos
✅ 5 atalhos carregados no state
```

## Se Nada Funcionar
1. Recarregue a extensão em chrome://extensions/
2. Recarregue a página web
3. Verifique se o servidor Django está rodando
4. Faça logout e login novamente na extensão
5. Verifique se há atalhos ativos no dashboard
