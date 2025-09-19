# Guia de Deploy Automático no Render

Este guia explica como configurar o deploy contínuo do Symplifika Django usando o Render e o GitHub Actions.

---

## 1. Pré-requisitos

- Conta no [Render](https://render.com/)
- Projeto Django já hospedado no Render (Web Service configurado)
- Repositório no GitHub com acesso de administrador

---

## 2. Configurando o Render

1. **Crie um serviço Web no Render**:
   - Escolha "Web Service"
   - Conecte ao seu repositório GitHub
   - Defina o comando de start:  
     ```
     gunicorn symplifika.wsgi:application
     ```
   - Configure as variáveis de ambiente necessárias (SECRET_KEY, DATABASE_URL, etc)

2. **Obtenha o Service ID**:
   - No painel do Render, acesse o serviço criado.
   - O Service ID está na URL ou na aba "Settings" (exemplo: `srv-xxxxxxxxxxxxxxxxxxxx`).

3. **Crie um API Key no Render**:
   - Vá em "Account Settings" > "API Keys"
   - Gere uma nova chave e copie o valor.

---

## 3. Configurando Secrets no GitHub

No repositório do GitHub:

1. Vá em **Settings > Secrets and variables > Actions**.
2. Clique em **New repository secret** e adicione:
   - `RENDER_API_KEY` — Cole o valor da API Key do Render.
   - `RENDER_SERVICE_ID` — Cole o Service ID do seu serviço Render.

> **Importante:**  
> Nunca exponha essas chaves em código ou logs públicos.

---

## 4. Workflow de Deploy (GitHub Actions)

O arquivo `.github/workflows/django.yml` já está configurado para deploy automático após passar nos testes, lint, coleta de estáticos e análise de segurança.

Trecho relevante do workflow:

```yaml
deploy:
  runs-on: ubuntu-latest
  needs: [test, staticfiles, security]
  steps:
    - name: Checkout code
      uses: actions/checkout@v4
    - name: Install Render CLI
      run: |
        curl -fsSL https://cdn.render.com/cli/install.sh | bash
        export PATH="$HOME/.render:$PATH"
    - name: Deploy to Render
      env:
        RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
      run: |
        export PATH="$HOME/.render:$PATH"
        render deploy --service ${{ secrets.RENDER_SERVICE_ID }} --api-key $RENDER_API_KEY
```

---

## 5. Fluxo Completo

1. Push ou Pull Request para `main` ou `master` no GitHub.
2. CI executa lint, testes, coleta de estáticos e análise de segurança.
3. Se tudo passar, o deploy é disparado automaticamente para o Render.
4. O Render faz o build e publica a nova versão do serviço.

---

## 6. Dicas e Boas Práticas

- Sempre mantenha as variáveis sensíveis como **secrets** no GitHub e Render.
- Monitore o deploy pelo painel do Render e logs do GitHub Actions.
- Para rollback, use o painel do Render para restaurar builds anteriores.
- Atualize as secrets se trocar o Service ID ou API Key.

---

## 7. Referências

- [Documentação Render CLI](https://render.com/docs/cli)
- [Deploy de Django no Render](https://render.com/docs/deploy-django)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

Em caso de dúvidas, consulte o README do projeto ou abra uma issue.