# Deploy da Landing Page Symplifika 🚀

Este guia detalha como fazer o deploy da landing page em diferentes plataformas e configurar todas as integrações necessárias.

## 📋 Pré-requisitos

- [ ] Domínio configurado (`symplifika.com` ou subdomínio)
- [ ] Certificado SSL ativo
- [ ] Contas nos serviços de analytics (opcional)
- [ ] Backend Django configurado (para API endpoints)

## 🌐 Opções de Deploy

### 1. Deploy Estático (Recomendado para MVP)

#### A. Netlify (Mais Fácil)

```bash
# 1. Instalar Netlify CLI
npm install -g netlify-cli

# 2. Build de produção
npm run build

# 3. Deploy
netlify deploy --prod --dir .
```

**Configurações no Netlify Dashboard:**
- **Site name**: `symplifika-landing`
- **Domain**: Configure seu domínio personalizado
- **Environment variables**:
  - `NODE_ENV=production`
  - `GA_TRACKING_ID=seu-google-analytics-id`

**Redirects** (criar arquivo `_redirects`):
```
# Redirect da raiz para landing page
/  /index.html  200

# API fallbacks para desenvolvimento local
/api/*  http://localhost:8000/api/:splat  200  Country=br
```

#### B. Vercel

```bash
# 1. Instalar Vercel CLI
npm install -g vercel

# 2. Deploy
vercel --prod
```

**Arquivo `vercel.json`:**
```json
{
  "version": 2,
  "builds": [
    {
      "src": "index.html",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "http://seu-backend-django.com/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/$1"
    }
  ]
}
```

#### C. GitHub Pages

```bash
# 1. Criar branch gh-pages
git checkout -b gh-pages

# 2. Build e commit
npm run build
git add dist/
git commit -m "Deploy to GitHub Pages"

# 3. Push
git push origin gh-pages
```

**GitHub Actions** (`.github/workflows/deploy.yml`):
```yaml
name: Deploy Landing Page
on:
  push:
    branches: [ main ]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Setup Node
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    - name: Install and Build
      run: |
        npm install
        npm run build
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./dist
```

### 2. Integração com Django

#### A. Servir via Django Templates

**1. Configurar no Django:**

```python
# settings.py
STATICFILES_DIRS = [
    BASE_DIR / "landing_page/assets",
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'landing_page'],
        # ...
    },
]
```

**2. URLs:**

```python
# urls.py
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    # Landing page como página inicial
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    
    # APIs da landing page
    path('api/', include('landing_page.urls')),
    
    # Dashboard principal (após login)
    path('app/', include('core.urls')),
]
```

**3. Template Django** (substituir `index.html`):

```html
<!DOCTYPE html>
<html lang="pt-BR" class="scroll-smooth">
<head>
    {% load static %}
    <meta charset="UTF-8">
    <title>{% block title %}Symplifika - Automações Fáceis e Rápidas | Em Breve{% endblock %}</title>
    
    <!-- CSS -->
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
    
    <!-- Analytics -->
    {% if not debug %}
    <!-- Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={{ GA_TRACKING_ID }}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', '{{ GA_TRACKING_ID }}');
    </script>
    {% endif %}
</head>
<body>
    <!-- Conteúdo da landing page aqui -->
    
    <!-- Scripts -->
    <script src="{% static 'js/main.js' %}"></script>
    <script>
        // Configurar URLs da API
        window.LANDING_CONFIG = {
            ...window.LANDING_CONFIG,
            API: {
                BASE_URL: '{{ request.get_host }}',
                ENDPOINTS: {
                    WAITLIST_SUBMIT: '{% url "waitlist_submit" %}',
                    ANALYTICS_TRACK: '{% url "analytics_track" %}'
                }
            }
        };
    </script>
</body>
</html>
```

#### B. Deploy Django + Landing Page

**1. Render.com:**

```yaml
# render.yaml
services:
  - type: web
    name: symplifika-app
    env: python
    buildCommand: |
      pip install -r requirements.txt
      python manage.py collectstatic --noinput
      python manage.py migrate
    startCommand: gunicorn symplifika.wsgi:application
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.5
      - key: DATABASE_URL
        fromDatabase:
          name: symplifika-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: GA_TRACKING_ID
        value: UA-XXXXXXXXX-X

databases:
  - name: symplifika-db
    databaseName: symplifika
    user: symplifika
```

**2. Heroku:**

```bash
# Procfile
web: gunicorn symplifika.wsgi:application
release: python manage.py migrate
```

```bash
# Deploy
heroku create symplifika-app
heroku addons:create heroku-postgresql:mini
heroku config:set SECRET_KEY=sua-secret-key
heroku config:set GA_TRACKING_ID=seu-google-analytics-id
git push heroku main
```

## 📊 Configurar Analytics

### Google Analytics 4

