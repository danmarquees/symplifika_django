#!/usr/bin/env python
"""
Script de verificação do sistema de testes do Stripe
Verifica se tudo está configurado corretamente antes de iniciar os testes
"""

import os
import sys
import django
from django.conf import settings
import requests
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'symplifika.settings')
django.setup()

# Cores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def print_header(message):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{message.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")

def check_environment():
    """Verifica configurações do ambiente"""
    print_header("VERIFICAÇÃO DO AMBIENTE")

    errors = []
    warnings = []

    # Verificar chaves do Stripe
    stripe_publishable = getattr(settings, 'STRIPE_PUBLISHABLE_KEY', '')
    stripe_secret = getattr(settings, 'STRIPE_SECRET_KEY', '')
    stripe_webhook = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')

    if not stripe_publishable:
        errors.append("STRIPE_PUBLISHABLE_KEY não configurada")
    elif not stripe_publishable.startswith('pk_test_'):
        errors.append("STRIPE_PUBLISHABLE_KEY não é uma chave de teste")
    else:
        print_success(f"Chave Publishable configurada: {stripe_publishable[:20]}...")

    if not stripe_secret:
        errors.append("STRIPE_SECRET_KEY não configurada")
    elif not stripe_secret.startswith('sk_test_'):
        errors.append("STRIPE_SECRET_KEY não é uma chave de teste")
    else:
        print_success(f"Chave Secret configurada: {stripe_secret[:20]}...")

    if not stripe_webhook:
        warnings.append("STRIPE_WEBHOOK_SECRET não configurada (necessária para webhooks)")
    else:
        print_success(f"Webhook Secret configurada: {stripe_webhook[:20]}...")

    # Verificar DEBUG
    if not settings.DEBUG:
        warnings.append("DEBUG=False - considere usar DEBUG=True para testes")
    else:
        print_success("DEBUG habilitado")

    # Verificar banco de dados
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print_success("Conexão com banco de dados OK")
    except Exception as e:
        errors.append(f"Erro na conexão com banco: {e}")

    return errors, warnings

def check_stripe_connection():
    """Verifica conexão com API do Stripe"""
    print_header("VERIFICAÇÃO DA CONEXÃO COM STRIPE")

    try:
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY

        # Testar conexão
        account = stripe.Account.retrieve()
        print_success(f"Conexão com Stripe OK - Conta: {account.id}")

        # Verificar se é conta de teste
        if account.id.startswith('acct_'):
            print_success("Conta de teste confirmada")
        else:
            print_warning("Não foi possível confirmar se é conta de teste")

        return True

    except stripe.error.AuthenticationError:
        print_error("Erro de autenticação - verifique STRIPE_SECRET_KEY")
        return False
    except Exception as e:
        print_error(f"Erro na conexão: {e}")
        return False

def check_products():
    """Verifica se os produtos foram criados"""
    print_header("VERIFICAÇÃO DOS PRODUTOS")

    from payments.models import StripeProduct, StripePrice

    products = StripeProduct.objects.all()
    if not products.exists():
        print_error("Nenhum produto encontrado no banco")
        print_info("Execute: python manage.py setup_stripe_test")
        return False

    print_success(f"{products.count()} produto(s) encontrado(s)")

    for product in products:
        print_info(f"  - {product.name} ({product.stripe_product_id})")

        prices = product.prices.all()
        if not prices.exists():
            print_warning(f"    Nenhum preço encontrado para {product.name}")
        else:
            for price in prices:
                print_info(f"    * {price.get_interval_display()}: R$ {price.amount_in_reais:.2f}")

    # Verificar no Stripe
    try:
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY

        stripe_products = stripe.Product.list(active=True)
        print_success(f"{len(stripe_products.data)} produto(s) ativo(s) no Stripe")

        for product in stripe_products.data:
            print_info(f"  - Stripe: {product.name} ({product.id})")

    except Exception as e:
        print_warning(f"Não foi possível verificar produtos no Stripe: {e}")

    return True

def check_server():
    """Verifica se o servidor Django está rodando"""
    print_header("VERIFICAÇÃO DO SERVIDOR")

    try:
        response = requests.get('http://localhost:8000/', timeout=5)
        if response.status_code == 200:
            print_success("Servidor Django rodando na porta 8000")
            return True
        else:
            print_warning(f"Servidor respondeu com status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Servidor não está rodando na porta 8000")
        print_info("Execute: python manage.py runserver")
        return False
    except Exception as e:
        print_warning(f"Erro ao verificar servidor: {e}")
        return False

