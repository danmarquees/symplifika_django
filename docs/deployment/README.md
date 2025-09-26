# 🚀 Documentação de Deploy - Symplifika

Este diretório contém documentação sobre deploy, configuração de produção e infraestrutura do Symplifika.

## 📁 Arquivos Disponíveis

### 🌐 **Deploy em Produção**
- **`deploy.md`** - Guia geral de deploy e configuração
- **`RENDER_DEPLOY.md`** - Deploy específico na plataforma Render
- **`POSTGRESQL_SETUP.md`** - Configuração do PostgreSQL

## 🎯 Plataformas Suportadas

### **Render.com** ⭐ (Recomendado)
- ✅ Deploy automático via Git
- ✅ PostgreSQL gerenciado
- ✅ SSL/HTTPS automático
- ✅ Escalabilidade automática
- ✅ Logs centralizados

### **Heroku**
- ✅ Buildpacks Python
- ✅ Add-ons PostgreSQL
- ✅ Pipeline de CI/CD
- ✅ Review apps

### **DigitalOcean**
- ✅ App Platform
- ✅ Droplets customizados
- ✅ Managed Databases
- ✅ Load Balancers

### **AWS**
- ✅ Elastic Beanstalk
- ✅ ECS/Fargate
- ✅ RDS PostgreSQL
- ✅ CloudFront CDN

## 🔧 Configuração de Ambiente

### **Variáveis de Produção**
```bash
# Básicas
DEBUG=False
SECRET_KEY=sua-chave-super-secreta-aqui
ALLOWED_HOSTS=seudominio.com,www.seudominio.com

# Banco de Dados
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Integrações
GEMINI_API_KEY=sua-chave-gemini
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app

# Monitoramento
SENTRY_DSN=https://sua-dsn.ingest.sentry.io/

# Segurança
CORS_ALLOWED_ORIGINS=https://seudominio.com
CSRF_TRUSTED_ORIGINS=https://seudominio.com
```

## 📋 Checklist de Deploy

### **Pré-Deploy**
- [ ] Testes passando localmente
- [ ] Migrações criadas e testadas
- [ ] Static files coletados
- [ ] Variáveis de ambiente configuradas
- [ ] Backup do banco de dados atual

### **Deploy**
- [ ] Código enviado para repositório
- [ ] Deploy automático executado
- [ ] Migrações aplicadas
- [ ] Static files servidos
- [ ] Health check passou

### **Pós-Deploy**
- [ ] Funcionalidades críticas testadas
- [ ] Logs verificados
- [ ] Performance monitorada
- [ ] Backup pós-deploy criado
- [ ] Equipe notificada

## 🗄️ Banco de Dados

### **PostgreSQL (Produção)**
```sql
-- Configurações recomendadas
shared_preload_libraries = 'pg_stat_statements'
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
```

### **Migrações**
```bash
# Aplicar migrações
python manage.py migrate

# Verificar status
python manage.py showmigrations

# Rollback se necessário
python manage.py migrate app_name 0001
```

### **Backup e Restore**
```bash
# Backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
psql $DATABASE_URL < backup_file.sql
```

## 📊 Monitoramento

### **Sentry (Errors)**
```python
# settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
)
```

### **Logs**
```bash
# Visualizar logs (Render)
render logs --service=symplifika

# Logs locais
tail -f logs/django.log
```

### **Health Checks**
```python
# core/views.py
def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0'
    })
```

## 🔒 Segurança em Produção

### **HTTPS/SSL**
- ✅ Certificados SSL automáticos
- ✅ Redirecionamento HTTP → HTTPS
- ✅ HSTS headers
- ✅ Secure cookies

### **Headers de Segurança**
```python
# settings.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
```

### **Rate Limiting**
```python
# Configurado via django-ratelimit
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'
```

## ⚡ Performance

### **Static Files**
```python
# settings.py
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

### **Cache**
```python
# Redis cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### **Database Optimization**
```python
# Conexões de banco
DATABASES['default']['CONN_MAX_AGE'] = 600
DATABASES['default']['OPTIONS'] = {
    'MAX_CONNS': 20,
    'MIN_CONNS': 5,
}
```

## 🔄 CI/CD Pipeline

### **GitHub Actions**
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Render
        run: curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}
```

### **Render Deploy Hook**
```bash
# Configurar webhook no Render
# Settings → Deploy Hook → Copy URL
# Adicionar como secret no GitHub
```

## 🚨 Troubleshooting

### **Problemas Comuns**
1. **Static files não carregam**: Verificar `STATIC_ROOT` e `collectstatic`
2. **Database connection**: Verificar `DATABASE_URL` e conectividade
3. **CORS errors**: Configurar `CORS_ALLOWED_ORIGINS`
4. **SSL issues**: Verificar certificados e configuração HTTPS

### **Logs Úteis**
```bash
# Render logs
render logs --service=symplifika --tail

# Django debug
DEBUG=True python manage.py runserver

# Database queries
python manage.py shell
>>> from django.db import connection
>>> connection.queries
```

---

**🎯 Objetivo**: Deploy seguro, escalável e monitorado do Symplifika em produção.

**📞 Suporte**: Para problemas de deploy, consulte [troubleshooting](../troubleshooting/) ou abra uma issue.
