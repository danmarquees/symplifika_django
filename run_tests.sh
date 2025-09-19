#!/bin/bash

# Script para testar o ambiente Django e executar o servidor

echo "🔧 Verificando ambiente Django..."

# Ativar ambiente virtual se existir
if [ -d "venv" ]; then
    echo "📦 Ativando ambiente virtual..."
    source venv/bin/activate
fi

# Verificar se Django está instalado
python -c "import django; print(f'✅ Django {django.get_version()} encontrado')" 2>/dev/null || {
    echo "❌ Django não encontrado. Instalando..."
    pip install django
}

# Verificar configurações do Django
echo "🔍 Verificando configurações..."
python manage.py check --deploy 2>/dev/null || python manage.py check

# Executar migrações se necessário
echo "🗄️ Aplicando migrações..."
python manage.py migrate

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Testar templates
echo "🧪 Testando templates..."
python test_templates.py

# Iniciar servidor
echo "🚀 Iniciando servidor de desenvolvimento..."
echo "📱 Acesse: http://localhost:8000"
python manage.py runserver 0.0.0.0:8000
