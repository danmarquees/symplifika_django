# Symplifika API - Exemplos de Uso

Este documento contém exemplos práticos de como usar a API do Symplifika.

## 🔐 Autenticação

### Registro de Usuário
```bash
curl -X POST http://localhost:8000/users/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "novo_usuario",
    "email": "usuario@exemplo.com",
    "first_name": "Nome",
    "last_name": "Sobrenome",
    "password": "senha123",
    "password_confirm": "senha123"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/users/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Resposta:**
```json
{
  "token": "abc123def456...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@symplifika.com",
    "first_name": "Admin",
    "last_name": "System"
  }
}
```

### Logout
```bash
curl -X POST http://localhost:8000/users/api/auth/logout/ \
  -H "Authorization: Token abc123def456..."
```

## 👤 Gestão de Usuários

### Obter Dados do Usuário Logado
```bash
curl -X GET http://localhost:8000/users/api/users/me/ \
  -H "Authorization: Token abc123def456..."
```

### Atualizar Perfil
```bash
curl -X PUT http://localhost:8000/users/api/users/update-profile/ \
  -H "Authorization: Token abc123def456..." \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Novo Nome",
    "last_name": "Novo Sobrenome",
    "email": "novo@email.com"
  }'
```

### Alterar Senha
```bash
curl -X POST http://localhost:8000/users/api/users/change-password/ \
  -H "Authorization: Token abc123def456..." \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "senha_atual",
    "new_password": "nova_senha123",
    "new_password_confirm": "nova_senha123"
  }'
```

### Obter Estatísticas do Usuário
```bash
curl -X GET http://localhost:8000/users/api/users/stats/ \
  -H "Authorization: Token abc123def456..."
```

**Resposta:**
```json
{
  "total_shortcuts": 25,
  "active_shortcuts": 23,
  "total_uses": 150,
  "ai_requests_used": 45,
  "ai_requests_remaining": 955,
  "time_saved_minutes": 120,
  "time_saved_hours": 2.0,
  "most_used_shortcuts": [
    {
      "trigger": "//email-boas-vindas",
      "title": "Email de Boas-vindas",
      "use_count": 25
    }
  ]
}
```

## 📁 Categorias

### Listar Categorias
```bash
curl -X GET http://localhost:8000/shortcuts/api/categories/ \
  -H "Authorization: Token abc123def456..."
```

### Criar Categoria
```bash
curl -X POST http://localhost:8000/shortcuts/api/categories/ \
  -H "Authorization: Token abc123def456..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Marketing",
    "description": "Templates para marketing",
    "color": "#ff6b6b"
  }'
```

### Obter Atalhos de uma Categoria
```bash
curl -X GET http://localhost:8000/shortcuts/api/categories/1/shortcuts/ \
  -H "Authorization: Token abc123def456..."
```

## 🔤 Atalhos

### Listar Atalhos
```bash
curl -X GET http://localhost:8000/shortcuts/api/shortcuts/ \
  -H "Authorization: Token abc123def456..."
```

### Criar Atalho Simples
```bash
curl -X POST http://localhost:8000/shortcuts/api/shortcuts/ \
  -H "Authorization: Token abc123def456..." \
  -H "Content-Type: application/json" \
  -d '{
    "trigger": "//meu-atalho",
    "title": "Meu Atalho Personalizado",
    "content": "Este é o conteúdo do meu atalho.",
    "expansion_type": "static",
    "category": 1
  }'
```

### Criar Atalho com IA
```bash
curl -X POST http://localhost:8000/shortcuts/api/shortcuts/ \
  -H "Authorization: Token abc123def456..." \
  -H "Content-Type: application/json" \
  -d '{
    "trigger": "//email-vendas",
    "title": "Email de Vendas",
    "content": "Olá, gostaria de apresentar nosso produto.",
    "expansion_type": "ai_enhanced",
    "ai_prompt": "Torne este email mais persuasivo e profissional",
    "category": 2
  }'
```

### Criar Atalho Dinâmico
```bash
curl -X POST http://localhost:8000/shortcuts/api/shortcuts/ \
  -H "Authorization: Token abc123def456..." \
  -H "Content-Type: application/json" \
  -d '{
    "trigger": "//contrato",
    "title": "Template de Contrato",
    "content": "Contrato entre {empresa} e {cliente} no valor de {valor}.",
    "expansion_type": "dynamic",
    "variables": {
      "empresa": "Minha Empresa",
      "cliente": "Nome do Cliente",
      "valor": "R$ 1.000,00"
    },
    "category": 3
  }'
