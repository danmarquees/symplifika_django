from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
import json
import csv
import stripe
from django.conf import settings
from .models import StripeSubscription, StripeCustomer
from users.models import UserProfile
from .services import StripeService
import logging

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


@method_decorator(staff_member_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class CancelSubscriptionView(View):
    """View para cancelar assinatura via admin"""

    def post(self, request):
        try:
            data = json.loads(request.body)
            subscription_id = data.get('subscription_id')

            if not subscription_id:
                return JsonResponse({
                    'success': False,
                    'error': 'ID da assinatura é obrigatório'
                })

            subscription = get_object_or_404(StripeSubscription, id=subscription_id)

            # Cancelar no Stripe
            stripe_subscription = stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=True
            )

            # Atualizar no banco local
            subscription.cancel_at_period_end = True
            subscription.save()

            # Log da ação
            logger.info(f"Assinatura cancelada pelo admin: {subscription.stripe_subscription_id} (Usuário: {subscription.user.username})")

            return JsonResponse({
                'success': True,
                'message': 'Assinatura cancelada com sucesso'
            })

        except StripeSubscription.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Assinatura não encontrada'
            })
        except stripe.error.StripeError as e:
            logger.error(f"Erro do Stripe ao cancelar assinatura: {e}")
            return JsonResponse({
                'success': False,
                'error': f'Erro no Stripe: {str(e)}'
            })
        except Exception as e:
            logger.error(f"Erro ao cancelar assinatura: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Erro interno do servidor'
            })


@method_decorator(staff_member_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class ReactivateSubscriptionView(View):
    """View para reativar assinatura via admin"""

    def post(self, request):
        try:
            data = json.loads(request.body)
            subscription_id = data.get('subscription_id')

            if not subscription_id:
                return JsonResponse({
                    'success': False,
                    'error': 'ID da assinatura é obrigatório'
                })

            subscription = get_object_or_404(StripeSubscription, id=subscription_id)

            # Reativar no Stripe
            stripe_subscription = stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=False
            )

            # Atualizar no banco local
            subscription.cancel_at_period_end = False
            subscription.status = stripe_subscription.status
            subscription.save()

            # Log da ação
            logger.info(f"Assinatura reativada pelo admin: {subscription.stripe_subscription_id} (Usuário: {subscription.user.username})")

            return JsonResponse({
                'success': True,
                'message': 'Assinatura reativada com sucesso'
            })

        except StripeSubscription.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Assinatura não encontrada'
            })
        except stripe.error.StripeError as e:
            logger.error(f"Erro do Stripe ao reativar assinatura: {e}")
            return JsonResponse({
                'success': False,
                'error': f'Erro no Stripe: {str(e)}'
            })
        except Exception as e:
            logger.error(f"Erro ao reativar assinatura: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Erro interno do servidor'
            })


@method_decorator(staff_member_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class SyncSubscriptionView(View):
    """View para sincronizar status da assinatura com Stripe"""

    def post(self, request):
        try:
            data = json.loads(request.body)
            subscription_id = data.get('subscription_id')

            if not subscription_id:
                return JsonResponse({
                    'success': False,
                    'error': 'ID da assinatura é obrigatório'
                })

            subscription = get_object_or_404(StripeSubscription, id=subscription_id)

            # Buscar dados no Stripe
            stripe_subscription = stripe.Subscription.retrieve(subscription.stripe_subscription_id)

            # Atualizar dados locais
            subscription.status = stripe_subscription.status
            subscription.current_period_start = timezone.datetime.fromtimestamp(
                stripe_subscription.current_period_start,
                tz=timezone.utc
            )
            subscription.current_period_end = timezone.datetime.fromtimestamp(
                stripe_subscription.current_period_end,
                tz=timezone.utc
            )
            subscription.cancel_at_period_end = stripe_subscription.cancel_at_period_end
            subscription.save()

            # Atualizar plano do usuário se necessário
            if subscription.is_active:
                profile = subscription.user.profile
                plan_map = {
                    'Premium': 'premium',
                    'Enterprise': 'enterprise'
                }
                product_name = subscription.price.product.name.replace(' (TESTE)', '')
                if product_name in plan_map:
                    profile.plan = plan_map[product_name]

                    # Definir limites
                    if plan_map[product_name] == 'premium':
                        profile.max_shortcuts = 500
                        profile.max_ai_requests = 1000
                    elif plan_map[product_name] == 'enterprise':
                        profile.max_shortcuts = -1
                        profile.max_ai_requests = 10000

                    profile.save()

            # Log da ação
            logger.info(f"Assinatura sincronizada pelo admin: {subscription.stripe_subscription_id} (Status: {subscription.status})")

            return JsonResponse({
                'success': True,
                'message': 'Status sincronizado com sucesso',
                'status': subscription.get_status_display()
            })

        except StripeSubscription.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Assinatura não encontrada'
            })
        except stripe.error.StripeError as e:
            logger.error(f"Erro do Stripe ao sincronizar assinatura: {e}")
            return JsonResponse({
                'success': False,
                'error': f'Erro no Stripe: {str(e)}'
            })
        except Exception as e:
            logger.error(f"Erro ao sincronizar assinatura: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Erro interno do servidor'
            })


