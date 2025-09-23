from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from .models import UserProfile, PlanPricing, Subscription, Payment, PlanUpgradeRequest


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'
    fk_name = 'user'

    fieldsets = (
        ('Plano e Limites', {
            'fields': ('plan', 'max_shortcuts', 'max_ai_requests')
        }),
        ('Configurações de IA', {
            'fields': ('ai_enabled', 'ai_model_preference', 'ai_requests_used')
        }),
        ('Interface', {
            'fields': ('theme', 'email_notifications')
        }),
        ('Sistema de Indicação', {
            'fields': ('referred_by', 'referral_code', 'total_referrals', 'referral_plan_upgrades', 'referral_bonus_earned')
        }),
        ('Estatísticas', {
            'fields': ('total_shortcuts_used', 'time_saved_minutes')
        }),
    )

    readonly_fields = ['total_shortcuts_used', 'time_saved_minutes', 'ai_requests_used', 'total_referrals', 'referral_plan_upgrades', 'referral_bonus_earned']


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = [
        'username', 'email', 'first_name', 'last_name',
        'get_plan', 'get_shortcuts_count', 'is_active', 'date_joined'
    ]
    list_filter = BaseUserAdmin.list_filter + ('profile__plan',)

    @admin.display(description='Plano')
    def get_plan(self, obj):
        if hasattr(obj, 'profile'):
            plan_colors = {
                'free': '#6c757d',
                'premium': '#ffc107',
                'enterprise': '#28a745'
            }
            color = plan_colors.get(obj.profile.plan, '#6c757d')
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color,
                obj.profile.get_plan_display()
            )
        return '-'

    @admin.display(description='Atalhos Ativos')
    def get_shortcuts_count(self, obj):
        count = obj.shortcuts.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:shortcuts_shortcut_changelist') + f'?user__id__exact={obj.id}'
            return format_html('<a href="{}">{}</a>', url, count)
        return count

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'plan_display', 'shortcuts_count', 'ai_requests_used',
        'max_ai_requests', 'total_shortcuts_used', 'referral_stats_display', 'created_at'
    ]
    list_filter = ['plan', 'ai_enabled', 'theme', 'created_at', 'referred_by']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'referral_code']
    readonly_fields = [
        'total_shortcuts_used', 'time_saved_minutes', 'ai_requests_used',
        'total_referrals', 'referral_plan_upgrades', 'referral_bonus_earned',
        'created_at', 'updated_at', 'last_login'
    ]

    fieldsets = (
        ('Usuário', {
            'fields': ('user',)
        }),
        ('Plano e Limites', {
            'fields': ('plan', 'max_shortcuts', 'max_ai_requests')
        }),
        ('Configurações de IA', {
            'fields': ('ai_enabled', 'ai_model_preference', 'ai_requests_used')
        }),
        ('Interface', {
            'fields': ('theme', 'email_notifications')
        }),
        ('Sistema de Indicação', {
            'fields': (
                'referred_by', 'referral_code', 'total_referrals',
                'referral_plan_upgrades', 'referral_bonus_earned'
            ),
            'classes': ('collapse',)
        }),
        ('Estatísticas', {
            'fields': ('total_shortcuts_used', 'time_saved_minutes'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at', 'last_login'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Plano')
    def plan_display(self, obj):
        plan_colors = {
            'free': '#6c757d',
            'premium': '#ffc107',
            'enterprise': '#28a745'
        }
        color = plan_colors.get(obj.plan, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_plan_display()
        )

    @admin.display(description='Indicações')
    def referral_stats_display(self, obj):
        if obj.total_referrals > 0:
            return format_html(
                '<span title="Total: {} | Upgrades: {} | Bônus: R$ {:.2f}">'
                '👥 {} ({}↗)</span>',
                obj.total_referrals,
                obj.referral_plan_upgrades,
                obj.referral_bonus_earned,
                obj.total_referrals,
                obj.referral_plan_upgrades
            )
        return '—'

    @admin.display(description='Atalhos Ativos')
    def shortcuts_count(self, obj):
        count = obj.user.shortcuts.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:shortcuts_shortcut_changelist') + f'?user__id__exact={obj.user.id}'
            return format_html('<a href="{}">{}</a>', url, count)
        return count

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    actions = ['reset_ai_counters', 'upgrade_to_premium', 'generate_referral_codes', 'reset_referral_stats']

    @admin.action(description='Resetar contadores mensais de IA')
    def reset_ai_counters(self, request, queryset):
        for profile in queryset:
            profile.reset_monthly_counters()
        self.message_user(request, f'Contadores de IA resetados para {queryset.count()} usuários.')

    @admin.action(description='Promover para Premium')
    def upgrade_to_premium(self, request, queryset):
        updated = 0
        for profile in queryset:
            if profile.plan == 'free':
                profile.plan = 'premium'
                profile.max_shortcuts = 500
                profile.max_ai_requests = 1000
                profile.save()
                updated += 1
        self.message_user(request, f'{updated} usuários foram promovidos para Premium.')

    @admin.action(description='Gerar códigos de indicação')
    def generate_referral_codes(self, request, queryset):
        generated = 0
        for profile in queryset:
            if not profile.referral_code:
                profile.generate_referral_code()
                generated += 1
        self.message_user(request, f'Códigos de indicação gerados para {generated} usuários.')

    @admin.action(description='Resetar estatísticas de indicação')
    def reset_referral_stats(self, request, queryset):
        updated = 0
        for profile in queryset:
            profile.total_referrals = 0
            profile.referral_plan_upgrades = 0
            profile.referral_bonus_earned = 0
            profile.save(update_fields=['total_referrals', 'referral_plan_upgrades', 'referral_bonus_earned'])
            updated += 1
        self.message_user(request, f'Estatísticas de indicação resetadas para {updated} usuários.')


@admin.register(PlanPricing)
class PlanPricingAdmin(admin.ModelAdmin):
    list_display = ['plan', 'monthly_price', 'yearly_price', 'is_active', 'created_at']
    list_filter = ['plan', 'is_active', 'created_at']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Plano', {
            'fields': ('plan', 'is_active')
        }),
        ('Preços', {
            'fields': ('monthly_price', 'yearly_price')
        }),
        ('Funcionalidades', {
            'fields': ('features',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'status', 'billing_cycle', 'amount', 'next_billing_date', 'is_active_display']
    list_filter = ['plan', 'status', 'billing_cycle', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'is_active_display', 'days_remaining_display']

    fieldsets = (
        ('Usuário', {
            'fields': ('user',)
        }),
        ('Assinatura', {
            'fields': ('plan', 'status', 'billing_cycle', 'amount')
        }),
        ('Datas', {
            'fields': ('start_date', 'end_date', 'next_billing_date')
        }),
        ('Status', {
            'fields': ('is_active_display', 'days_remaining_display'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Ativa', boolean=True)
    def is_active_display(self, obj):
        return obj.is_active

    @admin.display(description='Dias Restantes')
    def days_remaining_display(self, obj):
        return f"{obj.days_remaining} dias"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'payment_method', 'status', 'paid_at', 'created_at']
    list_filter = ['payment_method', 'status', 'created_at', 'paid_at']
    search_fields = ['user__username', 'user__email', 'transaction_id']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('user', 'subscription', 'amount')
        }),
        ('Pagamento', {
            'fields': ('payment_method', 'status', 'transaction_id', 'paid_at')
        }),
        ('Gateway', {
            'fields': ('gateway_response',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'subscription')


@admin.register(PlanUpgradeRequest)
class PlanUpgradeRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_plan', 'requested_plan', 'status', 'amount', 'created_at']
    list_filter = ['current_plan', 'requested_plan', 'status', 'payment_method', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Solicitação', {
            'fields': ('user', 'current_plan', 'requested_plan', 'status')
        }),
        ('Pagamento', {
            'fields': ('payment_method', 'billing_cycle', 'amount')
        }),
        ('Processamento', {
            'fields': ('processed_by', 'processed_at', 'notes')
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['approve_requests', 'reject_requests']

    @admin.action(description='Aprovar solicitações selecionadas')
    def approve_requests(self, request, queryset):
        approved = 0
        for upgrade_request in queryset.filter(status='pending'):
            upgrade_request.approve(processed_by=request.user)
            approved += 1
        self.message_user(request, f'{approved} solicitações foram aprovadas.')

    @admin.action(description='Rejeitar solicitações selecionadas')
    def reject_requests(self, request, queryset):
        rejected = 0
        for upgrade_request in queryset.filter(status='pending'):
            upgrade_request.reject(processed_by=request.user)
            rejected += 1
        self.message_user(request, f'{rejected} solicitações foram rejeitadas.')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'processed_by')


# Desregistra o UserAdmin padrão e registra o customizado
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
