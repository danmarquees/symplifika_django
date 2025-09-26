# 🔧 Documentação Técnica - Symplifika

Este diretório contém documentação técnica detalhada sobre a arquitetura, APIs e integrações do projeto Symplifika.

## 📁 Arquivos Disponíveis

### 🏗️ **Arquitetura e APIs**
- **`api.md`** - Documentação completa das APIs REST
- **`architecture.md`** - Diagrama e explicação da arquitetura do sistema

### 🌐 **Integrações**
- **`CHROME_EXTENSION_INTEGRATION.md`** - Integração completa da extensão Chrome
- **`DASHBOARD_INTEGRATION.md`** - Integração do dashboard e funcionalidades
- **`STRIPE_INTEGRATION.md`** - Integração do sistema de pagamentos Stripe
- **`GEMINI_MIGRATION.md`** - Migração e integração com Google Gemini IA

### 💳 **Sistema de Pagamentos**
- **`PAYMENT_SYSTEM.md`** - Documentação do sistema de pagamentos
- **`STRIPE_TEST_SETUP.md`** - Configuração do ambiente de teste Stripe
- **`README_STRIPE_TESTS.md`** - Guia de testes do Stripe

### 🔗 **Templates e URLs**
- **`TEMPLATES_VIEWS_URLS.md`** - Mapeamento completo de templates, views e URLs

## 🎯 Público-Alvo

Esta documentação é destinada a:
- 👨‍💻 **Desenvolvedores** que trabalham no projeto
- 🔧 **DevOps** responsáveis pelo deploy e infraestrutura
- 🧪 **QA Engineers** que precisam entender as integrações
- 📊 **Arquitetos de Software** analisando o sistema

## 📋 Como Usar

### 1. **Entendendo a Arquitetura**
Comece lendo `architecture.md` para ter uma visão geral do sistema.

### 2. **Trabalhando com APIs**
Consulte `api.md` para detalhes sobre endpoints, autenticação e exemplos de uso.

### 3. **Integrações Específicas**
- Para extensão Chrome: `CHROME_EXTENSION_INTEGRATION.md`
- Para pagamentos: `PAYMENT_SYSTEM.md` e `STRIPE_INTEGRATION.md`
- Para IA: `GEMINI_MIGRATION.md`

### 4. **Configuração de Testes**
Use `STRIPE_TEST_SETUP.md` e `README_STRIPE_TESTS.md` para configurar ambiente de testes.

## 🔍 Índice por Tópico

### **Autenticação**
- JWT implementation em `api.md`
- Refresh token system em `CHROME_EXTENSION_INTEGRATION.md`

### **Banco de Dados**
- Modelos e relacionamentos em `architecture.md`
- Migrações em `TEMPLATES_VIEWS_URLS.md`

### **Frontend**
- Dashboard integration em `DASHBOARD_INTEGRATION.md`
- Chrome extension em `CHROME_EXTENSION_INTEGRATION.md`

### **Pagamentos**
- Stripe setup em `PAYMENT_SYSTEM.md`
- Webhooks em `STRIPE_INTEGRATION.md`
- Testes em `STRIPE_TEST_SETUP.md`

### **IA e Machine Learning**
- Google Gemini em `GEMINI_MIGRATION.md`
- Text expansion em `api.md`

## 🚀 Fluxos Principais

### **Fluxo de Autenticação**
1. Login via API → JWT tokens
2. Refresh automático → Extensão Chrome
3. Logout → Limpeza de tokens

### **Fluxo de Pagamento**
1. Seleção de plano → Stripe Checkout
2. Webhook processing → Atualização de status
3. Confirmação → Página de sucesso

### **Fluxo de Expansão de Texto**
1. Trigger detection → Content script
2. API call → Background script
3. Text replacement → DOM manipulation

## 📊 Diagramas e Esquemas

### **Arquitetura Geral**
```
Frontend (Dashboard) ←→ Django APIs ←→ Database
       ↓                    ↓
Chrome Extension ←→ Background Scripts
       ↓                    ↓
Content Scripts ←→ DOM Manipulation
```

### **Integração de Pagamentos**
```
User → Stripe Checkout → Webhook → Django → Database
  ↓                        ↓         ↓        ↓
Plan Selection → Payment → Processing → Update
```

## 🔧 Ferramentas e Tecnologias

### **Backend**
- Django REST Framework
- JWT Authentication
- PostgreSQL/SQLite
- Celery (background tasks)

### **Frontend**
- Vanilla JavaScript
- Tailwind CSS
- Chrome Extension APIs
- Manifest V3

### **Integrações**
- Stripe Payment Processing
- Google Gemini AI
- CORS configuration
- Webhook handling

## 📝 Contribuindo

Ao adicionar nova documentação técnica:

1. **Siga o padrão**: Use a mesma estrutura dos arquivos existentes
2. **Inclua exemplos**: Sempre forneça código de exemplo
3. **Atualize índices**: Mantenha este README atualizado
4. **Teste instruções**: Verifique se os exemplos funcionam

---

**🔗 Links Relacionados**
- [Guias do Usuário](../user-guides/)
- [Documentação de Deploy](../deployment/)
- [Troubleshooting](../troubleshooting/)
- [Changelog](../changelog/)
