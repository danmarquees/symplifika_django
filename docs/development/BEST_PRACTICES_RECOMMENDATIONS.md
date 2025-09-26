# 🚀 RECOMENDAÇÕES DE MELHORES PRÁTICAS - SYMPLIFIKA

## 📋 VISÃO GERAL

Este documento apresenta recomendações de melhores práticas para manter o projeto Symplifika limpo, escalável e maintível após a limpeza realizada.

## 🏗️ ARQUITETURA E ESTRUTURA

### 1. Organização de Apps Django
```
✅ FAZER:
- Manter apps com responsabilidades bem definidas
- Usar nomes descritivos para apps e models
- Seguir o princípio Single Responsibility

❌ EVITAR:
- Apps muito grandes com múltiplas responsabilidades
- Dependências circulares entre apps
- Models em apps errados
```

### 2. Estrutura de Diretórios
```
Recomendado:
symplifika_django/
├── apps/                 # Apps do projeto
│   ├── core/
│   ├── shortcuts/
│   └── users/
├── config/              # Configurações
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   └── urls.py
├── static/
├── templates/
└── requirements/
    ├── base.txt
    ├── local.txt
    └── production.txt
```

## 🔧 CONFIGURAÇÕES

### 1. Settings Modulares
```python
# config/settings/base.py - Configurações comuns
# config/settings/local.py - Desenvolvimento
# config/settings/production.py - Produção
```

### 2. Variáveis de Ambiente
```python
✅ USAR:
- python-decouple para todas as variáveis sensíveis
- Valores padrão seguros
- Documentação das variáveis necessárias

❌ EVITAR:
- Hardcoding de valores sensíveis
- Configurações diferentes sem documentação
```

## 📝 CÓDIGO LIMPO

### 1. Views
```python
✅ BOAS PRÁTICAS:
- Usar Class-Based Views quando apropriado
- Manter views simples e focadas
- Separar lógica de negócio em services
- Usar decorators para funcionalidades comuns

# Exemplo:
class ShortcutListView(LoginRequiredMixin, ListView):
    model = Shortcut
    template_name = 'shortcuts/list.html'
    paginate_by = 20
    
    def get_queryset(self):
        return self.request.user.shortcuts.filter(is_active=True)
```

### 2. Models
```python
✅ BOAS PRÁTICAS:
- Usar verbose_name e help_text
- Implementar __str__ methods
- Usar Meta classes adequadamente
- Criar métodos de conveniência

class Shortcut(models.Model):
    title = models.CharField(
        max_length=200, 
        verbose_name="Título",
        help_text="Título descritivo do atalho"
    )
    
    class Meta:
        verbose_name = "Atalho"
        verbose_name_plural = "Atalhos"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.trigger} - {self.title}"
```

### 3. Serializers (DRF)
```python
✅ BOAS PRÁTICAS:
- Validações customizadas quando necessário
- Usar SerializerMethodField para campos calculados
- Separar serializers de leitura e escrita

class ShortcutSerializer(serializers.ModelSerializer):
    use_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Shortcut
        fields = ['id', 'title', 'trigger', 'content', 'use_count']
        read_only_fields = ['id', 'use_count']
    
    def validate_trigger(self, value):
        if not value.startswith('//'):
            raise serializers.ValidationError(
                "Trigger deve começar com '//'."
            )
        return value
```

## 🎨 FRONTEND

### 1. Templates Django
```html
✅ BOAS PRÁTICAS:
- Usar template inheritance adequadamente
- Criar includes para componentes reutilizáveis
- Usar template tags customizadas quando necessário

<!-- base.html -->
{% load static custom_tags %}

<!DOCTYPE html>
<html lang="pt-br">
<head>
    <title>{% block title %}Symplifika{% endblock %}</title>
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% include 'includes/navbar.html' %}
    {% block content %}{% endblock %}
    {% include 'includes/footer.html' %}
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### 2. CSS/JavaScript
```css
✅ BOAS PRÁTICAS:
- Usar metodologia BEM ou similar
- Componentes CSS reutilizáveis
- Media queries mobile-first
- Variáveis CSS para consistência

:root {
    --primary-color: #007bff;
    --secondary-color: #6c757d;
    --success-color: #28a745;
    --danger-color: #dc3545;
}

.btn {
    padding: 0.5rem 1rem;
    border-radius: 0.25rem;
    border: none;
    cursor: pointer;
    transition: all 0.2s ease;
}

.btn--primary {
    background-color: var(--primary-color);
    color: white;
}
```

## 🔒 SEGURANÇA

### 1. Autenticação e Autorização
```python
✅ IMPLEMENTAR:
- Rate limiting em APIs sensíveis
- Validação robusta de inputs
- Sanitização de dados
- CSRF protection em forms

from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers

