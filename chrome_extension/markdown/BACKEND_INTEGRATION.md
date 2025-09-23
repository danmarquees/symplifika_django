# Backend Integration - Chrome Extension

Este documento descreve a integração da extensão Chrome do Symplifika com os endpoints do backend Django.

## Endpoints Implementados

### Autenticação

#### Login
- **Endpoint**: `POST /users/api/auth/login/`
- **Payload**: 
  ```json
  {
    "username": "usuario@email.com",
    "password": "senha123"
  }
  ```
- **Resposta**:
  ```json
  {
    "token": "auth_token_aqui",
    "user": {
      "id": 1,
      "username": "usuario",
      "email": "usuario@email.com"
    }
  }
  ```

#### Logout
- **Endpoint**: `POST /users/api/auth/logout/`
- **Headers**: `Authorization: Token {token}`
- **Resposta**: Status 200

### Usuários

#### Perfil do Usuário
- **Endpoint**: `GET /users/api/users/me/`
- **Headers**: `Authorization: Token {token}`
- **Resposta**:
  ```json
  {
    "id": 1,
    "username": "usuario",
    "email": "usuario@email.com",
    "profile": {
      "plan_type": "free",
      "avatar": null
    }
  }
  ```

#### Estatísticas do Usuário
- **Endpoint**: `GET /users/api/users/stats/`
- **Headers**: `Authorization: Token {token}`
- **Resposta**:
  ```json
  {
    "total_shortcuts": 15,
    "total_usage": 342,
    "today_usage": 8,
    "most_used_shortcut": "//email"
  }
  ```

### Atalhos

#### Listar Atalhos
- **Endpoint**: `GET /api/shortcuts/`
- **Headers**: `Authorization: Token {token}`
- **Resposta**:
  ```json
  {
    "count": 15,
    "results": [
      {
        "id": 1,
        "title": "Email Pessoal",
        "trigger": "//email",
        "content": "usuario@email.com",
        "category": {
          "id": 1,
          "name": "Contato",
          "color": "#3b82f6"
        },
        "is_active": true,
        "is_ai_enhanced": false,
        "usage_count": 42,
        "last_used_at": "2024-01-15T14:30:00Z"
      }
    ]
  }
  ```

#### Usar Atalho
- **Endpoint**: `POST /api/shortcuts/{id}/use/`
- **Headers**: `Authorization: Token {token}`
- **Payload**:
  ```json
  {
    "variables": {}
  }
  ```
- **Resposta**:
  ```json
  {
    "expanded_content": "usuario@email.com",
    "usage_count": 43
  }
  ```

#### Buscar Atalhos
- **Endpoint**: `POST /api/shortcuts/search/`
- **Headers**: `Authorization: Token {token}`
- **Payload**:
  ```json
  {
    "query": "email"
  }
  ```
- **Resposta**:
  ```json
  {
    "results": [
      {
        "id": 1,
        "title": "Email Pessoal",
        "trigger": "//email",
        "content": "usuario@email.com"
      }
    ]
  }
  ```

#### Atalhos Mais Usados
- **Endpoint**: `GET /api/shortcuts/most-used/`
- **Headers**: `Authorization: Token {token}`
- **Resposta**:
  ```json
  {
    "results": [
      {
        "id": 1,
        "title": "Email Pessoal",
        "trigger": "//email",
        "usage_count": 42
      }
    ]
  }
  ```

#### Estatísticas dos Atalhos
- **Endpoint**: `GET /api/shortcuts/stats/`
- **Headers**: `Authorization: Token {token}`
- **Resposta**:
  ```json
  {
    "total_shortcuts": 15,
    "active_shortcuts": 12,
    "ai_enhanced": 3,
    "total_usage_today": 8
  }
  ```

### Categorias

#### Listar Categorias
- **Endpoint**: `GET /api/categories/`
- **Headers**: `Authorization: Token {token}`
- **Resposta**:
  ```json
  {
    "results": [
      {
        "id": 1,
        "name": "Contato",
        "color": "#3b82f6",
        "shortcut_count": 5
      }
    ]
  }
  ```

