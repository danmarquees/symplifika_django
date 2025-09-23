# Symplifika Chrome Extension - Guia de Configuração

## Visão Geral

A extensão Symplifika permite expandir atalhos de texto automaticamente em qualquer site, conectando-se à API RESTful do backend Django. A extensão detecta gatilhos (como `//boasvindas`) e os expande para textos completos, com suporte a expansão estática, dinâmica e melhorada por IA.

## Arquitetura

### Componentes Principais

1. **manifest.json** - Configuração da extensão (Manifest V3)
2. **background.js** - Service Worker para comunicação com API
3. **popup.html/js/css** - Interface de login e gerenciamento
4. **content.js** - Script para detecção e expansão de atalhos
5. **options.html/js/css** - Página de configurações avançadas

### Fluxo de Funcionamento

1. **Autenticação**: Login via popup → Token armazenado → Sincronização de atalhos
2. **Detecção**: Content script monitora campos de texto → Detecta padrão `//palavra`
3. **Expansão**: Busca atalho → Chama API → Substitui texto no campo

## API Endpoints Utilizados

### Base URL
- **Desenvolvimento**: `http://localhost:8000`
- **Produção**: Configurável via extensão

### Endpoints Essenciais

#### Autenticação
```
POST /users/auth/login/
Body: { "username": "user", "password": "password" }
Response: { "token": "your_auth_token_here" }
```

#### Atalhos
```
GET /shortcuts/api/shortcuts/
Headers: Authorization: Bearer <token>
Response: Array de objetos de atalho

POST /shortcuts/api/shortcuts/{id}/use/
Headers: Authorization: Bearer <token>
Body: { "variables": { "nome": "Cliente" } } (opcional)
Response: { "expanded_content": "Texto expandido" }
```

## Instalação e Configuração

### 1. Preparar a Extensão

1. Navegue até o diretório da extensão:
```bash
cd /home/danmarques/Documentos/Workplace/symplifika_django/chrome_extension/
```

2. Verifique se todos os arquivos estão presentes:
- manifest.json
- background.js
- popup.html, popup.js, popup.css
- content.js, content.css
- options.html, options.js, options.css
- icons/ (diretório com ícones)

### 2. Carregar no Chrome

1. Abra o Chrome e vá para `chrome://extensions/`
2. Ative o "Modo do desenvolvedor" (canto superior direito)
3. Clique em "Carregar sem compactação"
4. Selecione o diretório `chrome_extension`
5. A extensão aparecerá na lista e na barra de ferramentas

### 3. Configuração Inicial

1. Clique no ícone da extensão na barra de ferramentas
2. Faça login com suas credenciais do Symplifika
3. A extensão sincronizará automaticamente seus atalhos
4. Teste digitando `//` seguido de uma palavra-chave em qualquer campo de texto

## Uso da Extensão

### Expandir Atalhos

1. **Detecção Automática**: Digite `//palavra` em qualquer campo de texto
2. **Pressione Enter ou Tab** para expandir o atalho
3. **Expansão Instantânea**: O texto será substituído automaticamente

### Tipos de Expansão

- **Estática**: Texto fixo substituído diretamente
- **Dinâmica**: Solicita variáveis antes da expansão
- **IA**: Processada pelo backend com inteligência artificial

### Interface do Popup

- **Login/Logout**: Gerenciamento de autenticação
- **Lista de Atalhos**: Visualização e busca de atalhos
- **Estatísticas**: Uso e performance
- **Sincronização**: Atualização manual dos atalhos

## Funcionalidades Avançadas

### Busca Rápida
- **Ctrl/Cmd + J**: Abre busca rápida (em desenvolvimento)

### Menu de Contexto
- Clique direito em texto selecionado → "Expandir com Symplifika"

### Configurações
- Acesse via botão de configurações no popup
- Configure URL do servidor, intervalos de sincronização, etc.

## Desenvolvimento e Debug

### Modo Debug
1. Vá para `chrome://extensions/`
2. Clique em "Detalhes" na extensão Symplifika
3. Ative "Coletar erros"
4. Use o console do desenvolvedor para debug

### Logs
- **Background Script**: Console da extensão
- **Content Script**: Console da página web
- **Popup**: Console do popup (F12 no popup)

### Estrutura de Arquivos
```
chrome_extension/
├── manifest.json          # Configuração da extensão
├── background.js          # Service Worker (API communication)
├── popup.html            # Interface do popup
├── popup.js              # Lógica do popup
├── popup.css             # Estilos do popup
├── content.js            # Script de conteúdo (detecção)
├── content.css           # Estilos do content script
├── options.html          # Página de configurações
├── options.js            # Lógica das configurações
├── options.css           # Estilos das configurações
└── icons/                # Ícones da extensão
    ├── icon16.png
    ├── icon32.png
    └── icon48.png
```

## Solução de Problemas

### Problemas Comuns

1. **Extensão não carrega**
   - Verifique se o manifest.json está válido
   - Confirme que todos os arquivos estão presentes

2. **Login falha**
   - Verifique se o servidor Django está rodando
   - Confirme a URL do servidor nas configurações
   - Verifique credenciais

3. **Atalhos não expandem**
   - Confirme que está logado
   - Verifique se os atalhos foram sincronizados
   - Teste o padrão `//palavra` em campos de texto

4. **Problemas de conectividade**
   - Verifique CORS no backend Django
   - Confirme permissões no manifest.json

### Debug Avançado

1. **Inspecionar Background Script**:
   - `chrome://extensions/` → Detalhes → "Visualizações de inspeção" → background.html

2. **Inspecionar Content Script**:
   - F12 na página web → Console → Procure por logs "Symplifika"

3. **Verificar Storage**:
   - F12 → Application → Storage → Extension Storage

## Atualizações e Manutenção

### Atualizar a Extensão
1. Modifique os arquivos necessários
2. Vá para `chrome://extensions/`
3. Clique no botão "Recarregar" na extensão

### Versionamento
- Atualize o campo `version` no manifest.json
- Documente mudanças no histórico de versões

## Segurança

### Boas Práticas
- Tokens são armazenados localmente de forma segura
- Comunicação HTTPS em produção
- Validação de entrada nos content scripts
- Sanitização de HTML para prevenir XSS

### Permissões
A extensão solicita apenas as permissões necessárias:
- `storage`: Armazenar configurações e cache
- `activeTab`: Acessar a aba ativa para expansão
- `scripting`: Injetar scripts de conteúdo
- `host_permissions`: Comunicar com o servidor Symplifika

## Suporte

Para problemas ou dúvidas:
1. Verifique os logs de erro no console
2. Consulte a documentação da API
3. Teste com o servidor de desenvolvimento local
4. Reporte bugs com logs detalhados
