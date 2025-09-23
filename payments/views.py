from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views import View
from django.conf import settings
import stripe
import json
import logging

from .serializers import (
    StripeProductSerializer,
    StripePriceSerializer,
    StripeCustomerSerializer,
    StripeSubscriptionSerializer,
    StripePaymentIntentSerializer,
    CreateSubscriptionSerializer,
    CancelSubscriptionSerializer,
    PaymentMethodSerializer,
    PlanUpgradeSerializer
)
from .services import StripeService, PlanService
from .models import StripeWebhookEvent
from django.utils import timezone

logger = logging.getLogger(__name__)

# Configurar Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class PlansView(APIView):
    """View para listar planos disponíveis"""

    def get(self, request):
        """Lista todos os planos disponíveis"""
        try:
            plans = PlanService.get_available_plans()
            return Response({
                'success': True,
                'plans': plans
            })
        except Exception as e:
            logger.error(f"Erro ao obter planos: {e}")
            return Response({
                'success': False,
                'error': 'Erro ao obter planos'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserPlanView(APIView):
    """View para informações do plano do usuário"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Obtém informações do plano do usuário atual"""
        try:
            plan_info = PlanService.get_user_plan_info(request.user)
            return Response({
                'success': True,
                'plan_info': plan_info
            })
        except Exception as e:
            logger.error(f"Erro ao obter informações do plano: {e}")
            return Response({
                'success': False,
                'error': 'Erro ao obter informações do plano'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateSubscriptionView(APIView):
    """View para criar assinatura"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Cria uma nova assinatura"""
        try:
            serializer = CreateSubscriptionSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            data = serializer.validated_data

            # Criar assinatura
            subscription = StripeService.create_subscription(
                user=request.user,
                price_id=data['price_id'],
                payment_method_id=data['payment_method_id'],
                billing_cycle=data['billing_cycle']
            )

            # Serializar resposta
            subscription_data = StripeSubscriptionSerializer(subscription).data

            return Response({
                'success': True,
                'subscription': subscription_data,
                'message': 'Assinatura criada com sucesso'
            })

        except Exception as e:
            logger.error(f"Erro ao criar assinatura: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class CancelSubscriptionView(APIView):
    """View para cancelar assinatura"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Cancela a assinatura do usuário"""
        try:
            serializer = CancelSubscriptionSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            data = serializer.validated_data

            # Cancelar assinatura
            success = StripeService.cancel_subscription(
                user=request.user,
                cancel_at_period_end=data['cancel_at_period_end']
            )

            if success:
                return Response({
                    'success': True,
                    'message': 'Assinatura cancelada com sucesso'
                })
            else:
                return Response({
                    'success': False,
                    'error': 'Erro ao cancelar assinatura'
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Erro ao cancelar assinatura: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class CreatePaymentIntentView(APIView):
    """View para criar intenção de pagamento"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Cria uma intenção de pagamento"""
        try:
            amount = request.data.get('amount')
            currency = request.data.get('currency', 'brl')
            payment_method_types = request.data.get('payment_method_types', ['card', 'pix'])

            if not amount:
                return Response({
                    'success': False,
                    'error': 'Valor é obrigatório'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Criar intenção de pagamento
            payment_intent = StripeService.create_payment_intent(
                user=request.user,
                amount=amount,
                currency=currency,
                payment_method_types=payment_method_types
            )

            # Serializar resposta
            payment_intent_data = StripePaymentIntentSerializer(payment_intent).data

            return Response({
                'success': True,
                'payment_intent': payment_intent_data
            })

        except Exception as e:
            logger.error(f"Erro ao criar intenção de pagamento: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class PlanUpgradeView(APIView):
    """View para upgrade de plano"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Faz upgrade do plano do usuário"""
        try:
            serializer = PlanUpgradeSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            data = serializer.validated_data

            # Verificar se o usuário já tem uma assinatura ativa
            subscription_status = StripeService.get_subscription_status(request.user)

            if subscription_status['has_active_subscription']:
                # Cancelar assinatura atual
                StripeService.cancel_subscription(request.user, cancel_at_period_end=True)

            # Buscar preço do novo plano
            from .models import StripePrice
            prices = StripePrice.objects.filter(
                product__name__iexact=data['plan'],
                interval=data['billing_cycle'],
                is_active=True
            ).first()

            if not prices:
                return Response({
                    'success': False,
                    'error': 'Preço não encontrado para o plano solicitado'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Criar nova assinatura
            payment_method_id = data.get('payment_method_id')
            if not payment_method_id:
                # Usar método de pagamento padrão do cliente
                customer = StripeService.get_or_create_customer(request.user)
                stripe_customer = stripe.Customer.retrieve(customer.stripe_customer_id)
                payment_method_id = stripe_customer.invoice_settings.default_payment_method

            if not payment_method_id:
                return Response({
                    'success': False,
                    'error': 'Método de pagamento é obrigatório'
                }, status=status.HTTP_400_BAD_REQUEST)

            subscription = StripeService.create_subscription(
                user=request.user,
                price_id=prices.stripe_price_id,
                payment_method_id=payment_method_id,
                billing_cycle=data['billing_cycle']
            )

            return Response({
                'success': True,
                'message': f'Upgrade para {data["plan"]} realizado com sucesso',
                'subscription': StripeSubscriptionSerializer(subscription).data
            })

        except Exception as e:
            logger.error(f"Erro ao fazer upgrade do plano: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class CreateCheckoutSessionView(APIView):
    """View para criar sessão de checkout do Stripe"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Cria uma sessão de checkout do Stripe"""
        try:
            plan = request.data.get('plan')
            billing_cycle = request.data.get('billing_cycle', 'monthly')

            # Log para ambiente de testes
            logger.info(f"Criando checkout - Usuário: {request.user.username}, Plano: {plan}, Ciclo: {billing_cycle}")

            if not plan:
                return Response({
                    'success': False,
                    'error': 'Plano é obrigatório'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Normalizar billing_cycle
            if billing_cycle == 'yearly':
                billing_cycle = 'year'
            elif billing_cycle == 'monthly':
                billing_cycle = 'month'

            # Buscar preço do plano no Stripe
            from .models import StripePrice
            price = StripePrice.objects.filter(
                product__name__iexact=plan,
                interval=billing_cycle,
                is_active=True
            ).first()

            if not price:
                # Log detalhado para debug em testes
                available_prices = StripePrice.objects.filter(is_active=True).values_list(
                    'product__name', 'interval', 'stripe_price_id'
                )
                logger.error(f"Preço não encontrado - Plano: {plan}, Ciclo: {billing_cycle}")
                logger.error(f"Preços disponíveis: {list(available_prices)}")

                return Response({
                    'success': False,
                    'error': f'Preço não encontrado para o plano {plan} ({billing_cycle}). Verifique se os produtos foram criados.',
                    'debug_info': list(available_prices) if settings.DEBUG else None
                }, status=status.HTTP_400_BAD_REQUEST)

            # Obter ou criar cliente Stripe
            try:
                customer = StripeService.get_or_create_customer(request.user)
                logger.info(f"Cliente Stripe: {customer.stripe_customer_id}")
            except Exception as e:
                logger.error(f"Erro ao criar/obter cliente Stripe: {e}")
                return Response({
                    'success': False,
                    'error': 'Erro ao configurar cliente. Tente novamente.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # URLs de sucesso e cancelamento
            success_url = request.build_absolute_uri('/users/subscription-success/')
            cancel_url = request.build_absolute_uri('/users/plan-upgrade/')

            # Configuração específica para ambiente de testes
            checkout_params = {
                'customer': customer.stripe_customer_id,
                'payment_method_types': ['card'],
                'line_items': [{
                    'price': price.stripe_price_id,
                    'quantity': 1,
                }],
                'mode': 'subscription',
                'success_url': success_url + '?session_id={CHECKOUT_SESSION_ID}',
                'cancel_url': cancel_url,
                'allow_promotion_codes': True,
                'billing_address_collection': 'required',
                'customer_update': {
                    'address': 'auto',
                    'name': 'auto'
                },
                'metadata': {
                    'user_id': request.user.id,
                    'plan': plan,
                    'billing_cycle': billing_cycle,
                    'environment': 'test' if settings.STRIPE_SECRET_KEY.startswith('sk_test_') else 'live'
                }
            }

            # Em ambiente de teste, adicionar trial period
            if settings.DEBUG and settings.STRIPE_SECRET_KEY.startswith('sk_test_'):
                checkout_params['subscription_data'] = {
                    'trial_period_days': 7,
                    'metadata': {
                        'test_subscription': 'true',
                        'user_id': request.user.id
                    }
                }

            # Criar sessão de checkout
            checkout_session = stripe.checkout.Session.create(**checkout_params)

            logger.info(f"Checkout criado com sucesso: {checkout_session.id}")

            return Response({
                'success': True,
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id,
                'test_mode': settings.STRIPE_SECRET_KEY.startswith('sk_test_')
            })

        except stripe.error.InvalidRequestError as e:
            logger.error(f"Erro de requisição Stripe: {e}")
            return Response({
                'success': False,
                'error': f'Erro na configuração: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.AuthenticationError as e:
            logger.error(f"Erro de autenticação Stripe: {e}")
            return Response({
                'success': False,
                'error': 'Erro de autenticação com Stripe. Verifique as chaves de API.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except stripe.error.StripeError as e:
            logger.error(f"Erro do Stripe: {e}")
            return Response({
                'success': False,
                'error': f'Erro no processamento: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.error(f"Erro geral ao criar sessão de checkout: {e}")
            return Response({
                'success': False,
                'error': 'Erro interno. Tente novamente.' if not settings.DEBUG else str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomerPortalView(APIView):
    """View para portal do cliente Stripe"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Cria sessão do portal do cliente"""
        try:
            customer = StripeService.get_or_create_customer(request.user)

            # Criar sessão do portal
            session = stripe.billing_portal.Session.create(
                customer=customer.stripe_customer_id,
                return_url=request.data.get('return_url', settings.STRIPE_RETURN_URL)
            )

            return Response({
                'success': True,
                'url': session.url
            })

        except Exception as e:
            logger.error(f"Erro ao criar sessão do portal: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class WebhookView(View):
    """View para webhooks do Stripe"""

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        """Processa webhook do Stripe"""
        try:
            payload = request.body
            sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

            if not sig_header:
                return JsonResponse({'error': 'Assinatura não fornecida'}, status=400)

            # Verificar assinatura do webhook
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
                )
            except ValueError as e:
                logger.error(f"Payload inválido: {e}")
                return JsonResponse({'error': 'Payload inválido'}, status=400)
            except stripe.error.SignatureVerificationError as e:
                logger.error(f"Assinatura inválida: {e}")
                return JsonResponse({'error': 'Assinatura inválida'}, status=400)

            # Processar evento baseado no tipo
            event_type = event['type']

            if event_type == 'checkout.session.completed':
                StripeService.handle_checkout_session_completed(event)
            elif event_type == 'customer.subscription.updated':
                StripeService.handle_subscription_updated(event)
            elif event_type == 'customer.subscription.deleted':
                StripeService.handle_subscription_deleted(event)
            elif event_type == 'invoice.payment_succeeded':
                StripeService.handle_payment_succeeded(event)
            elif event_type == 'invoice.payment_failed':
                StripeService.handle_payment_failed(event)

            # Salvar evento no banco
            StripeWebhookEvent.objects.create(
                stripe_event_id=event['id'],
                event_type=event_type,
                data=event,
                processed=True,
                processed_at=timezone.now()
            )

            return JsonResponse({'status': 'success'})

        except Exception as e:
            logger.error(f"Erro ao processar webhook: {e}")
            return JsonResponse({'error': 'Erro interno'}, status=500)


# Views auxiliares para compatibilidade com o sistema existente
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subscription_status(request):
    """Obtém o status da assinatura do usuário"""
    try:
        status_info = StripeService.get_subscription_status(request.user)
        return Response({
            'success': True,
            'status': status_info
        })
    except Exception as e:
        logger.error(f"Erro ao obter status da assinatura: {e}")
        return Response({
            'success': False,
            'error': 'Erro ao obter status da assinatura'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_subscriptions(request):
    """Lista todas as assinaturas do usuário"""
    try:
        from .models import StripeSubscription
        subscriptions = StripeSubscription.objects.filter(user=request.user).order_by('-created_at')
        subscription_data = StripeSubscriptionSerializer(subscriptions, many=True).data

        return Response({
            'success': True,
            'subscriptions': subscription_data
        })
    except Exception as e:
        logger.error(f"Erro ao listar assinaturas: {e}")
        return Response({
            'success': False,
            'error': 'Erro ao listar assinaturas'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_history(request):
    """Lista histórico de pagamentos do usuário"""
    try:
        from .models import StripePaymentIntent
        payments = StripePaymentIntent.objects.filter(user=request.user).order_by('-created_at')
        payment_data = StripePaymentIntentSerializer(payments, many=True).data

        return Response({
            'success': True,
            'payments': payment_data
        })
    except Exception as e:
        logger.error(f"Erro ao listar pagamentos: {e}")
        return Response({
            'success': False,
            'error': 'Erro ao listar pagamentos'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