## Estrutura dos Arquivos

### background.js
- **SymphilikaAPI**: Classe principal para comunicação com a API
- **Métodos principais**:
  - `login(username, password)`: Autenticar usuário
  - `logout()`: Fazer logout
  - `syncShortcuts()`: Sincronizar atalhos
  - `useShortcut(id, variables)`: Usar um atalho
  - `searchShortcuts(query)`: Buscar atalhos
  - `getUserStats()`: Obter estatísticas do usuário
  - `getMostUsedShortcuts()`: Obter atalhos mais usados

### popup.js
- **SymphilikaPopup**: Classe para interface do popup
- **Funcionalidades**:
  - Login/logout de usuário
  - Exibição de atalhos
  - Busca e filtros
  - Estatísticas do usuário
  - Sincronização manual

### content.js
- **SymphilikaContentScript**: Detecção e expansão de atalhos
- **Funcionalidades**:
  - Detecção de padrões de trigger (ex: `//email`)
  - Expansão automática de atalhos
  - Comunicação com background script

### options.js
- **SymphilikaOptions**: Página de configurações
- **Funcionalidades**:
  - Configuração da URL do servidor
  - Teste de conexão
  - Configurações de comportamento
  - Importar/exportar configurações

## Configuração

### Variáveis de Ambiente
- **Base URL**: `http://localhost:8000` (padrão para desenvolvimento)
- **Endpoints**: Configurados automaticamente baseados na URL base

### Armazenamento
A extensão utiliza `chrome.storage.sync` para:
- Token de autenticação
- URL do servidor
- Configurações do usuário
- Cache de atalhos

### Permissões
```json
{
  "permissions": ["storage", "activeTab", "scripting"],
  "host_permissions": [
    "http://localhost:8000/*",
    "https://*.symplifika.com/*"
  ]
}
```

## Autenticação

### Token-based Authentication
- Todos os endpoints protegidos requerem header `Authorization: Token {token}`
- Token é obtido através do endpoint de login
- Token é armazenado localmente e enviado em todas as requisições

### Tratamento de Erros
- **401 Unauthorized**: Token inválido ou expirado - redirecionar para login
- **403 Forbidden**: Usuário sem permissão
- **404 Not Found**: Recurso não encontrado
- **500 Server Error**: Erro interno do servidor

## Sincronização

### Automática
- Sincronização a cada 30 minutos (configurável)
- Sincronização ao fazer login
- Sincronização ao iniciar a extensão

### Manual
- Botão de sincronização no popup
- Sincronização através das configurações

## Estados da Interface

### Loading State
- Exibido durante carregamento inicial
- Spinner com mensagem de status

### Auth State
- Exibido quando usuário não está autenticado
- Botão para abrir modal de login

### Main Content
- Exibido quando usuário está autenticado
- Lista de atalhos, busca, filtros, estatísticas

### Error State
- Exibido em caso de erro de conexão
- Botão para tentar novamente

## Notificações

### Tipos
- **Success**: Operações bem-sucedidas (verde)
- **Error**: Erros e falhas (vermelho)
- **Warning**: Avisos (amarelo)
- **Info**: Informações gerais (azul)

### Comportamento
- Auto-dismiss após 3-5 segundos
- Animação de entrada/saída
- Limite de notificações simultâneas

## Desenvolvimento

### Debugging
- Modo debug disponível nas configurações
- Logs detalhados no console
- Informações de performance

### Testes
- Teste de conexão com servidor
- Validação de endpoints
- Teste de funcionalidades offline

## Futuras Melhorias

- [ ] Suporte a múltiplos servidores
- [ ] Cache offline inteligente
- [ ] Sincronização em tempo real via WebSockets
- [ ] Métricas avançadas de uso
- [ ] Integração com outros navegadores