from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class AppSettings(models.Model):
    """Configurações globais da aplicação"""

    key = models.CharField(max_length=100, unique=True, verbose_name="Chave")
    value = models.TextField(verbose_name="Valor")
    description = models.TextField(blank=True, verbose_name="Descrição")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuração"
        verbose_name_plural = "Configurações"
        ordering = ['key']

    def __str__(self):
        return f"{self.key}: {self.value[:50]}"

    @classmethod
    def get_setting(cls, key, default=None):
        """Obtém uma configuração pelo nome da chave"""
        try:
            setting = cls.objects.get(key=key)
            return setting.value
        except cls.DoesNotExist:
            return default

    @classmethod
    def set_setting(cls, key, value, description=""):
        """Define uma configuração"""
        setting, created = cls.objects.get_or_create(
            key=key,
            defaults={'value': value, 'description': description}
        )
        if not created:
            setting.value = value
            setting.description = description
            setting.save()
        return setting


class ActivityLog(models.Model):
    """Log de atividades do sistema"""

    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('shortcut_created', 'Atalho Criado'),
        ('shortcut_used', 'Atalho Usado'),
        ('shortcut_deleted', 'Atalho Deletado'),
        ('ai_enhancement', 'Expansão por IA'),
        ('profile_updated', 'Perfil Atualizado'),
        ('plan_upgraded', 'Plano Atualizado'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="activity_logs"
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Log de Atividade"
        verbose_name_plural = "Logs de Atividades"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} - {self.created_at}"

    @classmethod
    def log_activity(cls, user, action, description="", metadata=None, request=None):
        """Método helper para registrar atividades"""
        log_data = {
            'user': user,
            'action': action,
            'description': description,
            'metadata': metadata or {}
        }

        if request:
            # Extrai IP do request
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')

            log_data['ip_address'] = ip
            log_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')

        return cls.objects.create(**log_data)


class SystemStats(models.Model):
    """Estatísticas do sistema"""

    total_users = models.PositiveIntegerField(default=0)
    active_users = models.PositiveIntegerField(default=0)
    total_shortcuts = models.PositiveIntegerField(default=0)
    total_shortcut_uses = models.PositiveIntegerField(default=0)
    total_ai_requests = models.PositiveIntegerField(default=0)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Estatística do Sistema"
        verbose_name_plural = "Estatísticas do Sistema"
        ordering = ['-date']
        unique_together = ['date']

    def __str__(self):
        return f"Stats {self.date}"

    @classmethod
    def update_daily_stats(cls):
        """Atualiza as estatísticas diárias"""
        from django.contrib.auth.models import User
        from shortcuts.models import Shortcut, ShortcutUsage
        from users.models import UserProfile

        today = timezone.now().date()

        # Calcula estatísticas
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        total_shortcuts = Shortcut.objects.filter(is_active=True).count()
        total_shortcut_uses = sum(Shortcut.objects.values_list('use_count', flat=True))
        total_ai_requests = sum(UserProfile.objects.values_list('ai_requests_used', flat=True))

        # Cria ou atualiza registro
        stats, created = cls.objects.get_or_create(
            date=today,
            defaults={
                'total_users': total_users,
                'active_users': active_users,
                'total_shortcuts': total_shortcuts,
                'total_shortcut_uses': total_shortcut_uses,
                'total_ai_requests': total_ai_requests,
            }
        )

        if not created:
            stats.total_users = total_users
            stats.active_users = active_users
            stats.total_shortcuts = total_shortcuts
            stats.total_shortcut_uses = total_shortcut_uses
            stats.total_ai_requests = total_ai_requests
            stats.save()

        return stats
