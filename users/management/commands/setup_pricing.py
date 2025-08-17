from django.core.management.base import BaseCommand
from decimal import Decimal
from users.models import PlanPricing


class Command(BaseCommand):
    help = 'Configura os preços dos planos padrão'

    def handle(self, *args, **options):
        self.stdout.write('Configurando preços dos planos...')

        # Dados dos planos
        plans_data = [
            {
                'plan': 'free',
                'monthly_price': Decimal('0.00'),
                'yearly_price': Decimal('0.00'),
                'features': {
                    'max_shortcuts': 50,
                    'max_ai_requests': 100,
                    'ai_enabled': True,
                    'categories': True,
                    'export_import': False,
                    'priority_support': False,
                    'custom_integrations': False,
                    'analytics': 'basic',
                    'team_sharing': False
                }
            },
            {
                'plan': 'premium',
                'monthly_price': Decimal('19.90'),
                'yearly_price': Decimal('199.00'),
                'features': {
                    'max_shortcuts': 500,
                    'max_ai_requests': 1000,
                    'ai_enabled': True,
                    'categories': True,
                    'export_import': True,
                    'priority_support': True,
                    'custom_integrations': False,
                    'analytics': 'advanced',
                    'team_sharing': False
                }
            },
            {
                'plan': 'enterprise',
                'monthly_price': Decimal('49.90'),
                'yearly_price': Decimal('499.00'),
                'features': {
                    'max_shortcuts': -1,  # Ilimitado
                    'max_ai_requests': -1,  # Ilimitado
                    'ai_enabled': True,
                    'categories': True,
                    'export_import': True,
                    'priority_support': True,
                    'custom_integrations': True,
                    'analytics': 'premium',
                    'team_sharing': True
                }
            }
        ]

        created_count = 0
        updated_count = 0

        for plan_data in plans_data:
            pricing, created = PlanPricing.objects.get_or_create(
                plan=plan_data['plan'],
                defaults={
                    'monthly_price': plan_data['monthly_price'],
                    'yearly_price': plan_data['yearly_price'],
                    'features': plan_data['features'],
                    'is_active': True
                }
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Plano {plan_data["plan"]} criado')
                )
            else:
                # Atualizar dados existentes
                pricing.monthly_price = plan_data['monthly_price']
                pricing.yearly_price = plan_data['yearly_price']
                pricing.features = plan_data['features']
                pricing.is_active = True
                pricing.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ Plano {plan_data["plan"]} atualizado')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nConcluído! {created_count} planos criados, {updated_count} atualizados.'
            )
        )

        # Mostrar resumo
        self.stdout.write('\n' + '='*50)
        self.stdout.write('RESUMO DOS PLANOS CONFIGURADOS:')
        self.stdout.write('='*50)

        for pricing in PlanPricing.objects.all().order_by('monthly_price'):
            self.stdout.write(f'\n{pricing.get_plan_display().upper()}:')
            self.stdout.write(f'  💰 Mensal: R$ {pricing.monthly_price}')
            if pricing.yearly_price:
                savings = (pricing.monthly_price * 12 - pricing.yearly_price) / (pricing.monthly_price * 12) * 100
                self.stdout.write(f'  💰 Anual: R$ {pricing.yearly_price} (economize {savings:.0f}%)')

            features = pricing.features
            max_shortcuts = features.get('max_shortcuts', 0)
            max_ai_requests = features.get('max_ai_requests', 0)

            self.stdout.write(f'  📝 Atalhos: {"Ilimitados" if max_shortcuts == -1 else max_shortcuts}')
            self.stdout.write(f'  🤖 IA: {"Ilimitada" if max_ai_requests == -1 else f"{max_ai_requests}/mês"}')

            if features.get('export_import'):
                self.stdout.write('  ↗️  Exportar/Importar')
            if features.get('priority_support'):
                self.stdout.write('  🚀 Suporte Prioritário')
            if features.get('custom_integrations'):
                self.stdout.write('  🔗 Integrações Personalizadas')

        self.stdout.write('\n' + '='*50)
