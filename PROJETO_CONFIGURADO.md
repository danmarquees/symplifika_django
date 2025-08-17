# Symplifika Django - Projeto Configurado

## 📋 Resumo do Projeto

O **Symplifika** é um sistema completo de atalhos de texto com funcionalidades avançadas de IA para expansão e melhoria de conteúdo. O projeto está totalmente configurado e funcional.

## 🏗️ Arquitetura do Sistema

### Apps Configurados

#### 1. **Core App** (`core/`)
- **Modelos**: 
  - `AppSettings`: Configurações globais da aplicação
  - `ActivityLog`: Log de atividades dos usuários
  - `SystemStats`: Estatísticas do sistema
- **Views**: Views básicas, APIs de status e saúde
- **URLs**: Rotas principais e redirecionamentos

#### 2. **Shortcuts App** (`shortcuts/`)
- **Modelos**:
  - `Category`: Categorias para organizar atalhos
  - `Shortcut`: Atalho principal com suporte a IA
  - `ShortcutUsage`: Histórico de uso dos atalhos
  - `AIEnhancementLog`: Log das expansões feitas pela IA
- **Views**: ViewSets completos com CRUD, busca, estatísticas
- **Serializers**: Serialização completa para APIs
- **Services**: `AIService` para integração com OpenAI

#### 3. **Users App** (`users/`)
- **Modelos**:
  - `UserProfile`: Perfil estendido com planos e configurações
- **Views**: Autenticação, gerenciamento de perfil, estatísticas
- **Serializers**: Serialização para usuários e perfis
- **Forms**: Formulários Django para templates HTML

## 🔧 Configurações Principais

### Banco de Dados
- **SQLite** (desenvolvimento) - configurado
- **PostgreSQL** (produção) - configuração comentada no settings

### APIs REST
- **Django REST Framework** configurado
- **Token Authentication** implementado
- **Paginação** configurada (20 itens por página)
- **CORS** configurado para frontend

### IA (OpenAI)
- **Serviço de IA** implementado (`shortcuts/services.py`)
- **Expansão de texto** automática
- **Templates de email** gerados por IA
- **Contadores de uso** por usuário

### Autenticação e Autorização
- **Sistema de usuários** Django nativo
- **Perfis estendidos** com planos (Free, Premium, Enterprise)
- **Limites por plano** configurados
- **Tokens de API** para autenticação

## 📊 Funcionalidades Implementadas

### 🔤 Sistema de Atalhos
- ✅ **CRUD completo** de atalhos
- ✅ **Categorização** com cores
- ✅ **Tipos de expansão**:
  - Texto estático
  - Expandido com IA
  - Dinâmico com variáveis
- ✅ **Contadores de uso**
- ✅ **Histórico de utilização**
- ✅ **Busca avançada** com filtros
- ✅ **Ações em lote**

### 🤖 Funcionalidades de IA
- ✅ **Expansão de texto** com OpenAI
- ✅ **Prompts customizados**
- ✅ **Geração de templates** de email
- ✅ **Sugestões automáticas** de atalhos
- ✅ **Logs de processamento** de IA
- ✅ **Controle de uso** por plano

### 👤 Gestão de Usuários
- ✅ **Registro e autenticação**
- ✅ **Perfis com configurações**
- ✅ **Sistema de planos** (Free/Premium/Enterprise)
- ✅ **Estatísticas de uso**
- ✅ **Logs de atividade**

### 📈 Analytics e Relatórios
- ✅ **Estatísticas por usuário**
- ✅ **Relatórios de uso** de atalhos
- ✅ **Métricas de IA**
- ✅ **Tempo economizado**
- ✅ **Estatísticas do sistema**

### 🔧 Administração
- ✅ **Django Admin** customizado
- ✅ **Gestão de usuários** e planos
- ✅ **Monitoramento de atalhos**
- ✅ **Logs de sistema**
- ✅ **Configurações globais**

## 🚀 Como Executar

### 1. Ativar Ambiente Virtual
```bash
cd symplifika_django
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 2. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto:
```env
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
OPENAI_API_KEY=sua-chave-openai-aqui
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 4. Executar Migrações
```bash
python manage.py migrate
```

### 5. Criar Superusuário (opcional)
```bash
python manage.py createsuperuser
```

### 6. Popular com Dados de Exemplo
```bash
python manage.py populate_sample_data --users 5 --shortcuts 25
```

