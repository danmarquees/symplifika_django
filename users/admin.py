from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from .models import UserProfile


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
        ('Estatísticas', {
            'fields': ('total_shortcuts_used', 'time_saved_minutes')
        }),
    )

    readonly_fields = ['total_shortcuts_used', 'time_saved_minutes', 'ai_requests_used']


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = [
        'username', 'email', 'first_name', 'last_name',
        'get_plan', 'get_shortcuts_count', 'is_active', 'date_joined'
    ]
    list_filter = BaseUserAdmin.list_filter + ('profile__plan',)

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
    get_plan.short_description = 'Plano'

    def get_shortcuts_count(self, obj):
        count = obj.shortcuts.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:shortcuts_shortcut_changelist') + f'?user__id__exact={obj.id}'
            return format_html('<a href="{}">{}</a>', url, count)
        return count
    get_shortcuts_count.short_description = 'Atalhos Ativos'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'plan_display', 'shortcuts_count', 'ai_requests_used',
        'max_ai_requests', 'total_shortcuts_used', 'created_at'
    ]
    list_filter = ['plan', 'ai_enabled', 'theme', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = [
        'total_shortcuts_used', 'time_saved_minutes', 'ai_requests_used',
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
        ('Estatísticas', {
            'fields': ('total_shortcuts_used', 'time_saved_minutes'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at', 'last_login'),
            'classes': ('collapse',)
        }),
    )

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
    plan_display.short_description = 'Plano'

    def shortcuts_count(self, obj):
        count = obj.user.shortcuts.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:shortcuts_shortcut_changelist') + f'?user__id__exact={obj.user.id}'
            return format_html('<a href="{}">{}</a>', url, count)
        return count
    shortcuts_count.short_description = 'Atalhos Ativos'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    actions = ['reset_ai_counters', 'upgrade_to_premium']

    def reset_ai_counters(self, request, queryset):
        for profile in queryset:
            profile.reset_monthly_counters()
        self.message_user(request, f'Contadores de IA resetados para {queryset.count()} usuários.')
    reset_ai_counters.short_description = 'Resetar contadores mensais de IA'

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
    upgrade_to_premium.short_description = 'Promover para Premium'


# Desregistra o UserAdmin padrão e registra o customizado
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
