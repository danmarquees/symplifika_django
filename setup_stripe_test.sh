#!/bin/bash

# Script para configurar ambiente de testes do Stripe
# Uso: ./setup_stripe_test.sh

set -e

echo "🧪 Configurando ambiente de TESTES do Stripe..."
echo "=================================================="

# Verificar se o Django está instalado
if ! python -c "import django" 2>/dev/null; then
    echo "❌ Django não encontrado. Execute: pip install -r requirements.txt"
    exit 1
fi

# Verificar se as chaves do Stripe estão configuradas
if [ -z "$STRIPE_SECRET_KEY" ] || [ -z "$STRIPE_PUBLISHABLE_KEY" ]; then
    echo "⚠️  Chaves do Stripe não configuradas!"
    echo ""
    echo "📋 INSTRUÇÕES:"
    echo "1. Acesse: https://dashboard.stripe.com/test/apikeys"
    echo "2. Copie suas chaves de TESTE (pk_test_... e sk_test_...)"
    echo "3. Configure no arquivo .env:"
    echo ""
    echo "   STRIPE_PUBLISHABLE_KEY=pk_test_sua_chave_aqui"
    echo "   STRIPE_SECRET_KEY=sk_test_sua_chave_aqui"
    echo "   STRIPE_WEBHOOK_SECRET=whsec_sua_chave_aqui"
    echo ""
    echo "4. Execute novamente este script"
    exit 1
fi

# Verificar se é ambiente de teste
if [[ ! "$STRIPE_SECRET_KEY" == sk_test_* ]]; then
    echo "🚨 ATENÇÃO: Você não está usando chaves de TESTE!"
    echo "Por segurança, use apenas chaves que começam com 'sk_test_'"
    exit 1
fi

echo "✅ Chaves de teste detectadas"

# Criar produtos de teste no Stripe
echo ""
echo "📦 Criando produtos de teste no Stripe..."
python manage.py setup_stripe_test --reset

# Executar migrações
echo ""
echo "🗄️  Executando migrações..."
python manage.py migrate

# Criar superusuário para testes (opcional)
echo ""
read -p "🤔 Deseja criar um superusuário para testes? (y/N): " create_superuser
if [[ $create_superuser =~ ^[Yy]$ ]]; then
    echo "👤 Criando superusuário..."
    python manage.py createsuperuser
fi

echo ""
echo "🎯 TESTES DISPONÍVEIS:"
echo "======================"

echo ""
echo "💳 CARTÕES DE TESTE:"
echo "• Sucesso: 4242424242424242"
echo "• Falha: 4000000000000002"
echo "• 3D Secure: 4000002760003184"
echo "• CVC: qualquer 3 dígitos"
echo "• Data: qualquer data futura"

echo ""
echo "🔗 CONFIGURAR WEBHOOKS:"
echo "Método 1 - Stripe CLI (Recomendado):"
echo "  stripe listen --forward-to localhost:8000/payments/webhook/"
echo ""
echo "Método 2 - Ngrok:"
echo "  ngrok http 8000"
echo "  Configure no Stripe Dashboard com a URL HTTPS"

echo ""
echo "🚀 INICIAR TESTES:"
echo "=================="
echo "1. Configure webhooks (instruções acima)"
echo "2. Execute: python manage.py runserver"
echo "3. Acesse: http://localhost:8000"
echo "4. Faça login e teste o modal de upgrade"
echo "5. Use os cartões de teste fornecidos"

echo ""
echo "📊 MONITORAR:"
echo "• Dashboard Stripe: https://dashboard.stripe.com/test/"
echo "• Webhooks: https://dashboard.stripe.com/test/webhooks"
echo "• Logs Django: tail -f logs/django.log"

echo ""
echo "✅ Ambiente de testes configurado com sucesso!"
echo "🔑 Chave em uso: ${STRIPE_SECRET_KEY:0:12}..."

echo ""
echo "📚 Para mais informações sobre webhooks:"
echo "python manage.py setup_stripe_test --webhook-info"
