from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Perfil estendido do usuário"""

    PLAN_CHOICES = [
        ('free', 'Gratuito'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    # Plano e limites
    plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default='free',
        verbose_name="Plano"
    )

    max_shortcuts = models.IntegerField(
        default=50,
        verbose_name="Máximo de Atalhos",
        help_text="Use -1 para ilimitado"
    )

    # Configurações de IA
    ai_enabled = models.BooleanField(
        default=True,
        verbose_name="IA Habilitada"
    )

    ai_model_preference = models.CharField(
        max_length=50,
        default='gpt-3.5-turbo',
        verbose_name="Modelo IA Preferido"
    )

    ai_requests_used = models.PositiveIntegerField(
        default=0,
        verbose_name="Requisições IA Usadas (mês atual)"
    )

    max_ai_requests = models.IntegerField(
        default=100,
        verbose_name="Máximo de Requisições IA por Mês",
        help_text="Use -1 para ilimitado"
    )

    # Configurações de interface
    theme = models.CharField(
        max_length=20,
        choices=[
            ('light', 'Claro'),
            ('dark', 'Escuro'),
            ('auto', 'Automático'),
        ],
        default='auto',
        verbose_name="Tema"
    )

    # Configurações de notificação
    email_notifications = models.BooleanField(
        default=True,
        verbose_name="Notificações por Email"
    )

    # Estatísticas
    total_shortcuts_used = models.PositiveIntegerField(
        default=0,
        verbose_name="Total de Atalhos Usados"
    )

    time_saved_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Tempo Economizado (minutos)"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Perfil do Usuário"
        verbose_name_plural = "Perfis dos Usuários"

    def __str__(self):
        return f"Perfil de {self.user.username}"

    def can_create_shortcut(self):
        """Verifica se o usuário pode criar mais atalhos"""
        if self.max_shortcuts == -1:  # Ilimitado
            return True
        current_shortcuts = self.user.shortcuts.filter(is_active=True).count()
        return current_shortcuts < self.max_shortcuts

    def can_use_ai(self):
        """Verifica se o usuário pode usar IA este mês"""
        if not self.ai_enabled:
            return False
        if self.max_ai_requests == -1:  # Ilimitado
            return True
        return self.ai_requests_used < self.max_ai_requests

    def increment_ai_usage(self):
        """Incrementa o uso de IA"""
        if self.can_use_ai():
            self.ai_requests_used += 1
            self.save(update_fields=['ai_requests_used'])
            return True
        return False

    def reset_monthly_counters(self):
        """Reseta contadores mensais (para ser executado todo mês)"""
        self.ai_requests_used = 0
        self.save(update_fields=['ai_requests_used'])


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Cria automaticamente um perfil quando um usuário é criado"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Salva o perfil quando o usuário é salvo"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
