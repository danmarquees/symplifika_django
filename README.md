# Symplifika

🚀 **Plataforma completa de automação de texto com IA integrada**

Automatize atalhos de texto e produtividade com Django + Extensão Chrome + Inteligência Artificial.

---

## Visão Geral

Symplifika é uma plataforma moderna e completa para criação, gerenciamento e uso de atalhos de texto inteligentes. Integra perfeitamente aplicação web, API RESTful robusta, extensão Chrome avançada e inteligência artificial (Google Gemini). 

**🎯 Principais Diferenciais:**
- ✅ **Dashboard Moderno**: Interface responsiva com design system completo
- ✅ **IA Integrada**: Expansão inteligente de texto com Google Gemini
- ✅ **Extensão Chrome**: Funcionalidade completa com UX/UI alinhada
- ✅ **APIs Robustas**: Sistema completo de autenticação JWT e endpoints
- ✅ **Sistema de Pagamentos**: Integração Stripe para planos Premium/Enterprise
- ✅ **UX/UI Moderna**: Toast notifications, configurações avançadas, temas
- ✅ **Totalmente Funcional**: Pronto para produção

---

## Documentação Completa

- Veja uma explicação geral sobre o que é o Symplifika, o que ele faz e como funciona em [`docs/como-funciona.md`](docs/como-funciona.md)

## Documentação Técnica

- Exemplos práticos de integração: veja [`docs/examples.md`](docs/examples.md)
- Diagrama de arquitetura do sistema: veja [`docs/architecture.md`](docs/architecture.md)

---

## ✨ Funcionalidades Implementadas

### 🎨 **Interface e UX/UI**
- ✅ **Dashboard Moderno**: Interface responsiva com design system Symplifika
- ✅ **Sistema de Toast**: Notificações elegantes com 5 tipos (success, error, warning, info, symplifika)
- ✅ **Navbar Completa**: User menu funcional com todos os ícones SVG
- ✅ **Temas Dinâmicos**: Light/Dark mode com aplicação em tempo real
- ✅ **Search Bar Inteligente**: Busca com sugestões, filtros e atalho Ctrl+K
- ✅ **Configurações Avançadas**: 5 seções completas (Perfil, Conta, Notificações, Privacidade, Aparência)

### 🚀 **Funcionalidades Core**
- ✅ **Gerenciamento de Atalhos**: CRUD completo com categorização
- ✅ **Campo URL de Contexto**: Sugestões inteligentes de gatilhos por serviço
- ✅ **Sistema de Estatísticas**: Dashboard com métricas em tempo real
- ✅ **Histórico de Uso**: Tracking completo de atalhos utilizados
- ✅ **Ações em Lote**: Operações múltiplas em atalhos

### 🤖 **Inteligência Artificial**
- ✅ **Google Gemini Integrado**: Expansão inteligente de texto
- ✅ **Templates de Email**: Geração automática com IA
- ✅ **Sugestões de Atalhos**: Criação inteligente baseada em contexto
- ✅ **Regeneração de Conteúdo**: Melhoria automática de textos
- ✅ **Logs de IA**: Monitoramento completo de uso

### 🔐 **Autenticação e Segurança**
- ✅ **JWT com Refresh Token**: Sistema robusto de autenticação
- ✅ **Rate Limiting**: Proteção contra brute force
- ✅ **CORS Configurado**: Suporte completo para extensão Chrome
- ✅ **Validações Robustas**: Tratamento de erros em todas as APIs
- ✅ **Exception Handler**: Tratamento customizado de erros JWT

### 💳 **Sistema de Pagamentos**
- ✅ **Stripe Integrado**: Checkout sessions para Premium/Enterprise
- ✅ **Webhooks**: Processamento automático de pagamentos
- ✅ **Planos Dinâmicos**: Free, Premium (R$ 29,90), Enterprise (R$ 99,90)
- ✅ **Página de Sucesso**: Confirmação pós-pagamento

### 🌐 **Extensão Chrome**
- ✅ **Interface Moderna**: UX/UI alinhada com aplicação principal
- ✅ **Glassmorphism Design**: Efeitos backdrop blur e gradientes
- ✅ **Toast Notifications**: Sistema completo na extensão
- ✅ **Quick Action Icon**: Dropdown moderno com hover effects
- ✅ **Autenticação Integrada**: Login/logout sincronizado
- ✅ **Expansão Automática**: Detecção e substituição de gatilhos

