from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import timedelta
import logging
import uuid

from .models import (
    UserProfile, PlanPricing, Subscription, Payment, PlanUpgradeRequest
)
from core.models import ActivityLog

logger = logging.getLogger(__name__)


class PaymentService:
    """Serviço para gerenciar pagamentos e upgrades de plano"""

    def __init__(self):
        self.setup_default_pricing()

    def setup_default_pricing(self):
        """Configura preços padrão dos planos se não existirem"""
        default_plans = [
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
                    'custom_integrations': False
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
                    'custom_integrations': False
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
                    'custom_integrations': True
                }
            }
        ]

        for plan_data in default_plans:
            PlanPricing.objects.get_or_create(
                plan=plan_data['plan'],
                defaults={
                    'monthly_price': plan_data['monthly_price'],
                    'yearly_price': plan_data['yearly_price'],
                    'features': plan_data['features']
                }
            )

    def get_plan_pricing(self, plan=None):
        """Obtém preços dos planos"""
        if plan:
            try:
                return PlanPricing.objects.get(plan=plan, is_active=True)
            except PlanPricing.DoesNotExist:
                return None

        return PlanPricing.objects.filter(is_active=True).order_by('monthly_price')

    def can_upgrade_to_plan(self, user, target_plan):
        """Verifica se o usuário pode fazer upgrade para o plano especificado"""
        current_plan = user.profile.plan

        plan_hierarchy = ['free', 'premium', 'enterprise']

        try:
            current_index = plan_hierarchy.index(current_plan)
            target_index = plan_hierarchy.index(target_plan)
            return target_index > current_index
        except ValueError:
            return False

    def calculate_upgrade_cost(self, user, target_plan, billing_cycle='monthly'):
        """Calcula o custo do upgrade"""
        if not self.can_upgrade_to_plan(user, target_plan):
            return None

        pricing = self.get_plan_pricing(target_plan)
        if not pricing:
            return None

        if billing_cycle == 'yearly' and pricing.yearly_price:
            return pricing.yearly_price
        else:
            return pricing.monthly_price

    def create_upgrade_request(self, user, target_plan, payment_method, billing_cycle='monthly'):
        """Cria uma solicitação de upgrade de plano"""
        try:
            # Verificar se pode fazer upgrade
            if not self.can_upgrade_to_plan(user, target_plan):
                raise ValueError("Upgrade não permitido para este plano")

            # Calcular custo
            amount = self.calculate_upgrade_cost(user, target_plan, billing_cycle)
            if amount is None:
                raise ValueError("Não foi possível calcular o custo do upgrade")

            # Verificar se já existe solicitação pendente
            existing_request = PlanUpgradeRequest.objects.filter(
                user=user,
                status='pending'
            ).first()

            if existing_request:
                raise ValueError("Já existe uma solicitação de upgrade pendente")

            # Criar solicitação
            upgrade_request = PlanUpgradeRequest.objects.create(
                user=user,
                current_plan=user.profile.plan,
                requested_plan=target_plan,
                payment_method=payment_method,
                billing_cycle=billing_cycle,
                amount=amount
            )

            # Log da atividade
            ActivityLog.log_activity(
                user=user,
                action='plan_upgrade',
                description=f'Solicitação de upgrade para {target_plan}',
                metadata={
                    'target_plan': target_plan,
                    'amount': str(amount),
                    'payment_method': payment_method,
                    'billing_cycle': billing_cycle
                }
            )

            logger.info(f"Upgrade request created for user {user.username} to {target_plan}")

            return upgrade_request

        except Exception as e:
            logger.error(f"Error creating upgrade request for {user.username}: {str(e)}")
            raise

    def process_payment(self, upgrade_request, gateway_response=None):
        """Processa o pagamento de um upgrade"""
        try:
            # Criar registro de pagamento
            payment = Payment.objects.create(
                user=upgrade_request.user,
                subscription=self.get_or_create_subscription(upgrade_request.user),
                amount=upgrade_request.amount,
                payment_method=upgrade_request.payment_method,
                status='processing',
                transaction_id=self.generate_transaction_id(),
                gateway_response=gateway_response or {}
            )

            # Simular processamento do pagamento
            # Em um ambiente real, aqui seria feita a integração com gateway de pagamento
            payment_success = self.simulate_payment_processing(payment)

            if payment_success:
                payment.status = 'completed'
                payment.paid_at = timezone.now()
                payment.save()

                # Aprovar a solicitação de upgrade
                upgrade_request.approve()

                # Atualizar assinatura
                self.update_subscription(upgrade_request.user, upgrade_request.requested_plan)

                logger.info(f"Payment processed successfully for user {upgrade_request.user.username}")

                return payment
            else:
                payment.status = 'failed'
                payment.save()

                logger.error(f"Payment failed for user {upgrade_request.user.username}")
                raise Exception("Falha no processamento do pagamento")

        except Exception as e:
            logger.error(f"Error processing payment: {str(e)}")
            raise

    def simulate_payment_processing(self, payment):
        """Simula o processamento de pagamento (para desenvolvimento)"""
        # Em produção, aqui seria a integração real com o gateway

        # Simular diferentes cenários baseado no método de pagamento
        if payment.payment_method == 'credit_card':
            return True  # 100% sucesso para cartão
        elif payment.payment_method == 'pix':
            return True  # 100% sucesso para PIX
        elif payment.payment_method == 'boleto':
            return True  # 100% sucesso para boleto
        else:
            return False  # Falha para métodos não implementados

    def generate_transaction_id(self):
        """Gera um ID único para a transação"""
        return f"TXN-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

    def get_or_create_subscription(self, user):
        """Obtém ou cria uma assinatura para o usuário"""
        subscription, created = Subscription.objects.get_or_create(
            user=user,
            defaults={
                'plan': user.profile.plan,
                'status': 'active',
                'billing_cycle': 'monthly',
                'start_date': timezone.now(),
                'end_date': timezone.now() + timedelta(days=30),
                'next_billing_date': timezone.now() + timedelta(days=30),
                'amount': Decimal('0.00')
            }
        )

        return subscription

    def update_subscription(self, user, new_plan):
        """Atualiza a assinatura do usuário"""
        try:
            subscription = self.get_or_create_subscription(user)
            pricing = self.get_plan_pricing(new_plan)

            subscription.plan = new_plan
            subscription.status = 'active'

            # Atualizar datas e valor
            if subscription.billing_cycle == 'yearly':
                subscription.amount = pricing.yearly_price or pricing.monthly_price * 12
                subscription.end_date = timezone.now() + timedelta(days=365)
                subscription.next_billing_date = timezone.now() + timedelta(days=365)
            else:
                subscription.amount = pricing.monthly_price
                subscription.end_date = timezone.now() + timedelta(days=30)
                subscription.next_billing_date = timezone.now() + timedelta(days=30)

            subscription.save()

            logger.info(f"Subscription updated for user {user.username} to {new_plan}")

        except Exception as e:
            logger.error(f"Error updating subscription: {str(e)}")
            raise

    def cancel_subscription(self, user):
        """Cancela a assinatura do usuário"""
        try:
            subscription = Subscription.objects.get(user=user)
            subscription.status = 'cancelled'
            subscription.save()

            # Downgrade para plano gratuito no final do período
            # Por enquanto, fazemos o downgrade imediatamente
            profile = user.profile
            profile.plan = 'free'
            profile.max_shortcuts = 50
            profile.max_ai_requests = 100
            profile.save()

            ActivityLog.log_activity(
                user=user,
                action='plan_upgrade',
                description='Assinatura cancelada - downgrade para plano gratuito',
                metadata={'previous_plan': subscription.plan}
            )

            logger.info(f"Subscription cancelled for user {user.username}")

        except Subscription.DoesNotExist:
            logger.warning(f"No subscription found for user {user.username}")

    def get_user_payment_history(self, user):
        """Obtém o histórico de pagamentos do usuário"""
        return Payment.objects.filter(user=user).order_by('-created_at')

    def get_available_payment_methods(self):
        """Retorna os métodos de pagamento disponíveis"""
        return [
            {
                'key': 'credit_card',
                'name': 'Cartão de Crédito',
                'description': 'Visa, Mastercard, Elo',
                'icon': 'credit-card',
                'is_available': True
            },
            {
                'key': 'debit_card',
                'name': 'Cartão de Débito',
                'description': 'Débito online',
                'icon': 'debit-card',
                'is_available': True
            },
            {
                'key': 'pix',
                'name': 'PIX',
                'description': 'Pagamento instantâneo',
                'icon': 'pix',
                'is_available': True
            },
            {
                'key': 'boleto',
                'name': 'Boleto Bancário',
                'description': 'Vencimento em 3 dias úteis',
                'icon': 'barcode',
                'is_available': True
            },
            {
                'key': 'paypal',
                'name': 'PayPal',
                'description': 'Pagamento via PayPal',
                'icon': 'paypal',
                'is_available': False  # Desabilitado por enquanto
            }
        ]

    def get_plan_comparison(self, user):
        """Retorna comparação de planos para o usuário"""
        plans = []
        current_plan = user.profile.plan

        for pricing in self.get_plan_pricing():
            plan_data = {
                'plan': pricing.plan,
                'plan_display': pricing.get_plan_display(),
                'monthly_price': pricing.monthly_price,
                'yearly_price': pricing.yearly_price,
                'features': pricing.features,
                'max_shortcuts': pricing.features.get('max_shortcuts', 0),
                'max_ai_requests': pricing.features.get('max_ai_requests', 0),
                'is_current': pricing.plan == current_plan,
                'can_upgrade': self.can_upgrade_to_plan(user, pricing.plan)
            }
            plans.append(plan_data)

        return plans

    def get_user_subscription_info(self, user):
        """Obtém informações da assinatura do usuário"""
        try:
            subscription = Subscription.objects.get(user=user)
            return {
                'has_subscription': True,
                'plan': subscription.plan,
                'status': subscription.status,
                'is_active': subscription.is_active,
                'days_remaining': subscription.days_remaining,
                'next_billing_date': subscription.next_billing_date,
                'amount': subscription.amount,
                'billing_cycle': subscription.billing_cycle
            }
        except Subscription.DoesNotExist:
            return {
                'has_subscription': False,
                'plan': user.profile.plan,
                'status': 'free',
                'is_active': True,
                'days_remaining': None,
                'next_billing_date': None,
                'amount': Decimal('0.00'),
                'billing_cycle': None
            }


