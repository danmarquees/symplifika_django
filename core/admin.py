from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import AppSettings, ActivityLog, SystemStats


@admin.register(AppSettings)
class AppSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'value_preview', 'description_preview', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['key', 'value', 'description']
    readonly_fields = ['created_at', 'updated_at']

    @admin.display(description='Valor')
    def value_preview(self, obj):
        if len(obj.value) > 50:
            return obj.value[:50] + '...'
        return obj.value

    @admin.display(description='Descrição')
    def description_preview(self, obj):
        if len(obj.description) > 30:
            return obj.description[:30] + '...'
        return obj.description


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_display', 'description_preview', 'ip_address', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['user__username', 'user__email', 'description', 'ip_address']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('user', 'action', 'description')
        }),
        ('Metadados', {
            'fields': ('metadata', 'ip_address', 'user_agent')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )

    @admin.display(description='Ação')
    def action_display(self, obj):
        return obj.get_action_display()

    @admin.display(description='Descrição')
    def description_preview(self, obj):
        if len(obj.description) > 50:
            return obj.description[:50] + '...'
        return obj.description

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    def has_add_permission(self, request):
        return False  # Logs são criados automaticamente


@admin.register(SystemStats)
class SystemStatsAdmin(admin.ModelAdmin):
    list_display = [
        'date', 'total_users', 'active_users', 'total_shortcuts',
        'total_shortcut_uses', 'total_ai_requests', 'created_at'
    ]
    list_filter = ['date', 'created_at']
    readonly_fields = ['created_at']

    def has_add_permission(self, request):
        return False  # Stats são geradas automaticamente

    def has_change_permission(self, request, obj=None):
        return False  # Stats não podem ser editadas
