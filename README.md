# Symplifika

Automatize atalhos de texto e produtividade com Django + Extensão Chrome.

## Visão Geral

Symplifika é uma plataforma para criação, gerenciamento e uso de atalhos de texto inteligentes, integrando web, API RESTful e extensão Chrome. Suporta autenticação JWT, integração com IA (Google Gemini), painel responsivo e CI/CD moderno.

---

## Funcionalidades

- Gerenciamento de atalhos personalizados
- API RESTful protegida por JWT
- Integração com extensão Chrome
- Painel web responsivo (Tailwind CSS)
- Suporte a IA (Google Gemini)
- CI/CD com GitHub Actions
- Documentação interativa da API (Swagger/OpenAPI)
- Segurança e boas práticas de desenvolvimento

---

## Como rodar localmente

```bash
git clone https://github.com/seuusuario/symplifika.git
cd symplifika_django
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## Testes

```bash
python manage.py test
```

---

## Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto. Veja `.env.example` para referência.

Principais variáveis:
- `SECRET_KEY`
- `DEBUG`
- `DATABASE_URL`
- `GEMINI_API_KEY`
- `STRIPE_PUBLISHABLE_KEY`
- `STRIPE_SECRET_KEY`

---

## API REST

Principais endpoints:

- **Autenticação:**  
  `POST /api/token/`  
  `POST /api/token/refresh/`

- **Atalhos:**  
  `GET /shortcuts/api/shortcuts/`  
  `POST /shortcuts/api/shortcuts/`

- **Usuário:**  
  `GET /users/api/profile/`

Veja [docs/api.md](docs/api.md) para exemplos detalhados de requisições.

---

## Extensão Chrome

- Instale a extensão via modo desenvolvedor no Chrome.
- Faça login usando sua conta Symplifika.
- Sincronize, crie e use atalhos diretamente no navegador.

Veja [chrome_extension/README.md](chrome_extension/README.md) para integração e instruções.

---

## CI/CD
## Build, minificação e integridade de static files

---

## Monitoramento, Rate Limiting e Segurança

### Sentry (monitoramento de erros)

- Adicione sua chave DSN Sentry ao ambiente:
  ```
  SENTRY_DSN=seu_dsn_aqui
  ```
- O projeto já está configurado para enviar erros automaticamente para o Sentry.

### Slack (notificações)

- Adicione seu webhook Slack ao ambiente:
  ```
  SLACK_WEBHOOK_URL=https://hooks.slack.com/services/SEU/WEBHOOK/URL
  ```
- Use a função `notify_slack("mensagem")` para enviar alertas críticos.

### Email (alertas administrativos)

- Configure as variáveis de email no ambiente:
  ```
  EMAIL_HOST=smtp.seuservidor.com
  EMAIL_PORT=587
  EMAIL_HOST_USER=seu@email.com
  EMAIL_HOST_PASSWORD=senha
  DEFAULT_FROM_EMAIL=Symplifika <no-reply@symplifika.com>
  ```
- Use `send_mail` do Django para enviar notificações administrativas.

### Rate Limiting e Proteção contra Brute Force

- O projeto utiliza **django-ratelimit** para limitar requisições ao endpoint de login.
- Por padrão, cada IP pode tentar login até 10 vezes por minuto.
- Após 5 tentativas falhas consecutivas, o login é bloqueado por 10 minutos para aquele IP/usuário.
- Atividades suspeitas (múltiplas falhas) são logadas e notificadas via Slack (se configurado).
- Para customizar limites, ajuste o decorator `@ratelimit` e a lógica de bloqueio no `login_view`.

**Exemplo de configuração:**
```python
@ratelimit(key='ip', rate='10/m', method='POST', block=True)
def login_view(request):
    # ... proteção contra brute force e monitoramento já implementados
```

---

- Workflow completo em `.github/workflows/django.yml`
- Lint, testes, cobertura, build de static files e análise de segurança automatizados.
- Pronto para deploy em Render, Heroku, AWS, etc.

### Minificação automática

O projeto utiliza **django-compressor** para minificar CSS/JS nos templates.  
No template, use:

```django
{% load compress %}
{% compress css %}
<link rel="stylesheet" href="{% static 'css/base.css' %}">
{% endcompress %}
```

Para minificar offline, rode:

```bash
python manage.py compress
```

### Verificação de integridade dos arquivos estáticos

Após rodar `collectstatic`, você pode verificar a integridade dos arquivos com:

```bash
find staticfiles/ -type f -exec sha256sum {} \; > staticfiles_hashes.txt
```

Compare o arquivo gerado entre builds para garantir que não há arquivos corrompidos ou ausentes.

### Otimização de imagens

Para otimizar PNGs:

```bash
find staticfiles/ -name "*.png" -exec pngquant --force --ext .png {} \;
```

Para minificar CSS gerado pelo Tailwind:

```bash
npx tailwindcss -i ./static/css/base.css -o ./static/css/base.min.css --minify
```

---

---

## Documentação Swagger/OpenAPI

A API do Symplifika possui documentação interativa disponível via Swagger/OpenAPI.

- **Acesse:**  
  `http://localhost:8000/api/docs/` (ambiente local)  
  ou  
  `https://seusite.com/api/docs/` (produção)

Nessa página você pode:
- Visualizar todos os endpoints disponíveis
- Testar requisições diretamente pelo navegador
- Ver exemplos de payloads e respostas
- Gerar código de integração para diversas linguagens

**Recomendação:**  
Consulte a documentação Swagger antes de integrar a extensão ou qualquer sistema externo à API do Symplifika.

---

## Integração com Gemini (IA)

- Configure sua chave Gemini em `.env`
- Use endpoints de IA para expandir atalhos e textos inteligentes.

Veja [docs/gemini.md](docs/gemini.md) para exemplos de uso.

---

## Exemplos de Uso da API

Veja [docs/api.md](docs/api.md) para exemplos práticos de integração (curl, JS, Python).

---

## Contribuição

Pull requests são bem-vindos!  
Sugestões, melhorias e correções podem ser enviadas via issues ou PR.

---

## Licença

MIT

---

## Contato

Dúvidas, sugestões ou suporte:  
[seuemail@dominio.com](mailto:seuemail@dominio.com)

---