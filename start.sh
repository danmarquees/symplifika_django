#!/bin/bash

# Symplifika - Script de Inicialização
# Este script automatiza o processo de inicialização do projeto Django

set -e  # Sair em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}"
    echo "=================================="
    echo "  $1"
    echo "=================================="
    echo -e "${NC}"
}

# Verificar se estamos no diretório correto
if [ ! -f "manage.py" ]; then
    print_error "manage.py não encontrado. Execute este script no diretório raiz do projeto."
    exit 1
fi

print_header "SYMPLIFIKA - INICIANDO SERVIDOR"

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    print_warning "Ambiente virtual não encontrado. Criando..."
    python3 -m venv venv
    print_message "Ambiente virtual criado com sucesso!"
fi

# Ativar ambiente virtual
print_message "Ativando ambiente virtual..."
source venv/bin/activate

# Verificar se requirements.txt existe e instalar dependências
if [ -f "requirements.txt" ]; then
    print_message "Instalando/atualizando dependências..."
    pip install -r requirements.txt
else
    print_warning "requirements.txt não encontrado. Instalando dependências básicas..."
    pip install django djangorestframework django-cors-headers python-decouple openai
fi

# Verificar se o arquivo .env existe
if [ ! -f ".env" ]; then
    print_warning "Arquivo .env não encontrado. Criando com valores padrão..."
    cat > .env << EOF
# Django Settings
SECRET_KEY=django-insecure-change-me-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=symplifika_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# AI/OpenAI Settings (for text expansion)
OPENAI_API_KEY=your-openai-api-key-here

# Security
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
EOF
    print_warning "Configure suas variáveis de ambiente no arquivo .env antes de usar IA!"
fi

# Criar diretórios necessários
print_message "Criando diretórios necessários..."
mkdir -p logs
mkdir -p static
mkdir -p media
mkdir -p templates

# Executar migrações
print_message "Executando migrações do banco de dados..."
python manage.py makemigrations
python manage.py migrate

# Verificar se existe algum superusuário
ADMIN_EXISTS=$(python manage.py shell -c "
from django.contrib.auth.models import User
print('yes' if User.objects.filter(is_superuser=True).exists() else 'no')
" 2>/dev/null | tail -n 1)

if [ "$ADMIN_EXISTS" = "no" ]; then
    print_message "Criando usuário administrador..."
    python manage.py create_admin --username admin --email admin@symplifika.com --password admin123
else
    print_message "Usuário administrador já existe."
fi

# Verificar se existem dados de demonstração
DEMO_EXISTS=$(python manage.py shell -c "
from django.contrib.auth.models import User
print('yes' if User.objects.filter(username='demo').exists() else 'no')
" 2>/dev/null | tail -n 1)

if [ "$DEMO_EXISTS" = "no" ]; then
    print_message "Criando dados de demonstração..."
    python manage.py setup_project --create-demo-data
else
    print_message "Dados de demonstração já existem."
fi

# Coletar arquivos estáticos (para produção)
if [ "$1" = "--production" ] || [ "$1" = "-p" ]; then
    print_message "Coletando arquivos estáticos..."
    python manage.py collectstatic --noinput
fi

print_header "SERVIDOR INICIADO COM SUCESSO"

print_message "Credenciais disponíveis:"
echo "  👤 Admin: admin / admin123"
echo "  👤 Demo: demo / demo123"
echo ""
print_message "URLs importantes:"
echo "  🌐 Aplicação: http://localhost:8000"
echo "  🔧 Admin: http://localhost:8000/admin/"
echo "  📡 API: http://localhost:8000/api/"
echo ""
print_warning "IMPORTANTE:"
echo "  - Configure sua OPENAI_API_KEY no arquivo .env para usar IA"
echo "  - Altere as senhas padrão em produção"
echo "  - Execute 'python test_api.py' para testar a API"
echo ""

# Verificar se deve iniciar o servidor automaticamente
if [ "$1" = "--run" ] || [ "$1" = "-r" ]; then
    print_message "Iniciando servidor Django..."
    python manage.py runserver
else
    print_message "Para iniciar o servidor, execute:"
    echo "  python manage.py runserver"
    echo ""
    print_message "Ou execute novamente com --run:"
    echo "  ./start.sh --run"
fi

print_message "Configuração concluída! 🚀"
