# Documentação de Exemplos de Uso da API Symplifika

Esta documentação apresenta exemplos práticos de requisições à API RESTful do Symplifika, incluindo autenticação, gerenciamento de atalhos e integração com a extensão Chrome.

---

## 1. Autenticação JWT

### Obter token de acesso

```bash
curl -X POST https://seusite.com/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "usuario", "password": "senha"}'
```

**Resposta:**
```json
{
  "access": "TOKEN_JWT_AQUI",
  "refresh": "TOKEN_REFRESH_AQUI"
}
```

### Renovar token de acesso

```bash
curl -X POST https://seusite.com/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "TOKEN_REFRESH_AQUI"}'
```

---

## 2. Atalhos

### Listar atalhos do usuário

```bash
curl -X GET https://seusite.com/shortcuts/api/shortcuts/ \
  -H "Authorization: Bearer TOKEN_JWT_AQUI"
```

### Criar um novo atalho

```bash
curl -X POST https://seusite.com/shortcuts/api/shortcuts/ \
  -H "Authorization: Bearer TOKEN_JWT_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "trigger": "//meuatalho",
    "title": "Título do Atalho",
    "content": "Conteúdo do atalho",
    "expansion_type": "default"
  }'
```

### Buscar atalhos por filtro

```bash
curl -X POST https://seusite.com/shortcuts/api/shortcuts/search/ \
  -H "Authorization: Bearer TOKEN_JWT_AQUI" \
  -H "Content-Type: application/json" \
  -d '{"query": "email"}'
```

---

## 3. Usuário

### Obter perfil do usuário

```bash
curl -X GET https://seusite.com/users/api/profile/ \
  -H "Authorization: Bearer TOKEN_JWT_AQUI"
```

---

## 4. Exemplos de Integração com Extensão Chrome (JavaScript)

### Login e salvar tokens

```javascript
fetch('https://seusite.com/api/token/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'usuario', password: 'senha' })
})
.then(res => res.json())
.then(data => {
  chrome.storage.local.set({ access: data.access, refresh: data.refresh });
});
```

### Requisição autenticada

```javascript
chrome.storage.local.get(['access'], function(result) {
  fetch('https://seusite.com/shortcuts/api/shortcuts/', {
    method: 'GET',
    headers: { 'Authorization': 'Bearer ' + result.access }
  })
  .then(res => res.json())
  .then(data => { /* processa atalhos */ });
});
```

### Renovar token

```javascript
chrome.storage.local.get(['refresh'], function(result) {
  fetch('https://seusite.com/api/token/refresh/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh: result.refresh })
  })
  .then(res => res.json())
  .then(data => {
    chrome.storage.local.set({ access: data.access });
  });
});
```

---

## 5. Respostas de Erro (Exemplo)

**Erro de autenticação:**
```json
{
  "error": "Usuário ou senha inválidos",
  "code": "invalid_credentials",
  "status": 401
}
```

**Erro de validação:**
```json
{
  "error": "Dados inválidos",
  "details": {
    "trigger": ["Este campo é obrigatório."]
  },
  "code": "invalid",
  "status": 400
}
```

---

## 6. Documentação Interativa

Acesse `/api/docs/` para visualizar e testar todos os endpoints via Swagger/OpenAPI.

---

## 7. Observações

- Sempre utilize HTTPS em produção.
- Os exemplos acima usam URLs fictícias; substitua por seu domínio real.
- Consulte o README para detalhes de configuração e integração.

---