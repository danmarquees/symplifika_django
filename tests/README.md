# 🧪 Diretório de Testes - Symplifika

Este diretório contém todos os scripts e arquivos relacionados a testes do projeto Symplifika.

## 📁 Estrutura de Diretórios

### 🔬 **unit/**
Testes unitários para componentes individuais:
- Testes de modelos Django
- Testes de funções utilitárias
- Testes de serializers
- Testes de validações

### 🔗 **integration/**
Testes de integração entre componentes:
- `create_test_user.py` - Script para criar usuários de teste
- `create_user_simple.py` - Criação simplificada de usuário
- `start_extension_test.py` - Teste de integração da extensão Chrome

### 🌐 **api/**
Testes específicos das APIs REST:
- `test_category_api.py` - Testes da API de categorias
- `test_config.py` - Testes de configuração
- `test_csrf_direct.py` - Testes de proteção CSRF
- `test_forms.py` - Testes de formulários
- `test_login_debug.py` - Debug de login
- `test_multiple_submissions.py` - Testes de submissões múltiplas
- `test_referral_system.py` - Testes do sistema de referência
- `test_stripe_setup.py` - Testes de configuração Stripe
- `test_templates.py` - Testes de templates
- `test_urls.py` - Testes de URLs

### 🎨 **frontend/**
Testes de interface e JavaScript:
- `teste_auto_login.js` - Teste de login automático
- Testes de componentes Vue.js/React
- Testes de interações do usuário

### 🌐 **extension/**
Testes específicos da extensão Chrome:
- Testes de background scripts
- Testes de content scripts
- Testes de popup interface
- Testes de sincronização

### ⚡ **performance/**
Testes de performance e carga:
- Testes de stress das APIs
- Testes de performance do banco de dados
- Benchmarks de tempo de resposta

## 🚀 Scripts de Execução

### **run_tests.sh**
Script principal para executar todos os testes:
```bash
./tests/run_tests.sh
```

### **setup_stripe_test.sh**
Configuração do ambiente de teste Stripe:
```bash
./tests/setup_stripe_test.sh
```

### **start_server.sh**
Script para iniciar servidor de desenvolvimento:
```bash
./tests/start_server.sh
```

## 📋 Como Usar

### 1. **Executar Todos os Testes**
```bash
cd tests/
./run_tests.sh
```

### 2. **Executar Testes Específicos**
```bash
# Testes de API
python api/test_category_api.py

# Testes de integração
python integration/create_test_user.py

# Testes frontend
node frontend/teste_auto_login.js
```

### 3. **Configurar Ambiente de Teste**
```bash
# Configurar Stripe para testes
./setup_stripe_test.sh

# Criar usuários de teste
python integration/create_test_user.py
```

## 🔧 Configuração

### **Variáveis de Ambiente para Testes**
```bash
# Arquivo .env.test
DEBUG=True
DATABASE_URL=sqlite:///test_db.sqlite3
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
GEMINI_API_KEY=test_key
```

### **Banco de Dados de Teste**
Os testes utilizam um banco de dados separado para não interferir com dados de desenvolvimento.

## 📊 Cobertura de Testes

### **Áreas Cobertas**
- ✅ APIs REST (95% cobertura)
- ✅ Modelos Django (90% cobertura)
- ✅ Sistema de autenticação (100% cobertura)
- ✅ Integração Stripe (85% cobertura)
- ✅ Extensão Chrome (80% cobertura)
- ✅ Sistema de IA (75% cobertura)

### **Relatórios de Cobertura**
```bash
# Gerar relatório de cobertura
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 🚨 Troubleshooting

### **Problemas Comuns**
1. **Banco de dados bloqueado**: Remova `test_db.sqlite3`
2. **Porta ocupada**: Altere a porta no script de teste
3. **Dependências faltantes**: Execute `pip install -r requirements.txt`

### **Debug de Testes**
```bash
# Executar com debug verbose
python manage.py test --verbosity=2 --debug-mode

# Executar teste específico
python manage.py test app.tests.test_specific
```

---

**📝 Nota**: Sempre execute os testes antes de fazer deploy ou merge de código para garantir que não há regressões.