```

### Usar Atalho
```bash
curl -X POST http://localhost:8000/shortcuts/api/shortcuts/1/use/ \
  -H "Authorization: Token abc123def456..." \
  -H "Content-Type: application/json" \
  -d '{
    "context": "Gmail"
  }'
```

**Resposta:**
```json
{
  "content": "Conteúdo processado do atalho (expandido pela IA se necessário)",
  "use_count": 26,
  "last_used": "2024-01-15T10:30:00Z"
}
```

### Regenerar Conteúdo com IA
```bash
curl -X POST http://localhost:8000/shortcuts/api/shortcuts/1/regenerate-ai/ \
  -H "Authorization: Token abc123def456..."
```

### Buscar Atalhos
```bash
curl -X POST http://localhost:8000/shortcuts/api/shortcuts/search/ \
  -H "Authorization: Token abc123def456..." \
  -H "Content-Type: application/json" \
  -d '{
    "query": "email",
    "category": 1,
    "expansion_type": "ai_enhanced",
    "is_active": true,
    "order_by": "-use_count"
  }'
```

### Atalhos Mais Usados
```bash
curl -X GET "http://localhost:8000/shortcuts/api/shortcuts/most-used/?days=30" \
  -H "Authorization: Token abc123def456..."
```

### Estatísticas de Atalhos
```bash
curl -X GET http://localhost:8000/shortcuts/api/shortcuts/stats/ \
  -H "Authorization: Token abc123def456..."
```

### Ações em Lote
```bash
# Ativar múltiplos atalhos
curl -X POST http://localhost:8000/shortcuts/api/shortcuts/bulk-action/ \
  -H "Authorization: Token abc123def456..." \
  -H "Content-Type: application/json" \
  -d '{
    "shortcut_ids": [1, 2, 3],
    "action": "activate"
  }'

# Mover para categoria
curl -X POST http://localhost:8000/shortcuts/api/shortcuts/bulk-action/ \
  -H "Authorization: Token abc123def456..." \
  -H "Content-Type: application/json" \
  -d '{
    "shortcut_ids": [1, 2, 3],
    "action": "change_category",
    "category_id": 2
  }'

# Deletar múltiplos atalhos
curl -X POST http://localhost:8000/shortcuts/api/shortcuts/bulk-action/ \
  -H "Authorization: Token abc123def456..." \
  -H "Content-Type: application/json" \
  -d '{
    "shortcut_ids": [1, 2, 3],
    "action": "delete"
  }'
```

### Histórico de Uso
```bash
curl -X GET http://localhost:8000/shortcuts/api/shortcuts/1/usage-history/ \
  -H "Authorization: Token abc123def456..."
```

## 📊 Relatórios e Logs

### Histórico de Uso Geral
```bash
curl -X GET http://localhost:8000/shortcuts/api/usage/ \
  -H "Authorization: Token abc123def456..."
```

### Logs de IA
```bash
curl -X GET http://localhost:8000/shortcuts/api/ai-logs/ \
  -H "Authorization: Token abc123def456..."
```

## 🔧 APIs do Sistema

### Status da API
```bash
curl -X GET http://localhost:8000/api/
```

**Resposta:**
```json
{
  "message": "Symplifika API",
  "version": "1.0",
  "endpoints": {
    "auth": "/users/auth/",
    "shortcuts": "/shortcuts/api/",
    "users": "/users/api/",
    "admin": "/admin/"
  }
}
```

### Health Check
```bash
curl -X GET http://localhost:8000/api/health/
```

**Resposta:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🐍 Exemplos em Python

### Cliente Python Básico
```python
import requests
import json

class SymplifikalClient:
    def __init__(self, base_url="http://localhost:8000", token=None):
        self.base_url = base_url
        self.token = token
        self.headers = {
            'Content-Type': 'application/json'
        }
        if token:
            self.headers['Authorization'] = f'Token {token}'
    
    def login(self, username, password):
        """Fazer login e obter token"""
        response = requests.post(
            f"{self.base_url}/users/api/auth/login/",
            json={'username': username, 'password': password}
        )
        if response.status_code == 200:
            data = response.json()
            self.token = data['token']
            self.headers['Authorization'] = f'Token {self.token}'
            return data
        return None
    
    def create_shortcut(self, trigger, title, content, expansion_type='static'):
        """Criar um novo atalho"""
        return requests.post(
            f"{self.base_url}/shortcuts/api/shortcuts/",
            headers=self.headers,
            json={
                'trigger': trigger,
                'title': title,
                'content': content,
                'expansion_type': expansion_type
            }
        ).json()
    
    def use_shortcut(self, shortcut_id, context=""):
        """Usar um atalho"""
        return requests.post(
            f"{self.base_url}/shortcuts/api/shortcuts/{shortcut_id}/use/",
            headers=self.headers,
            json={'context': context}
        ).json()
    
    def search_shortcuts(self, query):
        """Buscar atalhos"""
        return requests.post(
            f"{self.base_url}/shortcuts/api/shortcuts/search/",
            headers=self.headers,
            json={'query': query}
        ).json()