@cache_page(60 * 15)  # Cache por 15 minutos
@vary_on_headers('User-Agent')
def api_view(request):
    # Implementation
    pass
```

### 2. Dados Sensíveis
```python
✅ PROTEGER:
- Senhas sempre hasheadas
- Tokens de API seguros
- Logs sem informações sensíveis
- Backup de dados criptografados

# settings/base.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {name}: {message}',
            'style': '{',
        },
    },
    'filters': {
        'remove_sensitive_data': {
            '()': 'apps.core.filters.SensitiveDataFilter',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
            'formatter': 'verbose',
            'filters': ['remove_sensitive_data'],
        },
    },
}
```

## 🧪 TESTES

### 1. Estrutura de Testes
```python
✅ ORGANIZAÇÃO:
tests/
├── unit/
│   ├── test_models.py
│   ├── test_views.py
│   └── test_services.py
├── integration/
│   ├── test_api.py
│   └── test_workflows.py
└── fixtures/
    └── test_data.json

# Exemplo de teste
class ShortcutModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_shortcut_creation(self):
        shortcut = Shortcut.objects.create(
            user=self.user,
            title='Test Shortcut',
            trigger='//test',
            content='Test content'
        )
        
        self.assertEqual(shortcut.use_count, 0)
        self.assertTrue(shortcut.is_active)
        self.assertIn('//test', str(shortcut))
```

### 2. Cobertura de Testes
```bash
# Configurar coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html

# Meta: >80% de cobertura
```

## 🚀 PERFORMANCE

### 1. Otimizações de Database
```python
✅ USAR:
- select_related() e prefetch_related()
- Índices em campos frequentemente consultados
- Pagination em listas grandes

# models.py
class Meta:
    indexes = [
        models.Index(fields=['user', '-created_at']),
        models.Index(fields=['trigger']),
    ]

# views.py
def get_queryset(self):
    return Shortcut.objects.select_related('user', 'category')\
                          .prefetch_related('usage_history')\
                          .filter(is_active=True)
```

### 2. Cache
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# views.py
from django.core.cache import cache

def expensive_function():
    result = cache.get('expensive_key')
    if result is None:
        result = perform_expensive_calculation()
        cache.set('expensive_key', result, 300)  # 5 minutos
    return result
```

## 📊 MONITORAMENTO

### 1. Logging Estruturado
```python
import logging
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_logger_name,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.ConsoleRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    logger_factory=structlog.PrintLoggerFactory(),
    context_class=dict,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

def create_shortcut(request):
    logger.info(
        "shortcut_created",
        user_id=request.user.id,
        trigger=shortcut.trigger,
        extra_context={"ip": get_client_ip(request)}
    )
```

### 2. Health Checks
```python
# urls.py
urlpatterns = [
    path('health/', health_check_view, name='health-check'),
    path('health/db/', database_health_check, name='db-health'),
]

# views.py
def health_check_view(request):
    checks = {
        'database': check_database(),
        'cache': check_cache(),
        'external_apis': check_external_apis(),
    }
    
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    
    return JsonResponse({
        'status': 'healthy' if all_healthy else 'unhealthy',
        'checks': checks,
        'timestamp': timezone.now().isoformat()
    }, status=status_code)
```

## 🔄 DEPLOY E CI/CD

### 1. Docker
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/production.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
```

### 2. GitHub Actions
```yaml
# .github/workflows/django.yml
name: Django CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        pip install -r requirements/local.txt
    
    - name: Run tests
      run: |
        python manage.py test
    
    - name: Run linting
      run: |
        flake8 .
        black --check .
```

## 📚 DOCUMENTAÇÃO

### 1. README Estruturado
```markdown
# 📖 Symplifika

## 🚀 Setup Rápido
## 🏗️ Arquitetura
## 🔧 Configuração
## 🧪 Testes
## 📝 API Documentation
## 🚀 Deploy
## 🤝 Contribuição
```

### 2. API Documentation
```python
# Use Django REST Framework schema generation
# Install: pip install drf-yasg

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Symplifika API",
        default_version='v1',
        description="API para gerenciamento de atalhos e automações",
    ),
    public=True,
)

# urls.py
urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger')),
    path('redoc/', schema_view.with_ui('redoc')),
]
```

## ✅ CHECKLIST DE QUALIDADE

Antes de cada release, verifique:

- [ ] Todos os testes passando
- [ ] Cobertura de testes > 80%
- [ ] Linting sem erros (flake8, black)
- [ ] Documentação atualizada
- [ ] Migrações aplicadas
- [ ] Variáveis de ambiente documentadas
- [ ] Health checks funcionando
- [ ] Performance testada
- [ ] Logs estruturados
- [ ] Backup de dados configurado

---

**Lembre-se:** A qualidade do código é uma responsabilidade de toda a equipe. Estas práticas devem ser seguidas consistentemente para manter o projeto saudável e escalável.