from django.core.management.base import BaseCommand
from django.conf import settings
import stripe
from payments.models import StripeProduct, StripePrice

stripe.api_key = settings.STRIPE_SECRET_KEY


class Command(BaseCommand):
    help = 'Configura produtos e preços padrão no Stripe'

    def handle(self, *args, **options):
        if not settings.STRIPE_SECRET_KEY:
            self.stdout.write(
                self.style.ERROR('STRIPE_SECRET_KEY não configurada')
            )
            return

        self.stdout.write('Configurando produtos e preços no Stripe...')

        # Criar produto Premium
        try:
            premium_product = stripe.Product.create(
                name='Premium',
                description='Plano Premium com funcionalidades avançadas',
                metadata={
                    'plan_type': 'premium',
                    'max_shortcuts': '500',
                    'max_ai_requests': '1000'
                }
            )

            # Criar preço mensal Premium
            premium_monthly_price = stripe.Price.create(
                product=premium_product.id,
                unit_amount=2990,  # R$ 29,90
                currency='brl',
                recurring={'interval': 'month'},
                metadata={
                    'plan_type': 'premium',
                    'billing_cycle': 'monthly'
                }
            )

            # Criar preço anual Premium
            premium_yearly_price = stripe.Price.create(
                product=premium_product.id,
                unit_amount=29900,  # R$ 299,00
                currency='brl',
                recurring={'interval': 'year'},
                metadata={
                    'plan_type': 'premium',
                    'billing_cycle': 'yearly'
                }
            )

            # Salvar no banco local
            product, created = StripeProduct.objects.get_or_create(
                stripe_product_id=premium_product.id,
                defaults={
                    'name': 'Premium',
                    'description': 'Plano Premium com funcionalidades avançadas'
                }
            )

            if not created:
                product.name = 'Premium'
                product.description = 'Plano Premium com funcionalidades avançadas'
                product.save()

            # Salvar preços
            StripePrice.objects.get_or_create(
                stripe_price_id=premium_monthly_price.id,
                defaults={
                    'product': product,
                    'unit_amount': 2990,
                    'currency': 'brl',
                    'interval': 'month',
                    'interval_count': 1
                }
            )

            StripePrice.objects.get_or_create(
                stripe_price_id=premium_yearly_price.id,
                defaults={
                    'product': product,
                    'unit_amount': 29900,
                    'currency': 'brl',
                    'interval': 'year',
                    'interval_count': 1
                }
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Produto Premium criado: {premium_product.id}'
                )
            )

        except stripe.error.StripeError as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao criar produto Premium: {e}')
            )

        # Criar produto Enterprise
        try:
            enterprise_product = stripe.Product.create(
                name='Enterprise',
                description='Plano Enterprise com funcionalidades ilimitadas',
                metadata={
                    'plan_type': 'enterprise',
                    'max_shortcuts': 'unlimited',
                    'max_ai_requests': 'unlimited'
                }
            )

            # Criar preço mensal Enterprise
            enterprise_monthly_price = stripe.Price.create(
                product=enterprise_product.id,
                unit_amount=9990,  # R$ 99,90
                currency='brl',
                recurring={'interval': 'month'},
                metadata={
                    'plan_type': 'enterprise',
                    'billing_cycle': 'monthly'
                }
            )

            # Criar preço anual Enterprise
            enterprise_yearly_price = stripe.Price.create(
                product=enterprise_product.id,
                unit_amount=99900,  # R$ 999,00
                currency='brl',
                recurring={'interval': 'year'},
                metadata={
                    'plan_type': 'enterprise',
                    'billing_cycle': 'yearly'
                }
            )

            # Salvar no banco local
            product, created = StripeProduct.objects.get_or_create(
                stripe_product_id=enterprise_product.id,
                defaults={
                    'name': 'Enterprise',
                    'description': 'Plano Enterprise com funcionalidades ilimitadas'
                }
            )

            if not created:
                product.name = 'Enterprise'
                product.description = 'Plano Enterprise com funcionalidades ilimitadas'
                product.save()

            # Salvar preços
            StripePrice.objects.get_or_create(
                stripe_price_id=enterprise_monthly_price.id,
                defaults={
                    'product': product,
                    'unit_amount': 9990,
                    'currency': 'brl',
                    'interval': 'month',
                    'interval_count': 1
                }
            )

            StripePrice.objects.get_or_create(
                stripe_price_id=enterprise_yearly_price.id,
                defaults={
                    'product': product,
                    'unit_amount': 99900,
                    'currency': 'brl',
                    'interval': 'year',
                    'interval_count': 1
                }
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Produto Enterprise criado: {enterprise_product.id}'
                )
            )

        except stripe.error.StripeError as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao criar produto Enterprise: {e}')
            )

        self.stdout.write(
            self.style.SUCCESS('Configuração do Stripe concluída!')
        )

        # Listar produtos criados
        self.stdout.write('\nProdutos configurados:')
        products = StripeProduct.objects.all()
        for product in products:
            self.stdout.write(f'- {product.name}: {product.stripe_product_id}')
            prices = product.prices.all()
            for price in prices:
                self.stdout.write(
                    f'  * {price.get_interval_display()}: R$ {price.amount_in_reais:.2f}'
                )
