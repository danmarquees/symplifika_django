# Exemplos Práticos de Integração

Este documento apresenta exemplos reais de como consumir a API do Symplifika, integrar com os endpoints de IA (Google Gemini) e interagir com a API a partir da extensão Chrome.

---

## 1. Consumo da API REST

### Autenticação JWT

**Obter token de acesso:**

```bash
curl -X POST https://seusite.com/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "usuario", "password": "senha"}'
```

**Resposta esperada:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOi...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."
}
```

### Listar atalhos do usuário (Python)

```python
import requests

token = "SEU_TOKEN_JWT"
resp = requests.get(
    "https://seusite.com/shortcuts/api/shortcuts/",
    headers={"Authorization": f"Bearer {token}"}
)
print(resp.json())
```

### Criar novo atalho (JavaScript)

```js
fetch("https://seusite.com/shortcuts/api/shortcuts/", {
  method: "POST",
  headers: {
    "Authorization": "Bearer SEU_TOKEN_JWT",
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    title: "Saudação",
    content: "Olá, tudo bem?",
    category: "Pessoal"
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

---

## 2. Uso dos Endpoints de IA (Google Gemini)

### Expandir texto inteligente (Python)

```python
import requests

token = "SEU_TOKEN_JWT"
payload = {
    "prompt": "Resuma o texto: Inteligência Artificial está transformando o mundo..."
}
resp = requests.post(
    "https://seusite.com/ai/api/gemini/expand/",
    headers={"Authorization": f"Bearer {token}"},
    json=payload
)
print(resp.json())
```

**Resposta esperada:**
```json
{
  "result": "Resumo: A IA está mudando diversos setores..."
}
```

---

## 3. Comunicação da Extensão Chrome com a API

### Exemplo de chamada na extensão (background.js)

```js
async function fetchShortcuts(token) {
  const response = await fetch("https://seusite.com/shortcuts/api/shortcuts/", {
    headers: { "Authorization": "Bearer " + token }
  });
  return await response.json();
}

// Uso típico na extensão:
chrome.storage.local.get(["jwt_token"], ({ jwt_token }) => {
  fetchShortcuts(jwt_token).then(shortcuts => {
    // Atualiza popup ou insere atalhos no campo ativo
    console.log(shortcuts);
  });
});
```

### Enviando novo atalho a partir do popup

```js
document.getElementById("saveBtn").onclick = async () => {
  const token = await getTokenSomehow();
  const title = document.getElementById("title").value;
  const content = document.getElementById("content").value;
  fetch("https://seusite.com/shortcuts/api/shortcuts/", {
    method: "POST",
    headers: {
      "Authorization": "Bearer " + token,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ title, content, category: "Rápido" })
  })
  .then(res => res.json())
  .then(data => alert("Atalho salvo!"));
};
```

---

## 4. Dicas Gerais

- Sempre utilize HTTPS em produção.
- O token JWT deve ser armazenado de forma segura (ex: `chrome.storage.local` na extensão).
- Consulte a documentação Swagger/OpenAPI em `/api/docs/` para detalhes de todos os endpoints.
- Para integração com IA, consulte também `docs/gemini.md`.

---

## 5. Referências

- [Documentação Swagger/OpenAPI](../README.md#documentação-swaggeropenapi)
- [Guia de Deploy](./deploy.md)
- [Google Gemini API](https://ai.google.dev/)
- [Documentação Chrome Extensions](https://developer.chrome.com/docs/extensions/)

---