### 7. Coletar Arquivos Estáticos
```bash
python manage.py collectstatic
```

### 8. Executar Servidor
```bash
python manage.py runserver
```

## 📡 Endpoints Principais

### Autenticação
- `POST /users/api/auth/login/` - Login
- `POST /users/api/auth/register/` - Registro
- `POST /users/api/auth/logout/` - Logout

### Usuários
- `GET /users/api/users/me/` - Dados do usuário logado
- `PUT /users/api/users/update-profile/` - Atualizar perfil
- `GET /users/api/users/stats/` - Estatísticas do usuário

### Atalhos
- `GET /shortcuts/api/shortcuts/` - Listar atalhos
- `POST /shortcuts/api/shortcuts/` - Criar atalho
- `POST /shortcuts/api/shortcuts/{id}/use/` - Usar atalho
- `POST /shortcuts/api/shortcuts/search/` - Buscar atalhos
- `GET /shortcuts/api/shortcuts/stats/` - Estatísticas

### Categorias
- `GET /shortcuts/api/categories/` - Listar categorias
- `POST /shortcuts/api/categories/` - Criar categoria

## 🔑 Credenciais de Teste

### Usuário Admin
- **Username**: `admin`
- **Password**: `admin123`
- **Email**: `admin@symplifika.com`

### Usuários de Exemplo
- **Username**: `joao_silva` | **Password**: `password123`
- **Username**: `maria_santos` | **Password**: `password123`
- **Username**: `pedro_oliveira` | **Password**: `password123`

## 📁 Estrutura de Arquivos

```
symplifika_django/
├── core/                    # App principal
│   ├── models.py           # Configurações e logs
│   ├── views.py            # Views básicas
│   ├── admin.py            # Admin do core
│   └── management/         # Comandos customizados
├── shortcuts/              # App de atalhos
│   ├── models.py           # Modelos de atalhos
│   ├── views.py            # ViewSets e APIs
│   ├── serializers.py      # Serializers DRF
│   ├── services.py         # Serviços de IA
│   └── admin.py            # Admin de atalhos
├── users/                  # App de usuários
│   ├── models.py           # Perfil de usuário
│   ├── views.py            # Views de usuários
│   ├── serializers.py      # Serializers de usuários
│   ├── forms.py            # Formulários Django
│   └── admin.py            # Admin de usuários
├── templates/              # Templates HTML
├── static/                 # Arquivos estáticos
├── staticfiles/            # Arquivos coletados
├── logs/                   # Logs da aplicação
└── manage.py              # Comando principal
```

## 🎯 Recursos Avançados

### Sistema de Planos
- **Free**: 50 atalhos, 100 requisições IA/mês
- **Premium**: 500 atalhos, 1000 requisições IA/mês
- **Enterprise**: Ilimitado

### Tipos de Atalhos
1. **Estático**: Texto fixo
2. **IA**: Expandido automaticamente
3. **Dinâmico**: Com variáveis substituíveis

### Integrações
- **OpenAI GPT**: Para expansão de texto
- **Django REST**: APIs completas
- **Django Admin**: Interface de administração

## 🔒 Segurança

- ✅ **CSRF Protection** habilitado
- ✅ **Token Authentication** implementado
- ✅ **Permissões por usuário**
- ✅ **Validação de dados** completa
- ✅ **Logs de atividade** para auditoria

## 📚 Documentação da API

O projeto está configurado para ser facilmente documentado com:
- **Django REST Framework Browsable API**
- **Swagger/OpenAPI** (pode ser adicionado)

## 🧪 Testes

Para executar os testes:
```bash
python manage.py test
```

## 🚀 Deploy

### Configurações para Produção
1. Alterar `DEBUG=False`
2. Configurar PostgreSQL
3. Configurar servidor web (Nginx + Gunicorn)
4. Configurar HTTPS
5. Configurar variáveis de ambiente

### Exemplo de Configuração PostgreSQL
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'symplifika_db',
        'USER': 'symplifika_user',
        'PASSWORD': 'sua_senha',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 📞 Suporte

- **Documentação**: Veja os docstrings nos arquivos de código
- **Admin Interface**: `http://localhost:8000/admin/`
- **API Browsable**: `http://localhost:8000/shortcuts/api/`

---

**✅ Projeto totalmente configurado e funcional!**

Para começar a usar, execute os comandos da seção "Como Executar" e acesse `http://localhost:8000/admin/` com as credenciais de admin para explorar o sistema.