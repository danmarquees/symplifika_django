from django.core.management.base import BaseCommand
from django.conf import settings
import stripe
from payments.models import StripeProduct, StripePrice
import os

stripe.api_key = settings.STRIPE_SECRET_KEY


class Command(BaseCommand):
    help = 'Configura ambiente de testes do Stripe com produtos e preços para sandbox'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Remove todos os produtos existentes antes de criar novos',
        )
        parser.add_argument(
            '--webhook-info',
            action='store_true',
            help='Exibe informações sobre configuração de webhooks',
        )

    def handle(self, *args, **options):
        # Verificar se estamos usando chaves de teste
        if not settings.STRIPE_SECRET_KEY.startswith('sk_test_'):
            self.stdout.write(
                self.style.ERROR(
                    'ATENÇÃO: Você não está usando uma chave de teste do Stripe!\n'
                    'Por segurança, este comando só funciona com chaves que começam com "sk_test_"'
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS('🧪 Configurando ambiente de TESTES do Stripe...\n')
        )

        if options['webhook_info']:
            self.show_webhook_info()
            return

        if options['reset']:
            self.reset_products()

        self.create_test_products()
        self.show_test_cards()
        self.show_next_steps()

    def reset_products(self):
        """Remove produtos existentes"""
        self.stdout.write('🗑️ Removendo produtos existentes...')

        # Remover do banco local
        deleted_count = StripeProduct.objects.count()
        StripeProduct.objects.all().delete()

        self.stdout.write(f'   Removidos {deleted_count} produtos do banco local')

    def create_test_products(self):
        """Cria produtos e preços de teste"""
        self.stdout.write('📦 Criando produtos de teste...\n')

        # Produto Premium
        try:
            premium_product = stripe.Product.create(
                name='Premium (TESTE)',
                description='Plano Premium - Ambiente de Testes',
                metadata={
                    'environment': 'test',
                    'plan_type': 'premium',
                    'max_shortcuts': '500',
                    'max_ai_requests': '1000'
                }
            )

            # Preços Premium
            premium_monthly = stripe.Price.create(
                product=premium_product.id,
                unit_amount=2990,  # R$ 29,90
                currency='brl',
                recurring={'interval': 'month'},
                metadata={'plan_type': 'premium', 'billing_cycle': 'monthly'}
            )

            premium_yearly = stripe.Price.create(
                product=premium_product.id,
                unit_amount=29900,  # R$ 299,00
                currency='brl',
                recurring={'interval': 'year'},
                metadata={'plan_type': 'premium', 'billing_cycle': 'yearly'}
            )

            # Salvar no banco
            product_obj, created = StripeProduct.objects.get_or_create(
                stripe_product_id=premium_product.id,
                defaults={
                    'name': 'Premium',
                    'description': 'Plano Premium - Ambiente de Testes'
                }
            )

            StripePrice.objects.get_or_create(
                stripe_price_id=premium_monthly.id,
                defaults={
                    'product': product_obj,
                    'unit_amount': 2990,
                    'currency': 'brl',
                    'interval': 'month'
                }
            )

            StripePrice.objects.get_or_create(
                stripe_price_id=premium_yearly.id,
                defaults={
                    'product': product_obj,
                    'unit_amount': 29900,
                    'currency': 'brl',
                    'interval': 'year'
                }
            )

            self.stdout.write(
                self.style.SUCCESS(f'✅ Premium criado: {premium_product.id}')
            )

        except stripe.error.StripeError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao criar Premium: {e}')
            )

        # Produto Enterprise
        try:
            enterprise_product = stripe.Product.create(
                name='Enterprise (TESTE)',
                description='Plano Enterprise - Ambiente de Testes',
                metadata={
                    'environment': 'test',
                    'plan_type': 'enterprise',
                    'max_shortcuts': 'unlimited',
                    'max_ai_requests': '10000'
                }
            )

            # Preços Enterprise
            enterprise_monthly = stripe.Price.create(
                product=enterprise_product.id,
                unit_amount=9990,  # R$ 99,90
                currency='brl',
                recurring={'interval': 'month'},
                metadata={'plan_type': 'enterprise', 'billing_cycle': 'monthly'}
            )

            enterprise_yearly = stripe.Price.create(
                product=enterprise_product.id,
                unit_amount=99900,  # R$ 999,00
                currency='brl',
                recurring={'interval': 'year'},
                metadata={'plan_type': 'enterprise', 'billing_cycle': 'yearly'}
            )

            # Salvar no banco
            product_obj, created = StripeProduct.objects.get_or_create(
                stripe_product_id=enterprise_product.id,
                defaults={
                    'name': 'Enterprise',
                    'description': 'Plano Enterprise - Ambiente de Testes'
                }
            )

            StripePrice.objects.get_or_create(
                stripe_price_id=enterprise_monthly.id,
                defaults={
                    'product': product_obj,
                    'unit_amount': 9990,
                    'currency': 'brl',
                    'interval': 'month'
                }
            )

            StripePrice.objects.get_or_create(
                stripe_price_id=enterprise_yearly.id,
                defaults={
                    'product': product_obj,
                    'unit_amount': 99900,
                    'currency': 'brl',
                    'interval': 'year'
                }
            )

            self.stdout.write(
                self.style.SUCCESS(f'✅ Enterprise criado: {enterprise_product.id}')
            )

        except stripe.error.StripeError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao criar Enterprise: {e}')
            )

    def show_test_cards(self):
        """Exibe cartões de teste disponíveis"""
        self.stdout.write('\n💳 CARTÕES DE TESTE DISPONÍVEIS:')
        self.stdout.write('=' * 50)

        cards = [
            ('4242424242424242', 'Sucesso (Visa)', 'Pagamento aprovado'),
            ('4000000000000002', 'Falha Genérica', 'Cartão recusado'),
            ('4000000000009995', 'Fundos Insuficientes', 'Saldo insuficiente'),
            ('4000002760003184', '3D Secure', 'Requer autenticação'),
            ('4000000000000069', 'Expirado', 'Cartão expirado'),
            ('4000000000000127', 'CVC Incorreto', 'Código de segurança inválido'),
            ('5555555555554444', 'Sucesso (Mastercard)', 'Pagamento aprovado'),
        ]

        for card, name, description in cards:
            self.stdout.write(f'📋 {card} - {name}')
            self.stdout.write(f'   {description}')
            self.stdout.write('')

        self.stdout.write('ℹ️  Dados adicionais para qualquer cartão:')
        self.stdout.write('   CVC: Qualquer 3 dígitos (ex: 123)')
        self.stdout.write('   Data: Qualquer data futura (ex: 12/30)')
        self.stdout.write('   Nome: Qualquer nome')

    def show_webhook_info(self):
        """Exibe informações sobre configuração de webhooks"""
        self.stdout.write('\n🔗 CONFIGURAÇÃO DE WEBHOOKS PARA TESTES:')
        self.stdout.write('=' * 60)

        self.stdout.write('\n1️⃣ MÉTODO 1 - Stripe CLI (Recomendado):')
        self.stdout.write('   • Instale: https://stripe.com/docs/stripe-cli')
        self.stdout.write('   • Login: stripe login')
        self.stdout.write('   • Forward: stripe listen --forward-to localhost:8000/payments/webhook/')
        self.stdout.write('   • Copie o webhook secret exibido')

        self.stdout.write('\n2️⃣ MÉTODO 2 - Ngrok:')
        self.stdout.write('   • Instale ngrok: https://ngrok.com/')
        self.stdout.write('   • Execute: ngrok http 8000')
        self.stdout.write('   • Use a URL HTTPS no Stripe Dashboard')
        self.stdout.write('   • Endpoint: https://sua-url.ngrok.io/payments/webhook/')

        self.stdout.write('\n3️⃣ EVENTOS NECESSÁRIOS:')
        events = [
            'customer.subscription.created',
            'customer.subscription.updated',
            'customer.subscription.deleted',
            'invoice.payment_succeeded',
            'invoice.payment_failed',
            'checkout.session.completed'
        ]
        for event in events:
            self.stdout.write(f'   • {event}')

    def show_next_steps(self):
        """Exibe próximos passos"""
        self.stdout.write('\n🚀 PRÓXIMOS PASSOS:')
        self.stdout.write('=' * 40)

        steps = [
            'Configure suas chaves no arquivo .env',
            'Configure webhooks (use --webhook-info para detalhes)',
            'Execute: python manage.py runserver',
            'Acesse o dashboard e teste o modal de upgrade',
            'Use os cartões de teste fornecidos acima',
            'Monitore os webhooks no Stripe Dashboard'
        ]

        for i, step in enumerate(steps, 1):
            self.stdout.write(f'{i}. {step}')

        self.stdout.write('\n📊 MONITORAMENTO:')
        self.stdout.write('   • Logs: tail -f logs/django.log')
        self.stdout.write('   • Stripe Dashboard: https://dashboard.stripe.com/test/')
        self.stdout.write('   • Webhooks: https://dashboard.stripe.com/test/webhooks')

        self.stdout.write(f'\n✅ Ambiente de testes configurado com sucesso!')
        self.stdout.write(f'🔑 Chave usada: {settings.STRIPE_SECRET_KEY[:12]}...')
