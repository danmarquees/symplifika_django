from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.models import User
from .models import (
    StripeCustomer,
    StripeProduct,
    StripePrice,
    StripeSubscription,
    StripePaymentIntent,
    StripeWebhookEvent
)
from users.models import UserProfile
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


@admin.register(StripeCustomer)
class StripeCustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_email', 'user_plan', 'stripe_customer_id', 'created_at']
    list_filter = ['created_at', 'user__profile__plan']
    search_fields = ['user__username', 'user__email', 'stripe_customer_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'

    def user_plan(self, obj):
        plan = obj.user.profile.plan
        colors = {
            'free': 'gray',
            'premium': 'blue',
            'enterprise': 'purple'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(plan, 'black'),
            plan.title()
        )
    user_plan.short_description = 'Plano Atual'
    user_plan.admin_order_field = 'user__profile__plan'


@admin.register(StripeProduct)
class StripeProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'stripe_product_id', 'is_active', 'price_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'stripe_product_id', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']

    def price_count(self, obj):
        count = obj.prices.count()
        return format_html(
            '<a href="{}?product__id__exact={}">{} preço(s)</a>',
            reverse('admin:payments_stripeprice_changelist'),
            obj.id,
            count
        )
    price_count.short_description = 'Preços'


@admin.register(StripePrice)
class StripePriceAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'formatted_price', 'interval', 'subscription_count', 'is_active'
    ]
    list_filter = ['is_active', 'currency', 'interval', 'created_at']
    search_fields = ['stripe_price_id', 'product__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['product__name', 'unit_amount']

    def formatted_price(self, obj):
        return f"R$ {obj.amount_in_reais:.2f}"
    formatted_price.short_description = 'Preço'
    formatted_price.admin_order_field = 'unit_amount'

    def subscription_count(self, obj):
        count = obj.subscriptions.filter(status__in=['active', 'trialing']).count()
        if count > 0:
            return format_html(
                '<a href="{}?price__id__exact={}">{} assinatura(s)</a>',
                reverse('admin:payments_stripesubscription_changelist'),
                obj.id,
                count
            )
        return "0"
    subscription_count.short_description = 'Assinaturas Ativas'


@admin.register(StripeSubscription)
class StripeSubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'plan_info', 'status_display', 'current_period_end',
        'days_remaining', 'cancel_at_period_end', 'actions'
    ]
    list_filter = ['status', 'cancel_at_period_end', 'price__product__name', 'created_at']
    search_fields = ['user__username', 'user__email', 'stripe_subscription_id']
    readonly_fields = ['created_at', 'updated_at', 'stripe_subscription_id']
    ordering = ['-created_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'price__product')

    def plan_info(self, obj):
        return format_html(
            '<strong>{}</strong><br>R$ {:.2f}/{}'.format(
                obj.price.product.name,
                obj.price.amount_in_reais,
                obj.price.get_interval_display().lower()
            )
        )
    plan_info.short_description = 'Plano'

    def status_display(self, obj):
        colors = {
            'active': 'green',
            'trialing': 'orange',
            'past_due': 'red',
            'canceled': 'gray',
            'unpaid': 'red'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'

    def actions(self, obj):
        buttons = []

        if obj.status == 'active' and not obj.cancel_at_period_end:
            buttons.append(
                '<a class="button" href="#" onclick="cancelSubscription(\'{}\')">Cancelar</a>'.format(obj.id)
            )

        if obj.status == 'canceled' and obj.current_period_end > timezone.now():
            buttons.append(
                '<a class="button" href="#" onclick="reactivateSubscription(\'{}\')">Reativar</a>'.format(obj.id)
            )

        return format_html(' '.join(buttons))
    actions.short_description = 'Ações'

    def change_user_plan(self, request, queryset):
        """Ação para alterar plano do usuário baseado na assinatura"""
        for subscription in queryset:
            if subscription.is_active:
                plan_map = {
                    'Premium': 'premium',
                    'Enterprise': 'enterprise'
                }
                plan_name = subscription.price.product.name
                if plan_name in plan_map:
                    profile = subscription.user.profile
                    profile.plan = plan_map[plan_name]

                    # Definir limites baseados no plano
                    if plan_map[plan_name] == 'premium':
                        profile.max_shortcuts = 500
                        profile.max_ai_requests = 1000
                    elif plan_map[plan_name] == 'enterprise':
                        profile.max_shortcuts = -1  # Ilimitado
                        profile.max_ai_requests = 10000

                    profile.save()

        self.message_user(request, f'{queryset.count()} planos de usuário atualizados.')

    change_user_plan.short_description = "Atualizar plano do usuário"

    actions = ['change_user_plan']

    class Media:
        js = ('admin/js/subscription_actions.js',)


@admin.register(StripePaymentIntent)
class StripePaymentIntentAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'formatted_amount', 'status_display', 'created_at'
    ]
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['user__username', 'user__email', 'stripe_payment_intent_id']
    readonly_fields = ['created_at', 'updated_at', 'stripe_payment_intent_id', 'client_secret']
    ordering = ['-created_at']

    def formatted_amount(self, obj):
        return f"R$ {obj.amount_in_reais:.2f}"
    formatted_amount.short_description = 'Valor'
    formatted_amount.admin_order_field = 'amount'

    def status_display(self, obj):
        colors = {
            'succeeded': 'green',
            'processing': 'orange',
            'requires_payment_method': 'blue',
            'requires_confirmation': 'blue',
            'requires_action': 'orange',
            'canceled': 'gray',
            'requires_capture': 'orange'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'


@admin.register(StripeWebhookEvent)
class StripeWebhookEventAdmin(admin.ModelAdmin):
    list_display = [
        'event_type', 'stripe_event_id', 'processed_display', 'created_at'
    ]
    list_filter = ['processed', 'event_type', 'created_at']
    search_fields = ['stripe_event_id', 'event_type']
    readonly_fields = ['created_at', 'processed_at', 'stripe_event_id']
    ordering = ['-created_at']

    def processed_display(self, obj):
        if obj.processed:
            return format_html(
                '<span style="color: green;">✓ Processado</span><br><small>{}</small>',
                obj.processed_at.strftime('%d/%m/%Y %H:%M') if obj.processed_at else ''
            )
        return format_html('<span style="color: red;">✗ Pendente</span>')
    processed_display.short_description = 'Status'
    processed_display.admin_order_field = 'processed'

    def mark_as_processed(self, request, queryset):
        updated = queryset.update(processed=True, processed_at=timezone.now())
        self.message_user(request, f'{updated} eventos marcados como processados.')

    def reprocess_events(self, request, queryset):
        """Reprocessar eventos de webhook"""
        from .services import StripeService
        processed_count = 0

        for event in queryset:
            try:
                # Simular reprocessamento do evento
                event_data = event.data
                if event.event_type == 'customer.subscription.updated':
                    StripeService.handle_subscription_updated({'data': event_data})
                elif event.event_type == 'invoice.payment_succeeded':
                    StripeService.handle_payment_succeeded({'data': event_data})

                event.processed = True
                event.processed_at = timezone.now()
                event.save()
                processed_count += 1
            except Exception as e:
                self.message_user(request, f'Erro ao processar evento {event.stripe_event_id}: {e}', level='ERROR')

        if processed_count > 0:
            self.message_user(request, f'{processed_count} eventos reprocessados com sucesso.')

    mark_as_processed.short_description = "Marcar como processado"
    reprocess_events.short_description = "Reprocessar eventos"

    actions = ['mark_as_processed', 'reprocess_events']


# Admin personalizado para UserProfile com controle de planos
class UserProfilePlanAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan_display', 'max_shortcuts', 'max_ai_requests', 'ai_requests_used']
    list_filter = ['plan', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'total_shortcuts_used', 'time_saved_minutes']

    fieldsets = (
        ('Informações do Usuário', {
            'fields': ('user',)
        }),
        ('Plano e Limites', {
            'fields': ('plan', 'max_shortcuts', 'max_ai_requests', 'ai_requests_used')
        }),
        ('Estatísticas', {
            'fields': ('total_shortcuts_used', 'time_saved_minutes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def plan_display(self, obj):
        colors = {
            'free': 'gray',
            'premium': 'blue',
            'enterprise': 'purple'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.plan, 'black'),
            obj.plan.title()
        )
    plan_display.short_description = 'Plano'
    plan_display.admin_order_field = 'plan'

    def upgrade_to_premium(self, request, queryset):
        updated = queryset.update(
            plan='premium',
            max_shortcuts=500,
            max_ai_requests=1000
        )
        self.message_user(request, f'{updated} usuários atualizados para Premium.')

    def upgrade_to_enterprise(self, request, queryset):
        updated = queryset.update(
            plan='enterprise',
            max_shortcuts=-1,
            max_ai_requests=10000
        )
        self.message_user(request, f'{updated} usuários atualizados para Enterprise.')

    def downgrade_to_free(self, request, queryset):
        updated = queryset.update(
            plan='free',
            max_shortcuts=50,
            max_ai_requests=100
        )
        self.message_user(request, f'{updated} usuários rebaixados para Free.')

    def reset_ai_usage(self, request, queryset):
        updated = queryset.update(ai_requests_used=0)
        self.message_user(request, f'Uso de IA resetado para {updated} usuários.')

    upgrade_to_premium.short_description = "Upgrade para Premium"
    upgrade_to_enterprise.short_description = "Upgrade para Enterprise"
    downgrade_to_free.short_description = "Downgrade para Free"
    reset_ai_usage.short_description = "Resetar uso de IA"

    actions = ['upgrade_to_premium', 'upgrade_to_enterprise', 'downgrade_to_free', 'reset_ai_usage']

# Registrar o admin customizado do UserProfile
admin.site.unregister(UserProfile)
admin.site.register(UserProfile, UserProfilePlanAdmin)