### 📊 **APIs RESTful**
- ✅ **Endpoints Completos**: 25+ endpoints funcionais
- ✅ **Documentação Swagger**: API interativa disponível
- ✅ **Paginação**: Suporte completo em listagens
- ✅ **Filtros Avançados**: Busca por múltiplos critérios
- ✅ **Serializers Robustos**: Validação completa de dados

### 🛠️ **DevOps e Infraestrutura**
- ✅ **CI/CD GitHub Actions**: Pipeline completo automatizado
- ✅ **Django Compressor**: Minificação automática de assets
- ✅ **Static Files**: Coleta e otimização automática
- ✅ **Environment Variables**: Configuração flexível
- ✅ **Error Monitoring**: Sentry integrado

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

## ⚙️ Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto. Veja `.env.example` para referência completa.

### 🔧 **Configurações Básicas**
```bash
SECRET_KEY=sua-chave-secreta-django
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 🤖 **Integração IA (Google Gemini)**
```bash
GEMINI_API_KEY=sua-chave-do-google-gemini
```

### 💳 **Pagamentos (Stripe)**
```bash
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### 📧 **Email e Notificações**
```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app
DEFAULT_FROM_EMAIL=Symplifika <no-reply@symplifika.com>
```

### 📊 **Monitoramento**
```bash
SENTRY_DSN=https://sua-dsn-sentry.ingest.sentry.io/
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

### 🔒 **Segurança**
```bash
CORS_ALLOWED_ORIGINS=http://localhost:3000,chrome-extension://*
CSRF_TRUSTED_ORIGINS=http://localhost:8000
```

---

## 🔌 API REST Completa

### 🔐 **Autenticação JWT**
```http
POST /api/token/                    # Login e obtenção de tokens
POST /api/token/refresh/            # Refresh do access token
```

### 👤 **Usuário e Perfil**
```http
GET  /api/profile/                  # Dados do perfil
PUT  /api/profile/                  # Atualizar perfil
GET  /api/account/                  # Configurações da conta
PUT  /api/account/                  # Atualizar conta
POST /api/change-password/          # Alterar senha
GET  /api/notifications-preferences/ # Preferências de notificação
PUT  /api/notifications-preferences/ # Atualizar preferências
POST /api/profile/avatar/upload/    # Upload de avatar
DELETE /api/profile/avatar/delete/  # Remover avatar
GET  /api/profile/export/           # Exportar dados
DELETE /api/profile/delete/         # Excluir conta
```

### ⚡ **Atalhos (Shortcuts)**
```http
GET    /shortcuts/api/shortcuts/           # Listar atalhos
POST   /shortcuts/api/shortcuts/           # Criar atalho
GET    /shortcuts/api/shortcuts/{id}/      # Detalhes do atalho
PUT    /shortcuts/api/shortcuts/{id}/      # Atualizar atalho
DELETE /shortcuts/api/shortcuts/{id}/      # Excluir atalho
POST   /shortcuts/api/shortcuts/search/   # Busca avançada
GET    /shortcuts/api/shortcuts/stats/    # Estatísticas de atalhos
GET    /shortcuts/api/shortcuts/most-used/ # Atalhos mais usados
POST   /shortcuts/api/shortcuts/bulk-action/ # Ações em lote
POST   /shortcuts/api/shortcuts/{id}/use/ # Marcar atalho como usado
POST   /shortcuts/api/shortcuts/{id}/regenerate-ai/ # Regenerar com IA
GET    /shortcuts/api/shortcuts/{id}/usage-history/ # Histórico de uso
```

### 📁 **Categorias**
```http
GET    /shortcuts/api/categories/          # Listar categorias
POST   /shortcuts/api/categories/          # Criar categoria
GET    /shortcuts/api/categories/{id}/     # Detalhes da categoria
PUT    /shortcuts/api/categories/{id}/     # Atualizar categoria
DELETE /shortcuts/api/categories/{id}/     # Excluir categoria
GET    /shortcuts/api/categories/{id}/shortcuts/ # Atalhos da categoria
```

### 📊 **Dashboard e Estatísticas**
```http
GET /api/dashboard/stats/           # Estatísticas do dashboard
```

### 📈 **Uso e IA**
```http
GET /shortcuts/api/usage/           # Histórico de uso
GET /shortcuts/api/ai-logs/         # Logs de processamento IA
```

### 💳 **Pagamentos (Stripe)**
```http
POST /payments/create-checkout-session/ # Criar sessão de checkout
POST /payments/webhook/             # Webhook do Stripe
GET  /users/subscription-success/   # Página de sucesso
```

### 📚 **Documentação Interativa**
- **Swagger UI**: `http://localhost:8000/api/docs/`
- **Redoc**: `http://localhost:8000/api/redoc/`

