import stripe
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from .models import (
    StripeCustomer,
    StripeProduct,
    StripePrice,
    StripeSubscription,
    StripePaymentIntent,
    StripeWebhookEvent
)
from users.models import UserProfile, Subscription
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

# Configurar Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Serviço para integração com Stripe"""
    
    @staticmethod
    def create_customer(user: User, email: str = None) -> StripeCustomer:
        """Cria um cliente no Stripe"""
        try:
            # Criar cliente no Stripe
            stripe_customer = stripe.Customer.create(
                email=email or user.email,
                name=f"{user.first_name} {user.last_name}".strip() or user.username,
                metadata={
                    'user_id': user.id,
                    'username': user.username
                }
            )
            
            # Salvar no banco local
            customer, created = StripeCustomer.objects.get_or_create(
                user=user,
                defaults={
                    'stripe_customer_id': stripe_customer.id
                }
            )
            
            if not created:
                customer.stripe_customer_id = stripe_customer.id
                customer.save()
            
            return customer
            
        except stripe.error.StripeError as e:
            logger.error(f"Erro ao criar cliente Stripe: {e}")
            raise Exception(f"Erro ao criar cliente: {str(e)}")
    
    @staticmethod
    def get_or_create_customer(user: User) -> StripeCustomer:
        """Obtém ou cria um cliente no Stripe"""
        try:
            customer = StripeCustomer.objects.get(user=user)
            return customer
        except StripeCustomer.DoesNotExist:
            return StripeService.create_customer(user)
    
    @staticmethod
    def create_subscription(
        user: User,
        price_id: str,
        payment_method_id: str,
        billing_cycle: str = 'month'
    ) -> StripeSubscription:
        """Cria uma assinatura no Stripe"""
        try:
            customer = StripeService.get_or_create_customer(user)
            
            # Anexar método de pagamento ao cliente
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer.stripe_customer_id
            )
            
            # Definir como método padrão
            stripe.Customer.modify(
                customer.stripe_customer_id,
                invoice_settings={
                    'default_payment_method': payment_method_id
                }
            )
            
            # Criar assinatura
            stripe_subscription = stripe.Subscription.create(
                customer=customer.stripe_customer_id,
                items=[{'price': price_id}],
                payment_behavior='default_incomplete',
                payment_settings={'save_default_payment_method': 'on_subscription'},
                expand=['latest_invoice.payment_intent'],
                metadata={
                    'user_id': user.id,
                    'billing_cycle': billing_cycle
                }
            )
            
            # Obter preço
            price = StripePrice.objects.get(stripe_price_id=price_id)
            
            # Salvar assinatura local
            subscription = StripeSubscription.objects.create(
                user=user,
                stripe_subscription_id=stripe_subscription.id,
                price=price,
                status=stripe_subscription.status,
                current_period_start=timezone.datetime.fromtimestamp(
                    stripe_subscription.current_period_start,
                    tz=timezone.utc
                ),
                current_period_end=timezone.datetime.fromtimestamp(
                    stripe_subscription.current_period_end,
                    tz=timezone.utc
                ),
                cancel_at_period_end=stripe_subscription.cancel_at_period_end
            )
            
            # Atualizar perfil do usuário
            profile = user.profile
            if price.product.name.lower() == 'premium':
                profile.plan = 'premium'
                profile.max_shortcuts = 500
                profile.max_ai_requests = 1000
            elif price.product.name.lower() == 'enterprise':
                profile.plan = 'enterprise'
                profile.max_shortcuts = -1
                profile.max_ai_requests = -1
            profile.save()
            
            return subscription
            
        except stripe.error.StripeError as e:
            logger.error(f"Erro ao criar assinatura Stripe: {e}")
            raise Exception(f"Erro ao criar assinatura: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao criar assinatura: {e}")
            raise
    
    @staticmethod
    def cancel_subscription(
        user: User,
        cancel_at_period_end: bool = True
    ) -> bool:
        """Cancela uma assinatura no Stripe"""
        try:
            subscription = StripeSubscription.objects.filter(
                user=user,
                status__in=['active', 'trialing']
            ).first()
            
            if not subscription:
                raise Exception("Nenhuma assinatura ativa encontrada")
            
            # Cancelar no Stripe
            if cancel_at_period_end:
                stripe.Subscription.modify(
                    subscription.stripe_subscription_id,
                    cancel_at_period_end=True
                )
                subscription.cancel_at_period_end = True
            else:
                stripe.Subscription.cancel(subscription.stripe_subscription_id)
                subscription.status = 'canceled'
            
            subscription.save()
            
            # Atualizar perfil do usuário para plano gratuito
            profile = user.profile
            profile.plan = 'free'
            profile.max_shortcuts = 50
            profile.max_ai_requests = 100
            profile.save()
            
            return True
            
        except stripe.error.StripeError as e:
            logger.error(f"Erro ao cancelar assinatura Stripe: {e}")
            raise Exception(f"Erro ao cancelar assinatura: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao cancelar assinatura: {e}")
            raise
    
    @staticmethod
    def create_payment_intent(
        user: User,
        amount: Decimal,
        currency: str = 'brl',
        payment_method_types: list = None
    ) -> StripePaymentIntent:
        """Cria uma intenção de pagamento no Stripe"""
        try:
            if payment_method_types is None:
                payment_method_types = ['card', 'pix']
            
            customer = StripeService.get_or_create_customer(user)
            
            # Criar intenção de pagamento
            stripe_payment_intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Stripe usa centavos
                currency=currency,
                customer=customer.stripe_customer_id,
                payment_method_types=payment_method_types,
                metadata={
                    'user_id': user.id
                }
            )
            
            # Salvar localmente
            payment_intent = StripePaymentIntent.objects.create(
                user=user,
                stripe_payment_intent_id=stripe_payment_intent.id,
                amount=int(amount * 100),
                currency=currency,
                status=stripe_payment_intent.status,
                payment_method_types=payment_method_types,
                client_secret=stripe_payment_intent.client_secret
            )
            
            return payment_intent
            
        except stripe.error.StripeError as e:
            logger.error(f"Erro ao criar intenção de pagamento Stripe: {e}")
            raise Exception(f"Erro ao criar intenção de pagamento: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao criar intenção de pagamento: {e}")
            raise
    
    @staticmethod
    def get_subscription_status(user: User) -> dict:
        """Obtém o status da assinatura do usuário"""
        try:
            subscription = StripeSubscription.objects.filter(
                user=user,
                status__in=['active', 'trialing']
            ).first()
            
            if not subscription:
                return {
                    'has_active_subscription': False,
                    'plan': 'free',
                    'status': 'inactive'
                }
            
            return {
                'has_active_subscription': True,
                'plan': subscription.price.product.name.lower(),
                'status': subscription.status,
                'current_period_end': subscription.current_period_end,
                'days_remaining': subscription.days_remaining,
                'cancel_at_period_end': subscription.cancel_at_period_end
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter status da assinatura: {e}")
            return {
                'has_active_subscription': False,
                'plan': 'free',
                'status': 'error'
            }
    
    @staticmethod
    def process_webhook(event_data: dict) -> bool:
        """Processa webhook do Stripe"""
        try:
            event_id = event_data.get('id')
            event_type = event_data.get('type')
            
            # Verificar se já foi processado
            if StripeWebhookEvent.objects.filter(stripe_event_id=event_id).exists():
                logger.info(f"Evento {event_id} já foi processado")
                return True
            
            # Salvar evento
            webhook_event = StripeWebhookEvent.objects.create(
                stripe_event_id=event_id,
                event_type=event_type,
                data=event_data
            )
            
            # Processar evento
            if event_type == 'customer.subscription.updated':
                StripeService._handle_subscription_updated(event_data)
            elif event_type == 'customer.subscription.deleted':
                StripeService._handle_subscription_deleted(event_data)
            elif event_type == 'invoice.payment_succeeded':
                StripeService._handle_payment_succeeded(event_data)
            elif event_type == 'invoice.payment_failed':
                StripeService._handle_payment_failed(event_data)
            
            # Marcar como processado
            webhook_event.processed = True
            webhook_event.processed_at = timezone.now()
            webhook_event.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar webhook: {e}")
            return False
    
    @staticmethod
    def _handle_subscription_updated(event_data: dict):
        """Manipula atualização de assinatura"""
        try:
            subscription_data = event_data['data']['object']
            subscription_id = subscription_data['id']
            
            subscription = StripeSubscription.objects.get(
                stripe_subscription_id=subscription_id
            )
            
            # Atualizar status
            subscription.status = subscription_data['status']
            subscription.current_period_start = timezone.datetime.fromtimestamp(
                subscription_data['current_period_start'],
                tz=timezone.utc
            )
            subscription.current_period_end = timezone.datetime.fromtimestamp(
                subscription_data['current_period_end'],
                tz=timezone.utc
            )
            subscription.cancel_at_period_end = subscription_data['cancel_at_period_end']
            subscription.save()
            
            logger.info(f"Assinatura {subscription_id} atualizada")
            
        except Exception as e:
            logger.error(f"Erro ao processar atualização de assinatura: {e}")
    
    @staticmethod
    def _handle_subscription_deleted(event_data: dict):
        """Manipula exclusão de assinatura"""
        try:
            subscription_data = event_data['data']['object']
            subscription_id = subscription_data['id']
            
            subscription = StripeSubscription.objects.get(
                stripe_subscription_id=subscription_id
            )
            
            # Atualizar status
            subscription.status = 'canceled'
            subscription.save()
            
            # Atualizar perfil do usuário para plano gratuito
            profile = subscription.user.profile
            profile.plan = 'free'
            profile.max_shortcuts = 50
            profile.max_ai_requests = 100
            profile.save()
            
            logger.info(f"Assinatura {subscription_id} cancelada")
            
        except Exception as e:
            logger.error(f"Erro ao processar cancelamento de assinatura: {e}")
    
    @staticmethod
    def _handle_payment_succeeded(event_data: dict):
        """Manipula pagamento bem-sucedido"""
        try:
            invoice_data = event_data['data']['object']
            subscription_id = invoice_data.get('subscription')
            
            if subscription_id:
                subscription = StripeSubscription.objects.get(
                    stripe_subscription_id=subscription_id
                )
                
                # Atualizar perfil do usuário
                profile = subscription.user.profile
                if subscription.price.product.name.lower() == 'premium':
                    profile.plan = 'premium'
                    profile.max_shortcuts = 500
                    profile.max_ai_requests = 1000
                elif subscription.price.product.name.lower() == 'enterprise':
                    profile.plan = 'enterprise'
                    profile.max_shortcuts = -1
                    profile.max_ai_requests = -1
                profile.save()
                
                logger.info(f"Pagamento processado para assinatura {subscription_id}")
            
        except Exception as e:
            logger.error(f"Erro ao processar pagamento bem-sucedido: {e}")
    
    @staticmethod
    def _handle_payment_failed(event_data: dict):
        """Manipula falha no pagamento"""
        try:
            invoice_data = event_data['data']['object']
            subscription_id = invoice_data.get('subscription')
            
            if subscription_id:
                subscription = StripeSubscription.objects.get(
                    stripe_subscription_id=subscription_id
                )
                
                # Atualizar status se necessário
                if subscription.status == 'active':
                    subscription.status = 'past_due'
                    subscription.save()
                
                logger.info(f"Falha no pagamento para assinatura {subscription_id}")
            
        except Exception as e:
            logger.error(f"Erro ao processar falha no pagamento: {e}")
    
    @staticmethod
    def handle_checkout_session_completed(event_data: dict):
        """Processa checkout session completado"""
        try:
            session = event_data['data']['object']
            customer_id = session['customer']
            subscription_id = session['subscription']
            metadata = session.get('metadata', {})
            
            # Buscar usuário pelos metadados
            user_id = metadata.get('user_id')
            if not user_id:
                logger.error("User ID não encontrado nos metadados da sessão")
                return
            
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                logger.error(f"Usuário {user_id} não encontrado")
                return
            
            # Buscar assinatura no Stripe
            stripe_subscription = stripe.Subscription.retrieve(subscription_id)
            
            # Buscar preço local
            price_id = stripe_subscription['items']['data'][0]['price']['id']
            try:
                local_price = StripePrice.objects.get(stripe_price_id=price_id)
            except StripePrice.DoesNotExist:
                logger.error(f"Preço {price_id} não encontrado localmente")
                return
            
            # Criar ou atualizar assinatura local
            subscription, created = StripeSubscription.objects.get_or_create(
                stripe_subscription_id=subscription_id,
                defaults={
                    'user': user,
                    'price': local_price,
                    'status': stripe_subscription['status'],
                    'current_period_start': timezone.datetime.fromtimestamp(
                        stripe_subscription['current_period_start'], 
                        tz=timezone.utc
                    ),
                    'current_period_end': timezone.datetime.fromtimestamp(
                        stripe_subscription['current_period_end'], 
                        tz=timezone.utc
                    ),
                    'cancel_at_period_end': stripe_subscription['cancel_at_period_end']
                }
            )
            
            # Atualizar plano do usuário
            plan_name = metadata.get('plan', local_price.product.name.lower())
            profile = user.profile
            profile.plan = plan_name
            
            # Atualizar limites baseado no plano
            if plan_name == 'premium':
                profile.max_shortcuts = 500
                profile.max_ai_requests = 1000
            elif plan_name == 'enterprise':
                profile.max_shortcuts = -1
                profile.max_ai_requests = -1
            
            profile.save()
            
            logger.info(f"Assinatura {subscription_id} ativada para usuário {user.username}")
            
        except Exception as e:
            logger.error(f"Erro ao processar checkout session completado: {e}")


class PlanService:
    """Serviço para gerenciar planos"""
    
    @staticmethod
    def get_available_plans() -> list:
        """Retorna os planos disponíveis com preços"""
        try:
            prices = StripePrice.objects.filter(
                is_active=True,
                product__is_active=True
            ).select_related('product')
            
            plans = {}
            for price in prices:
                plan_name = price.product.name.lower()
                if plan_name not in plans:
                    plans[plan_name] = {
                        'name': price.product.name,
                        'description': price.product.description,
                        'prices': []
                    }
                
                plans[plan_name]['prices'].append({
                    'id': price.stripe_price_id,
                    'amount': price.amount_in_reais,
                    'interval': price.interval,
                    'interval_count': price.interval_count
                })
            
            return list(plans.values())
            
        except Exception as e:
            logger.error(f"Erro ao obter planos: {e}")
            return []
    
    @staticmethod
    def get_user_plan_info(user: User) -> dict:
        """Obtém informações do plano do usuário"""
        try:
            profile = user.profile
            subscription_info = StripeService.get_subscription_status(user)
            
            return {
                'current_plan': profile.plan,
                'max_shortcuts': profile.max_shortcuts,
                'max_ai_requests': profile.max_ai_requests,
                'ai_requests_used': profile.ai_requests_used,
                'subscription': subscription_info
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter informações do plano: {e}")
            return {
                'current_plan': 'free',
                'max_shortcuts': 50,
                'max_ai_requests': 100,
                'ai_requests_used': 0,
                'subscription': {'has_active_subscription': False}
            } 