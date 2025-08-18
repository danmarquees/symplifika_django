# Symplifika - Sistema de Atalhos de Texto Inteligente

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Django](https://img.shields.io/badge/django-5.2.5-green.svg)
![Frontend](https://img.shields.io/badge/frontend-integrated-success.svg)
![Status](https://img.shields.io/badge/status-complete-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🎉 INTEGRAÇÃO DJANGO-FRONTEND CONCLUÍDA!

✅ **Status do Projeto:** COMPLETO E FUNCIONAL  
🌐 **Interface Web:** Totalmente integrada  
📱 **Design:** Responsivo com tema claro/escuro  
🔗 **API:** RESTful completamente funcional  
🚀 **Deploy:** Pronto para produção

## 📋 Sobre o Projeto

A **Symplifika** é uma aplicação web moderna e completa, projetada para aumentar a produtividade através da gestão inteligente de atalhos de texto. O objetivo principal é eliminar a necessidade de digitar repetidamente frases, parágrafos ou blocos de código, permitindo que o usuário crie "gatilhos" (ex: `//email-boasvindas`) que se expandem automaticamente para um texto completo com ajuda de IA.

## ✨ Funcionalidades Principais

### 🚀 Core Features
- **Atalhos Personalizados**: Crie gatilhos únicos que se expandem para textos completos
- **Expansão com IA**: Use Google Gemini para expandir e melhorar automaticamente seus textos
- **Variáveis Dinâmicas**: Suporte a placeholders que podem ser substituídos dinamicamente
- **Categorização**: Organize seus atalhos em categorias personalizadas
- **Busca Avançada**: Encontre rapidamente qualquer atalho usando filtros inteligentes

### 📊 Analytics & Gestão
- **Estatísticas de Uso**: Acompanhe quais atalhos são mais utilizados
- **Histórico Completo**: Veja quando e onde cada atalho foi usado
- **Dashboard Intuitivo**: Visualize sua produtividade em tempo real
- **Tempo Economizado**: Calcule quantas horas você economizou

### 🔐 Planos e Limites
- **Plano Gratuito**: 50 atalhos, 100 expansões de IA por mês
- **Plano Premium**: 500 atalhos, 1000 expansões de IA por mês
- **Plano Enterprise**: Atalhos ilimitados, 10000 expansões de IA por mês

## 🛠️ Tecnologias Utilizadas

### Backend
- **Django 5.2.5**: Framework web principal
- **Django REST Framework**: API RESTful
- **SQLite/PostgreSQL**: Banco de dados
- **Google Gemini API**: Integração com inteligência artificial

### Bibliotecas Principais
- **python-decouple**: Gerenciamento de configurações
- **django-cors-headers**: Suporte a CORS para frontend
- **pydantic**: Validação de dados

## 🌐 Interface Web Integrada

### 🎨 Frontend Moderno
- **Interface responsiva** com Tailwind CSS
- **Tema claro/escuro** automático
- **Componentes interativos** (modais, toasts, formulários)
- **Navegação fluida** entre páginas
- **Animações suaves** e feedback visual

### 📱 Páginas Disponíveis
- **🔐 Login/Registro** - Autenticação segura
- **📝 Dashboard** - Gestão de atalhos
- **📂 Categorias** - Organização com cores
- **⚙️ Configurações** - Personalização e dados
- **🔧 Admin** - Painel administrativo Django

### 🔗 URLs do Sistema
- **Interface Web:** http://localhost:8000
- **Admin Django:** http://localhost:8000/admin
- **API REST:** http://localhost:8000/api

## 📦 Instalação e Configuração

### Pré-requisitos
- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)
- Git

### 1. Clone o Repositório
```bash
git clone <url-do-repositorio>
cd symplifika_dango
```

### 2. Crie o Ambiente Virtual
```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Instale as Dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as Variáveis de Ambiente
Copie o arquivo `.env` e configure suas variáveis:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:
```env
# Django Settings
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite por padrão)
DB_NAME=symplifika_db
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Google Gemini API (obrigatório para funcionalidades de IA)
GEMINI_API_KEY=sua-chave-gemini-aqui

# Security
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 5. Execute as Migrações
```bash
python manage.py migrate
```

### 6. Setup Inicial do Projeto
```bash
# Criar superusuário e dados de demonstração
python manage.py setup_project --create-superuser --create-demo-data

# Ou apenas o superusuário
python manage.py setup_project --create-superuser --admin-username admin --admin-email admin@symplifika.com
```

### 7. Execute o Servidor
```bash
python manage.py runserver
```

Acesse: `http://localhost:8000`

## 🎯 Uso da Aplicação

### Autenticação
- **Registro**: `POST /users/auth/register/`
- **Login**: `POST /users/auth/login/`
- **Logout**: `POST /users/auth/logout/`

### Gerenciamento de Atalhos
- **Listar**: `GET /shortcuts/api/shortcuts/`
- **Criar**: `POST /shortcuts/api/shortcuts/`
- **Usar Atalho**: `POST /shortcuts/api/shortcuts/{id}/use/`
- **Buscar**: `POST /shortcuts/api/shortcuts/search/`

### Exemplos de Uso

#### Criar um Atalho Simples
```json
{
  "trigger": "//assinatura",
  "title": "Minha Assinatura",
  "content": "Atenciosamente,\nJoão Silva\nDesenvolvedor",
  "expansion_type": "static"
}
```

#### Criar um Atalho com Variáveis
```json
{
  "trigger": "//email-cliente",
  "title": "Email para Cliente",
  "content": "Olá {nome},\n\nObrigado por escolher a {empresa}!",
  "expansion_type": "dynamic",
  "variables": {
    "nome": "Cliente",
    "empresa": "Minha Empresa"
  }
}
```

#### Criar um Atalho com IA
```json
{
  "trigger": "//proposta",
  "title": "Proposta Comercial",
  "content": "Proposta para desenvolvimento de sistema.",
  "expansion_type": "ai_enhanced",
  "ai_prompt": "Expanda em uma proposta comercial completa e profissional"
}
```

## 📚 Estrutura da API

### Endpoints Principais

#### Autenticação
- `POST /users/auth/register/` - Registrar usuário
- `POST /users/auth/login/` - Fazer login
- `POST /users/auth/logout/` - Fazer logout

#### Usuários
- `GET /users/api/users/me/` - Dados do usuário logado
- `PUT /users/api/users/update-profile/` - Atualizar perfil
- `GET /users/api/users/stats/` - Estatísticas do usuário
- `GET /users/dashboard/` - Dados do dashboard

#### Atalhos
- `GET /shortcuts/api/shortcuts/` - Listar atalhos
- `POST /shortcuts/api/shortcuts/` - Criar atalho
- `PUT /shortcuts/api/shortcuts/{id}/` - Atualizar atalho
- `DELETE /shortcuts/api/shortcuts/{id}/` - Deletar atalho
- `POST /shortcuts/api/shortcuts/{id}/use/` - Usar atalho
- `POST /shortcuts/api/shortcuts/search/` - Buscar atalhos
- `GET /shortcuts/api/shortcuts/stats/` - Estatísticas dos atalhos

#### Categorias
- `GET /shortcuts/api/categories/` - Listar categorias
- `POST /shortcuts/api/categories/` - Criar categoria
- `GET /shortcuts/api/categories/{id}/shortcuts/` - Atalhos da categoria

## 🔧 Administração

### Painel Admin
Acesse: `http://localhost:8000/admin/`

### Comandos de Gerenciamento

#### Setup do Projeto
```bash
# Setup completo
python manage.py setup_project --create-superuser --create-demo-data

# Apenas superusuário
python manage.py setup_project --create-superuser
```

#### Gerenciamento de Usuários
```bash
# Criar superusuário manualmente
python manage.py createsuperuser

# Resetar contadores mensais de IA
python manage.py shell -c "
from users.models import UserProfile
for profile in UserProfile.objects.all():
    profile.reset_monthly_counters()
"
```

## 🎨 Modelos de Dados

### Principais Entidades

#### Shortcut (Atalho)
- `trigger`: Gatilho único (ex: //email-boasvindas)
- `title`: Título descritivo
- `content`: Conteúdo original
- `expanded_content`: Conteúdo expandido pela IA
- `expansion_type`: Tipo de expansão (static, dynamic, ai_enhanced)
- `variables`: Variáveis dinâmicas (JSON)
- `use_count`: Contador de uso
- `category`: Categoria do atalho

#### UserProfile (Perfil do Usuário)
- `plan`: Plano do usuário (free, premium, enterprise)
- `max_shortcuts`: Limite de atalhos
- `ai_requests_used`: Requisições de IA usadas no mês
- `max_ai_requests`: Limite de requisições de IA
- `theme`: Tema da interface

#### Category (Categoria)
- `name`: Nome da categoria
- `description`: Descrição
- `color`: Cor da categoria
- `user`: Usuário proprietário

## 🔒 Segurança

### Autenticação
- Token-based authentication
- Session authentication para admin
- Proteção CSRF

### Permissões
- Usuários só acessam seus próprios dados
- Validação de ownership em todas as operações
- Rate limiting implícito via planos

### Boas Práticas
- Senhas hasheadas
- Validação de entrada em todos os endpoints
- Logs de segurança
- Variáveis de ambiente para credenciais

## 📈 Monitoramento e Logs

### Logs do Sistema
Os logs são salvos em `logs/django.log` e incluem:
- Requisições à API
- Erros de sistema
- Uso de IA
- Ações administrativas

### Métricas Disponíveis
- Uso de atalhos por usuário
- Performance das expansões de IA
- Estatísticas de crescimento
- Tempo economizado pelos usuários

## 🧪 Testes

```bash
# Executar todos os testes
python manage.py test

# Testes de uma app específica
python manage.py test shortcuts

# Testes com coverage
pip install coverage
coverage run manage.py test
coverage report
```

## 🚀 Deploy

### Preparação para Produção

1. **Configure as variáveis de ambiente de produção**
2. **Use PostgreSQL ao invés de SQLite**
3. **Configure um servidor web (Nginx + Gunicorn)**
4. **Setup de SSL/HTTPS**
5. **Configure backup automático do banco**

### Exemplo com Gunicorn
```bash
pip install gunicorn
gunicorn symplifika.wsgi:application --bind 0.0.0.0:8000
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📞 Suporte

- **Email**: suporte@symplifika.com
- **Issues**: Use as issues do GitHub para reportar bugs
- **Documentação**: Wiki do projeto no GitHub

## 🎯 Roadmap

### Próximas Versões

#### v1.1
- [ ] Sistema de templates compartilhados
- [ ] Export/Import de atalhos
- [ ] API webhooks para integrações

#### v1.2
- [ ] Aplicativo mobile (React Native)
- [ ] Plugin para navegadores
- [ ] Integração com Slack/Discord

#### v1.3
- [ ] IA própria treinada
- [ ] Suporte a múltiplos idiomas
- [ ] Analytics avançados

---

**Desenvolvido com ❤️ pela equipe Symplifika**