Veja [docs/api.md](docs/api.md) para exemplos detalhados de requisições.

---

## 🌐 Extensão Chrome Completa

### ✨ **Funcionalidades Implementadas**
- ✅ **Interface Moderna**: UX/UI alinhada com aplicação principal
- ✅ **Glassmorphism Design**: Backdrop blur, gradientes e efeitos visuais
- ✅ **Autenticação JWT**: Login/logout sincronizado com refresh token automático
- ✅ **Toast Notifications**: Sistema completo de notificações na extensão
- ✅ **Quick Action Icon**: Dropdown moderno com hover effects
- ✅ **Expansão Automática**: Detecção e substituição de gatilhos em tempo real
- ✅ **Sincronização**: Atalhos sincronizados automaticamente com o servidor

### 🚀 **Como Instalar e Usar**

#### **1. Compilar a Extensão**
```bash
cd chrome_extension
npm install
npm run build
```

#### **2. Instalar no Chrome**
1. Abra `chrome://extensions/`
2. Ative "Modo do desenvolvedor"
3. Clique em "Carregar sem compactação"
4. Selecione a pasta `chrome_extension/dist/`

#### **3. Configurar e Usar**
1. **Login**: Clique no ícone da extensão e faça login
2. **Sincronização**: Atalhos são sincronizados automaticamente
3. **Uso**: Digite `!atalho` + espaço em qualquer campo de texto
4. **Expansão**: Texto é substituído automaticamente

### 🎨 **Design System Moderno**
- **Popup**: 400x600px com gradiente Symplifika
- **Cards**: Glassmorphism com backdrop blur 20px
- **Animações**: Transições suaves e micro-interações
- **Toast System**: 4 tipos (success, error, warning, info)
- **Responsive**: Adaptação automática para diferentes contextos

### 🔧 **Arquitetura Técnica**
- **Manifest V3**: Versão mais recente do Chrome Extensions
- **Background Script**: Service worker para processamento
- **Content Script**: Injeção e detecção em páginas web
- **Popup Interface**: React/Vue.js com design moderno
- **Storage API**: Persistência local de dados e configurações

### 📱 **Funcionalidades Avançadas**
- **Context Invalidation Handling**: Recuperação automática de erros
- **TrustedHTML Policy**: Segurança moderna do navegador
- **Message Port Management**: Comunicação robusta entre scripts
- **Auto-reconnection**: Reconexão automática em caso de falhas
- **Error Recovery**: Tratamento gracioso de erros

Veja [chrome_extension/README.md](chrome_extension/README.md) para documentação técnica completa.

---

## CI/CD

O projeto possui integração contínua (CI) e deploy contínuo (CD) via GitHub Actions, incluindo lint, testes, análise de segurança, build de arquivos estáticos e **deploy automático no Render**.

Veja o guia completo de deploy em [`docs/deploy.md`](docs/deploy.md).

## Build, minificação e integridade de static files

---

## Onboarding para Novos Desenvolvedores