@staff_member_required
def export_subscriptions(request):
    """Exportar dados de assinaturas para CSV"""
    try:
        # Obter IDs selecionados
        ids = request.GET.get('ids', '').split(',')
        ids = [id.strip() for id in ids if id.strip()]

        if not ids:
            subscriptions = StripeSubscription.objects.all()
        else:
            subscriptions = StripeSubscription.objects.filter(id__in=ids)

        # Preparar resposta CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="assinaturas.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Usuário', 'Email', 'Plano', 'Status', 'Valor', 'Intervalo',
            'Início Período', 'Fim Período', 'Cancelar no Fim', 'Criada em'
        ])

        for sub in subscriptions.select_related('user', 'price__product'):
            writer.writerow([
                sub.id,
                sub.user.username,
                sub.user.email,
                sub.price.product.name,
                sub.get_status_display(),
                f"R$ {sub.price.amount_in_reais:.2f}",
                sub.price.get_interval_display(),
                sub.current_period_start.strftime('%d/%m/%Y %H:%M'),
                sub.current_period_end.strftime('%d/%m/%Y %H:%M'),
                'Sim' if sub.cancel_at_period_end else 'Não',
                sub.created_at.strftime('%d/%m/%Y %H:%M')
            ])

        return response

    except Exception as e:
        logger.error(f"Erro ao exportar assinaturas: {e}")
        return HttpResponse("Erro ao exportar dados", status=500)


@staff_member_required
def subscription_analytics(request):
    """View para análise de assinaturas"""
    from django.db.models import Count, Sum
    from django.http import JsonResponse

    try:
        # Estatísticas gerais
        total_subscriptions = StripeSubscription.objects.count()
        active_subscriptions = StripeSubscription.objects.filter(
            status__in=['active', 'trialing']
        ).count()

        # Assinaturas por status
        status_stats = StripeSubscription.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count')

        # Assinaturas por plano
        plan_stats = StripeSubscription.objects.select_related('price__product').values(
            'price__product__name'
        ).annotate(
            count=Count('id'),
            revenue=Sum('price__unit_amount')
        ).order_by('-count')

        # Receita total
        total_revenue = StripeSubscription.objects.filter(
            status__in=['active', 'trialing']
        ).aggregate(
            total=Sum('price__unit_amount')
        )['total'] or 0

        # Conversões recentes (últimos 30 dias)
        recent_subscriptions = StripeSubscription.objects.filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=30)
        ).count()

        data = {
            'total_subscriptions': total_subscriptions,
            'active_subscriptions': active_subscriptions,
            'conversion_rate': (active_subscriptions / total_subscriptions * 100) if total_subscriptions > 0 else 0,
            'status_distribution': list(status_stats),
            'plan_distribution': list(plan_stats),
            'total_monthly_revenue': total_revenue / 100,  # Converter de centavos para reais
            'recent_conversions': recent_subscriptions
        }

        return JsonResponse(data)

    except Exception as e:
        logger.error(f"Erro ao gerar análises de assinatura: {e}")
        return JsonResponse({'error': 'Erro ao gerar análises'}, status=500)


@staff_member_required
def bulk_subscription_action(request):
    """Ação em massa para assinaturas"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)

    try:
        data = json.loads(request.body)
        subscription_ids = data.get('subscription_ids', [])
        action = data.get('action')

        if not subscription_ids or not action:
            return JsonResponse({
                'success': False,
                'error': 'IDs de assinatura e ação são obrigatórios'
            })

        subscriptions = StripeSubscription.objects.filter(id__in=subscription_ids)
        processed_count = 0
        errors = []

        for subscription in subscriptions:
            try:
                if action == 'cancel':
                    stripe.Subscription.modify(
                        subscription.stripe_subscription_id,
                        cancel_at_period_end=True
                    )
                    subscription.cancel_at_period_end = True
                    subscription.save()
                    processed_count += 1

                elif action == 'reactivate':
                    stripe.Subscription.modify(
                        subscription.stripe_subscription_id,
                        cancel_at_period_end=False
                    )
                    subscription.cancel_at_period_end = False
                    subscription.save()
                    processed_count += 1

                elif action == 'sync':
                    stripe_sub = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
                    subscription.status = stripe_sub.status
                    subscription.current_period_start = timezone.datetime.fromtimestamp(
                        stripe_sub.current_period_start, tz=timezone.utc
                    )
                    subscription.current_period_end = timezone.datetime.fromtimestamp(
                        stripe_sub.current_period_end, tz=timezone.utc
                    )
                    subscription.cancel_at_period_end = stripe_sub.cancel_at_period_end
                    subscription.save()
                    processed_count += 1

            except Exception as e:
                errors.append(f"Erro na assinatura {subscription.id}: {str(e)}")

        return JsonResponse({
            'success': True,
            'processed_count': processed_count,
            'errors': errors,
            'message': f'{processed_count} assinaturas processadas com sucesso'
        })

    except Exception as e:
        logger.error(f"Erro na ação em massa de assinaturas: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Erro interno do servidor'
        })
