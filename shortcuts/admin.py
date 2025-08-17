from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Category, Shortcut, ShortcutUsage, AIEnhancementLog


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'color_display', 'shortcuts_count', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']

    def color_display(self, obj):
        return format_html(
            '<span style="color: {}; font-weight: bold;">● {}</span>',
            obj.color,
            obj.color
        )
    color_display.short_description = 'Cor'

    def shortcuts_count(self, obj):
        count = obj.shortcuts.filter(is_active=True).count()
        url = reverse('admin:shortcuts_shortcut_changelist') + f'?category__id__exact={obj.id}'
        return format_html('<a href="{}">{} atalhos</a>', url, count)
    shortcuts_count.short_description = 'Atalhos Ativos'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Shortcut)
class ShortcutAdmin(admin.ModelAdmin):
    list_display = [
        'trigger', 'title', 'user', 'category', 'expansion_type',
        'is_active', 'use_count', 'last_used', 'created_at'
    ]
    list_filter = [
        'expansion_type', 'is_active', 'category',
        'created_at', 'last_used'
    ]
    search_fields = ['trigger', 'title', 'content', 'user__username']
    readonly_fields = ['use_count', 'last_used', 'created_at', 'updated_at']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('trigger', 'title', 'user', 'category', 'is_active')
        }),
        ('Conteúdo', {
            'fields': ('content', 'expanded_content', 'expansion_type')
        }),
        ('Configurações de IA', {
            'fields': ('ai_prompt',),
            'classes': ('collapse',)
        }),
        ('Variáveis Dinâmicas', {
            'fields': ('variables',),
            'classes': ('collapse',)
        }),
        ('Estatísticas', {
            'fields': ('use_count', 'last_used'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'category')

    actions = ['activate_shortcuts', 'deactivate_shortcuts']

    def activate_shortcuts(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} atalhos foram ativados.')
    activate_shortcuts.short_description = 'Ativar atalhos selecionados'

    def deactivate_shortcuts(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} atalhos foram desativados.')
    deactivate_shortcuts.short_description = 'Desativar atalhos selecionados'


@admin.register(ShortcutUsage)
class ShortcutUsageAdmin(admin.ModelAdmin):
    list_display = ['shortcut', 'user', 'used_at', 'context']
    list_filter = ['used_at', 'shortcut__expansion_type']
    search_fields = ['shortcut__trigger', 'shortcut__title', 'user__username', 'context']
    readonly_fields = ['used_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('shortcut', 'user')

    def has_add_permission(self, request):
        return False  # Registros criados automaticamente


@admin.register(AIEnhancementLog)
class AIEnhancementLogAdmin(admin.ModelAdmin):
    list_display = [
        'shortcut', 'ai_model_used', 'processing_time_display',
        'content_preview', 'created_at'
    ]
    list_filter = ['ai_model_used', 'created_at']
    search_fields = ['shortcut__trigger', 'shortcut__title', 'original_content']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('shortcut', 'ai_model_used', 'processing_time', 'created_at')
        }),
        ('Conteúdo', {
            'fields': ('original_content', 'enhanced_content')
        }),
    )

    def processing_time_display(self, obj):
        return f'{obj.processing_time:.2f}s'
    processing_time_display.short_description = 'Tempo de Processamento'

    def content_preview(self, obj):
        original_preview = obj.original_content[:50] + '...' if len(obj.original_content) > 50 else obj.original_content
        enhanced_preview = obj.enhanced_content[:50] + '...' if len(obj.enhanced_content) > 50 else obj.enhanced_content

        return format_html(
            '<strong>Original:</strong> {}<br><strong>Expandido:</strong> {}',
            original_preview,
            enhanced_preview
        )
    content_preview.short_description = 'Preview do Conteúdo'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('shortcut')

    def has_add_permission(self, request):
        return False  # Registros criados automaticamente


# Configurações gerais do admin
admin.site.site_header = 'Symplifika - Administração'
admin.site.site_title = 'Symplifika Admin'
admin.site.index_title = 'Painel de Administração'