# Exemplo de uso
client = SymplifikalClient()

# Login
login_data = client.login('admin', 'admin123')
print(f"Login realizado: {login_data['user']['username']}")

# Criar atalho
shortcut = client.create_shortcut(
    trigger='//python-example',
    title='Exemplo Python',
    content='Este atalho foi criado via API Python!'
)
print(f"Atalho criado: {shortcut['trigger']}")

# Usar atalho
usage = client.use_shortcut(shortcut['id'], context='Python Script')
print(f"Conteúdo: {usage['content']}")

# Buscar atalhos
results = client.search_shortcuts('python')
print(f"Encontrados {len(results)} atalhos")
```

### Exemplo com Async/Await
```python
import aiohttp
import asyncio

async def async_symplifika_example():
    async with aiohttp.ClientSession() as session:
        # Login
        async with session.post(
            'http://localhost:8000/users/api/auth/login/',
            json={'username': 'admin', 'password': 'admin123'}
        ) as response:
            login_data = await response.json()
            token = login_data['token']
        
        headers = {'Authorization': f'Token {token}'}
        
        # Buscar atalhos
        async with session.get(
            'http://localhost:8000/shortcuts/api/shortcuts/',
            headers=headers
        ) as response:
            shortcuts = await response.json()
            print(f"Total de atalhos: {shortcuts['count']}")

# Executar
asyncio.run(async_symplifika_example())
```

## 📱 Exemplo JavaScript/Frontend

```javascript
class SymplifikalAPI {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
        this.token = localStorage.getItem('symplifika_token');
    }
    
    async login(username, password) {
        const response = await fetch(`${this.baseURL}/users/api/auth/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        if (response.ok) {
            const data = await response.json();
            this.token = data.token;
            localStorage.setItem('symplifika_token', this.token);
            return data;
        }
        throw new Error('Login failed');
    }
    
    async getShortcuts() {
        const response = await fetch(`${this.baseURL}/shortcuts/api/shortcuts/`, {
            headers: { 'Authorization': `Token ${this.token}` }
        });
        return response.json();
    }
    
    async useShortcut(shortcutId, context = '') {
        const response = await fetch(
            `${this.baseURL}/shortcuts/api/shortcuts/${shortcutId}/use/`,
            {
                method: 'POST',
                headers: {
                    'Authorization': `Token ${this.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ context })
            }
        );
        return response.json();
    }
}

// Uso
const api = new SymplifikalAPI();

// Login
api.login('admin', 'admin123').then(user => {
    console.log('Logged in:', user.user.username);
    
    // Buscar atalhos
    return api.getShortcuts();
}).then(shortcuts => {
    console.log('Shortcuts:', shortcuts.results);
});
```

## 🚨 Códigos de Erro Comuns

### 400 - Bad Request
```json
{
  "error": "Dados inválidos",
  "details": {
    "trigger": ["Este gatilho já existe"]
  }
}
```

### 401 - Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 - Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 - Not Found
```json
{
  "detail": "Not found."
}
```

### 429 - Rate Limited
```json
{
  "error": "Limite de uso de IA atingido",
  "detail": "Você atingiu o limite de requisições de IA para este mês."
}
```

## 📝 Notas Importantes

1. **Autenticação**: Todas as APIs (exceto login/registro) requerem token de autenticação
2. **Rate Limiting**: APIs de IA têm limite baseado no plano do usuário
3. **Paginação**: Listas são paginadas com 20 itens por página
4. **Filtros**: A maioria das listagens suporta filtros via query parameters
5. **CORS**: Configurado para permitir requests de localhost:3000

## 🔗 Links Úteis

- **Admin Interface**: http://localhost:8000/admin/
- **API Browser**: http://localhost:8000/shortcuts/api/
- **Health Check**: http://localhost:8000/api/health/
- **API Root**: http://localhost:8000/api/

Para mais exemplos, consulte a documentação do Django REST Framework e explore a API através do navegador web.