class PaymentGatewayService:
    """Serviço para integração com gateways de pagamento"""

    def __init__(self):
        self.gateway_config = {
            'stripe': {
                'public_key': settings.STRIPE_PUBLIC_KEY if hasattr(settings, 'STRIPE_PUBLIC_KEY') else '',
                'secret_key': settings.STRIPE_SECRET_KEY if hasattr(settings, 'STRIPE_SECRET_KEY') else '',
                'enabled': False
            },
            'pagseguro': {
                'email': settings.PAGSEGURO_EMAIL if hasattr(settings, 'PAGSEGURO_EMAIL') else '',
                'token': settings.PAGSEGURO_TOKEN if hasattr(settings, 'PAGSEGURO_TOKEN') else '',
                'enabled': False
            },
            'mercadopago': {
                'access_token': settings.MERCADOPAGO_ACCESS_TOKEN if hasattr(settings, 'MERCADOPAGO_ACCESS_TOKEN') else '',
                'enabled': False
            }
        }

    def process_credit_card_payment(self, payment_data):
        """Processa pagamento com cartão de crédito"""
        # Implementação futura - integração com Stripe ou similar
        return {
            'success': True,
            'transaction_id': f"CC-{uuid.uuid4().hex[:8].upper()}",
            'message': 'Pagamento processado com sucesso'
        }

    def process_pix_payment(self, payment_data):
        """Processa pagamento via PIX"""
        # Implementação futura - integração com gateway PIX
        return {
            'success': True,
            'transaction_id': f"PIX-{uuid.uuid4().hex[:8].upper()}",
            'qr_code': f"00020126{uuid.uuid4().hex}",
            'message': 'PIX gerado com sucesso'
        }

    def process_boleto_payment(self, payment_data):
        """Processa pagamento via boleto"""
        # Implementação futura - integração com gateway de boleto
        return {
            'success': True,
            'transaction_id': f"BOL-{uuid.uuid4().hex[:8].upper()}",
            'boleto_url': f"https://example.com/boleto/{uuid.uuid4().hex}",
            'due_date': (timezone.now() + timedelta(days=3)).date(),
            'message': 'Boleto gerado com sucesso'
        }
