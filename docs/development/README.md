# 👨‍💻 Documentação de Desenvolvimento - Symplifika

Este diretório contém documentação específica para desenvolvedores trabalhando no projeto Symplifika.

## 📁 Arquivos Disponíveis

### 🔧 **Configuração**
- **`gemini.md`** - Integração Google Gemini IA
- **`onboarding.md`** - Guia para novos desenvolvedores

### 📱 **Mobile & UX**
- **`MOBILE_RESPONSIVENESS_GUIDE.md`** - Guia de responsividade
- **`MOBILE_RESPONSIVENESS_IMPROVEMENTS.md`** - Melhorias implementadas
- **`ACCESSIBILITY_FIXES.md`** - Correções de acessibilidade

### 🏗️ **Arquitetura**
- **`BEST_PRACTICES_RECOMMENDATIONS.md`** - Boas práticas
- **`PRODUCTION_CHECKLIST.md`** - Checklist de produção

### 🔍 **Melhorias**
- **`QUICK_ACTION_IMPROVEMENTS.md`** - Melhorias quick actions
- **`RELATORIO_INVESTIGACAO_EXTENSAO.md`** - Relatório extensão

## 🚀 Setup Rápido

```bash
# Clone e configure
git clone https://github.com/seuusuario/symplifika.git
cd symplifika_django
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

## 🔧 Stack Tecnológico

### **Backend**
- Django 4.2+ + DRF
- PostgreSQL/SQLite
- Celery + Redis

### **Frontend**
- Vanilla JS + Tailwind CSS
- Chrome Extension (Manifest V3)
- TypeScript + Vite

### **Integrações**
- Google Gemini IA
- Stripe Payments
- Sentry Monitoring

## 📱 Responsividade

### **Breakpoints**
```css
/* Mobile First */
sm: 640px | md: 768px | lg: 1024px | xl: 1280px
```

### **Componentes Responsivos**
- ✅ Navbar adaptativa
- ✅ Sidebar colapsável  
- ✅ Cards flexíveis
- ✅ Formulários otimizados

## ♿ Acessibilidade

### **Padrões WCAG 2.1**
- ✅ Navegação por teclado
- ✅ Screen reader support
- ✅ Contraste adequado (AA)
- ✅ ARIA labels
- ✅ Focus indicators

## 🧪 Testes

```bash
# Django Tests
python manage.py test

# Coverage
coverage run --source='.' manage.py test
coverage report

# Linting
flake8 .
eslint static/js/
```

## 🔒 Segurança

- ✅ CSRF Protection
- ✅ JWT Authentication
- ✅ Rate Limiting
- ✅ Input Validation
- ✅ CORS configurado

## 📊 Performance

- ✅ Static files compressão
- ✅ Database indexação
- ✅ Caching estratégico
- ✅ Lazy loading

---

**🎯 Objetivo**: Manter código limpo, testável e performático seguindo as melhores práticas de desenvolvimento web moderno.