**1. Criar propriedade no GA4:**
- Acesse [Google Analytics](https://analytics.google.com)
- Crie nova propriedade
- Copie o Measurement ID (GA-XXXXXXXXX-X)

**2. Configurar no código:**

```javascript
// No index.html ou template Django
gtag('config', 'GA-XXXXXXXXX-X', {
  page_title: 'Symplifika Landing Page',
  page_location: window.location.href
});

// Eventos customizados
gtag('event', 'waitlist_signup', {
  event_category: 'conversion',
  event_label: 'email_signup',
  value: 1
});
```

### Google Tag Manager (Alternativa)

**1. Criar container no GTM**
**2. Adicionar no `<head>`:**

```html
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-XXXXXXX');</script>
```

### Facebook Pixel (Opcional)

```html
<script>
!function(f,b,e,v,n,t,s)
{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}(window,document,'script',
'https://connect.facebook.net/en_US/fbevents.js');

fbq('init', 'YOUR_PIXEL_ID');
fbq('track', 'PageView');
</script>
```

## 🔧 Configurações de Produção

### 1. Variáveis de Ambiente

**Arquivo `.env.production`:**

```env
# Ambiente
NODE_ENV=production
DEBUG=false

# Analytics
GA_TRACKING_ID=GA-XXXXXXXXX-X
GTM_ID=GTM-XXXXXXX
FACEBOOK_PIXEL_ID=123456789

# APIs
API_BASE_URL=https://symplifika.com
DJANGO_SECRET_KEY=sua-secret-key-super-segura

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@symplifika.com
SMTP_PASSWORD=sua-senha-app

# Database
DATABASE_URL=postgres://user:pass@host:port/db

# Cache
REDIS_URL=redis://localhost:6379/0

# Monitoring
SENTRY_DSN=https://xxx@sentry.io/xxx
```

### 2. Otimizações de Performance

**CSP Headers** (Content Security Policy):

```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               script-src 'self' 'unsafe-inline' https://www.google-analytics.com https://www.googletagmanager.com; 
               style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; 
               font-src https://fonts.gstatic.com; 
               img-src 'self' data: https:;">
```

**Service Worker** (cache estático):

```javascript
// sw.js
const CACHE_NAME = 'symplifika-landing-v1';
const urlsToCache = [
  '/',
  '/assets/css/style.css',
  '/assets/js/main.js',
  'https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
```

### 3. Monitoramento

**Sentry** (Error Tracking):

```javascript
// No main.js
import * as Sentry from "@sentry/browser";

if (LANDING_CONFIG.SENTRY_DSN) {
  Sentry.init({
    dsn: LANDING_CONFIG.SENTRY_DSN,
    environment: LANDING_CONFIG.ENVIRONMENT
  });
}
```

**Uptime Monitoring:**
- [UptimeRobot](https://uptimerobot.com)
- [Pingdom](https://pingdom.com)
- [StatusCake](https://statuscake.com)

## 🔍 SEO e Performance

### 1. Meta Tags Essenciais

```html
<!-- Open Graph -->
<meta property="og:title" content="Symplifika - Automações Fáceis e Rápidas">
<meta property="og:description" content="Plataforma de automação de texto com IA integrada">
<meta property="og:image" content="https://symplifika.com/og-image.jpg">
<meta property="og:url" content="https://symplifika.com">
<meta property="og:type" content="website">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Symplifika - Automações Fáceis e Rápidas">
<meta name="twitter:description" content="Plataforma de automação de texto com IA integrada">
<meta name="twitter:image" content="https://symplifika.com/twitter-image.jpg">

<!-- Schema.org -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Symplifika",
  "description": "Plataforma de automação de texto com IA integrada",
  "url": "https://symplifika.com",
  "applicationCategory": "ProductivityApplication",
  "operatingSystem": "Web, Chrome Extension"
}
</script>
```

### 2. Sitemap.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://symplifika.com/</loc>
    <lastmod>2024-01-15</lastmod>
    <priority>1.0</priority>
  </url>
</urlset>
```

### 3. Robots.txt

```txt
User-agent: *
Allow: /

Sitemap: https://symplifika.com/sitemap.xml
```

## ✅ Checklist Final

### Antes do Deploy

- [ ] Teste todos os formulários localmente
- [ ] Validar responsividade em diferentes dispositivos
- [ ] Verificar performance com Lighthouse
- [ ] Testar velocidade de carregamento
- [ ] Validar HTML/CSS/JS sem erros
- [ ] Configurar analytics de teste

### Após Deploy

- [ ] Verificar SSL certificate
- [ ] Testar formulário de waitlist em produção
- [ ] Confirmar eventos de analytics
- [ ] Testar em diferentes navegadores
- [ ] Configurar monitoring/alertas
- [ ] Submeter ao Google Search Console
- [ ] Compartilhar com stakeholders para feedback

### Monitoramento Contínuo

- [ ] Métricas de conversão semanais
- [ ] Performance reports mensais
- [ ] A/B tests de elementos-chave
- [ ] Feedback dos usuários
- [ ] Updates de conteúdo conforme necessário

## 🆘 Troubleshooting

### Problemas Comuns

**1. Formulário não envia:**
- Verificar CORS headers
- Validar URLs da API
- Checar console do navegador

**2. Analytics não trackeia:**
- Confirmar Tracking ID correto
- Verificar adblockers
- Testar com Google Analytics Debugger

**3. Performance lenta:**
- Otimizar imagens
- Minificar CSS/JS
- Configurar CDN
- Verificar hosting

**4. SSL/HTTPS issues:**
- Renovar certificado
- Verificar mixed content
- Atualizar URLs absolutas

### Logs Úteis

```bash
# Netlify logs
netlify dev
netlify logs

# Heroku logs
heroku logs --tail

# PM2 logs (servidor próprio)
pm2 logs symplifika-app

# Django logs
tail -f /var/log/django/symplifika.log
```

## 📞 Suporte

- **Documentação**: [/docs/landing-page/](../docs/)
- **Issues**: [GitHub Issues](https://github.com/seu-repo/issues)
- **Email**: dev@symplifika.com
- **Slack**: #symplifika-dev

---

🎯 **Objetivo**: Landing page funcionando perfeitamente em produção, capturando leads e fornecendo dados valiosos para o lançamento do Symplifika.

📊 **Métricas de Sucesso**: 
- Uptime > 99.9%
- Page Speed Score > 90
- Conversion Rate > 3%
- Zero errors críticos