Se você deseja contribuir ou rodar o projeto localmente, siga estes passos:

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seuusuario/symplifika.git
   cd symplifika_django
   ```

2. **Crie e ative um ambiente virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente:**
   - Copie o arquivo de exemplo:  
     `cp env_example.txt .env`
   - Edite `.env` conforme necessário.

5. **Execute as migrações e rode o servidor:**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

6. **Rodando os testes:**
   ```bash
   python manage.py test
   ```

### Estrutura dos principais diretórios/apps

- `core/` — Lógica principal, views, templates centrais
- `users/` — Autenticação, perfis, assinaturas
- `payments/` — Integração com Stripe
- `chrome_extension/` — Código da extensão Chrome
- `templates/` — Templates HTML
- `static/` — Arquivos estáticos (CSS, JS, imagens)
- `docs/` — Documentação técnica, exemplos, diagramas

Para mais detalhes sobre integração, exemplos de código e arquitetura, consulte a seção "Documentação Técnica" acima.

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

## 🤖 Integração com IA (Google Gemini)

### ✨ **Funcionalidades IA Implementadas**
- ✅ **Expansão Inteligente**: Melhoria automática de textos de atalhos
- ✅ **Templates de Email**: Geração automática com diferentes tons
- ✅ **Sugestões de Atalhos**: Criação inteligente baseada em contexto
- ✅ **Regeneração de Conteúdo**: Melhoria de atalhos existentes
- ✅ **Logs Detalhados**: Monitoramento completo de uso da IA

### 🔧 **Configuração**
```bash
# Adicione no arquivo .env
GEMINI_API_KEY=sua-chave-do-google-gemini
```

### 🚀 **Como Usar**
1. **Obter API Key**: Registre-se em [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Configurar .env**: Adicione a chave no arquivo de ambiente
3. **Criar Atalhos IA**: Selecione "Expansão com IA" ao criar atalhos
4. **Regenerar**: Use o endpoint `/shortcuts/{id}/regenerate-ai/`

### 📊 **Características Técnicas**
- **Modelo**: `gemini-1.5-flash`
- **Max Tokens**: 500 (configurável)
- **Temperature**: 0.7 (configurável)
- **Fallback Gracioso**: Funciona mesmo sem API key
- **Rate Limiting**: Controle de uso por usuário

Veja [docs/gemini.md](docs/gemini.md) para exemplos de uso detalhados.

---

## 📊 Status do Projeto

### ✅ **Totalmente Implementado e Funcional**
- 🎯 **Dashboard**: Interface moderna 100% funcional
- 🔌 **APIs**: 25+ endpoints completamente operacionais
- 🌐 **Extensão Chrome**: UX/UI moderna e totalmente integrada
- 🤖 **IA**: Google Gemini integrado com fallback gracioso
- 💳 **Pagamentos**: Stripe completamente configurado
- 🔐 **Autenticação**: JWT com refresh token automático
- 🎨 **UX/UI**: Sistema de toast, configurações, temas
- 📱 **Responsivo**: Funciona perfeitamente em todos os dispositivos

### 🚀 **Pronto para Produção**
- ✅ Todas as funcionalidades testadas e funcionais
- ✅ Tratamento robusto de erros implementado
- ✅ Sistema de notificações ativo
- ✅ Documentação completa disponível
- ✅ CI/CD pipeline configurado
- ✅ Segurança e validações implementadas

### 🎯 **Principais Conquistas**
1. **Resolução Completa de APIs 404**: Todas as URLs funcionais
2. **Sistema Toast Notifications**: Implementado globalmente
3. **Extensão Chrome Moderna**: UX/UI alinhada com app principal
4. **Configurações Avançadas**: 5 seções completas funcionais
5. **IA Totalmente Integrada**: Google Gemini operacional
6. **Sistema de Pagamentos**: Stripe checkout completo
7. **User Menu Navbar**: Totalmente funcional com ícones SVG
8. **Campo URL de Contexto**: Sugestões inteligentes implementadas

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

## 📞 Contato e Suporte

### 🚀 **Projeto Totalmente Funcional**
O Symplifika está **100% implementado e operacional**, com todas as funcionalidades principais desenvolvidas e testadas. O projeto está pronto para uso em produção.

### 💬 **Suporte Técnico**
- **Issues**: [GitHub Issues](https://github.com/danmarquees/symplifika/issues)
- **Documentação**: Consulte os arquivos em `docs/` para detalhes técnicos
- **API Docs**: Acesse `http://localhost:8000/api/docs/` para documentação interativa

### 🤝 **Contribuições**
Pull requests são bem-vindos! O projeto segue as melhores práticas de desenvolvimento:
- ✅ Código limpo e documentado
- ✅ Testes automatizados
- ✅ CI/CD pipeline configurado
- ✅ Padrões de segurança implementados

### 📧 **Contato**
Para dúvidas, sugestões ou parcerias:  
[contato@symplifika.com](mailto:contato@symplifika.com)

---

## 🎉 Conclusão

O **Symplifika** representa uma solução completa e moderna para automação de texto, combinando:

- 🎨 **Interface Moderna**: UX/UI de alta qualidade
- 🤖 **Inteligência Artificial**: Integração com Google Gemini
- 🌐 **Extensão Chrome**: Experiência seamless no navegador
- 🔐 **Segurança Robusta**: Autenticação JWT e validações completas
- 💳 **Monetização**: Sistema de pagamentos Stripe integrado
- 📊 **Analytics**: Métricas e estatísticas detalhadas
- 🚀 **Pronto para Produção**: Todas as funcionalidades implementadas

**Status: ✅ PROJETO COMPLETO E FUNCIONAL**

---