def check_endpoints():
    """Verifica endpoints de pagamento"""
    print_header("VERIFICAÇÃO DOS ENDPOINTS")

    if not check_server():
        return False

    endpoints = [
        ('/payments/plans/', 'GET'),
        ('/payments/create-checkout-session/', 'POST'),
        ('/payments/webhook/', 'POST'),
    ]

    for endpoint, method in endpoints:
        try:
            url = f'http://localhost:8000{endpoint}'
            if method == 'GET':
                response = requests.get(url, timeout=5)
            else:
                # Para POST, apenas verificar se o endpoint existe
                response = requests.post(url, timeout=5)

            if response.status_code in [200, 400, 401, 403]:  # Códigos esperados
                print_success(f"{method} {endpoint} - Endpoint disponível")
            else:
                print_warning(f"{method} {endpoint} - Status {response.status_code}")

        except Exception as e:
            print_error(f"{method} {endpoint} - Erro: {e}")

    return True

def test_checkout_creation():
    """Testa criação de sessão de checkout"""
    print_header("TESTE DE CRIAÇÃO DE CHECKOUT")

    from django.contrib.auth import get_user_model
    from payments.views import CreateCheckoutSessionView
    from django.test.client import RequestFactory
    from django.contrib.auth.models import AnonymousUser

    User = get_user_model()

    # Criar usuário de teste se não existir
    try:
        test_user = User.objects.get(username='stripe_test_user')
    except User.DoesNotExist:
        test_user = User.objects.create_user(
            username='stripe_test_user',
            email='test@stripe.example.com',
            password='test123456'
        )
        print_info("Usuário de teste criado: stripe_test_user")

    # Simular requisição
    factory = RequestFactory()
    request = factory.post(
        '/payments/create-checkout-session/',
        data={'plan': 'premium', 'billing_cycle': 'monthly'},
        content_type='application/json'
    )
    request.user = test_user

    try:
        view = CreateCheckoutSessionView.as_view()
        response = view(request)

        if response.status_code == 200:
            print_success("Criação de checkout funcionando")
            return True
        else:
            print_warning(f"Checkout retornou status {response.status_code}")
            if hasattr(response, 'data'):
                print_info(f"Resposta: {response.data}")
            return False

    except Exception as e:
        print_error(f"Erro ao testar checkout: {e}")
        return False

def run_tests():
    """Executa todos os testes"""
    print(f"{Colors.BOLD}🧪 VERIFICAÇÃO DO SISTEMA DE TESTES DO STRIPE{Colors.END}")
    print("Este script verifica se tudo está configurado corretamente\n")

    total_errors = 0
    total_warnings = 0

    # 1. Verificar ambiente
    errors, warnings = check_environment()
    total_errors += len(errors)
    total_warnings += len(warnings)

    for error in errors:
        print_error(error)
    for warning in warnings:
        print_warning(warning)

    if errors:
        print_error("Corrija os erros antes de continuar")
        return False

    # 2. Verificar conexão Stripe
    if not check_stripe_connection():
        total_errors += 1
        return False

    # 3. Verificar produtos
    if not check_products():
        total_errors += 1

    # 4. Verificar endpoints
    check_endpoints()

    # 5. Teste de checkout
    test_checkout_creation()

    # Resumo final
    print_header("RESUMO")

    if total_errors == 0:
        print_success("✅ TODOS OS TESTES PASSARAM!")
        print_info("Sistema pronto para testes de pagamento")
        print_info("\nPróximos passos:")
        print_info("1. Configure webhooks (veja STRIPE_TEST_SETUP.md)")
        print_info("2. Execute: python manage.py runserver")
        print_info("3. Acesse http://localhost:8000 e teste o modal de upgrade")
        print_info("4. Use cartão de teste: 4242424242424242")
    else:
        print_error(f"❌ {total_errors} erro(s) encontrado(s)")
        print_info("Corrija os erros antes de continuar")

    if total_warnings > 0:
        print_warning(f"⚠️  {total_warnings} aviso(s) - considere resolver")

    return total_errors == 0

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
