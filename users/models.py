from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal
import os
from PIL import Image
from django.core.files.storage import default_storage


def user_avatar_path(instance, filename):
    """Gera o caminho para o upload do avatar do usuário"""
    ext = filename.split('.')[-1]
    filename = f'avatar_{instance.user.id}.{ext}'
    return os.path.join('avatars', filename)


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

    # Informações pessoais
    avatar = models.ImageField(
        upload_to=user_avatar_path,
        null=True,
        blank=True,
        verbose_name="Avatar",
        help_text="Imagem do perfil (máx. 5MB)"
    )

    bio = models.TextField(
        max_length=500,
        blank=True,
        verbose_name="Biografia",
        help_text="Conte um pouco sobre você (máx. 500 caracteres)"
    )

    location = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Localização"
    )

    website = models.URLField(
        blank=True,
        verbose_name="Website"
    )

    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Nascimento"
    )

    # Configurações de privacidade
    public_profile = models.BooleanField(
        default=True,
        verbose_name="Perfil Público",
        help_text="Permitir que outros usuários vejam seu perfil"
    )

    show_email = models.BooleanField(
        default=False,
        verbose_name="Mostrar Email",
        help_text="Exibir email no perfil público"
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

    # Sistema de Indicação
    referred_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referred_users',
        verbose_name="Indicado por",
        help_text="Usuário que fez a indicação"
    )

    referral_code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Código de Indicação",
        help_text="Código único para indicar outros usuários"
    )

    total_referrals = models.PositiveIntegerField(
        default=0,
        verbose_name="Total de Indicações",
        help_text="Número total de usuários indicados"
    )

    referral_plan_upgrades = models.PositiveIntegerField(
        default=0,
        verbose_name="Upgrades de Indicados",
        help_text="Número de indicados que fizeram upgrade de plano"
    )

    referral_bonus_earned = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Bônus Ganho por Indicação",
        help_text="Valor total ganho em bônus por indicações"
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

    def get_avatar_url(self):
        """Retorna a URL do avatar ou None se não existir"""
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return None

    def get_avatar_or_initial(self):
        """Retorna URL do avatar ou inicial do nome"""
        avatar_url = self.get_avatar_url()
        if avatar_url:
            return avatar_url

        # Retorna inicial do nome
        name = self.user.get_full_name() or self.user.username
        return name[0].upper() if name else 'U'

    @property
    def max_ai_requests_free(self):
        """Retorna o limite de requisições IA para planos gratuitos"""
        from core.models import AppSettings
        try:
            setting = AppSettings.objects.get(key='max_ai_requests_free')
            return int(setting.value)
        except (AppSettings.DoesNotExist, ValueError):
            return 50  # Valor padrão

    def delete_avatar(self):
        """Remove o avatar atual"""
        if self.avatar:
            # Remove o arquivo físico
            if default_storage.exists(self.avatar.name):
                default_storage.delete(self.avatar.name)
            # Remove a referência do banco
            self.avatar = None
            self.save(update_fields=['avatar'])
            return True
        return False

    def save(self, *args, **kwargs):
        """Override do save para processar avatar"""
        # Se há um novo avatar, processa a imagem
        if self.avatar:
            self._process_avatar()
        super().save(*args, **kwargs)

    def _process_avatar(self):
        """Processa e redimensiona o avatar"""
        if not self.avatar:
            return

        try:
            # Abre a imagem
            img = Image.open(self.avatar)

            # Converte para RGB se necessário
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')

            # Redimensiona mantendo proporção
            max_size = (400, 400)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Salva a imagem processada
            from io import BytesIO
            from django.core.files.base import ContentFile

            output = BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)

            # Substitui o arquivo original
            self.avatar.save(
                self.avatar.name,
                ContentFile(output.read()),
                save=False
            )

        except Exception as e:
            # Em caso de erro, mantém o arquivo original
            print(f"Erro ao processar avatar: {e}")

    @property
    def age(self):
        """Calcula a idade baseada na data de nascimento"""
        if self.birth_date:
            from datetime import date
            today = date.today()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None

    @property
    def full_location(self):
        """Retorna localização formatada"""
        return self.location if self.location else "Não informado"

    def generate_referral_code(self):
        """Gera um código único de indicação"""
        import string
        import random

        if self.referral_code:
            return self.referral_code

        # Gera código baseado no ID do usuário e caracteres aleatórios
        base_code = f"{self.user.username[:3].upper()}{self.user.id}"
        random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        self.referral_code = f"{base_code}{random_chars}"

        # Verifica se o código já existe e gera um novo se necessário
        while UserProfile.objects.filter(referral_code=self.referral_code).exclude(id=self.id).exists():
            random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            self.referral_code = f"{base_code}{random_chars}"

        self.save()
        return self.referral_code

    def process_referral_upgrade(self, referred_user, bonus_amount=0):
        """Processa o upgrade de um usuário indicado"""
        try:
            from decimal import Decimal

            # Incrementa o contador de upgrades de indicados
            self.referral_plan_upgrades += 1

            # Adiciona o bônus se especificado
            if bonus_amount > 0:
                # Garantir que o valor é Decimal
                if isinstance(bonus_amount, (int, float)):
                    bonus_amount = Decimal(str(bonus_amount))
                self.referral_bonus_earned = self.referral_bonus_earned + bonus_amount

            self.save()

            # Log da ação
            from django.utils import timezone
            print(f"[{timezone.now()}] Usuário {self.user.username} ganhou bônus de R$ {bonus_amount} pela indicação de {referred_user.username}")

            # Criar notificação para o indicador (se existir sistema de notificações)
            self._create_referral_notification(referred_user, float(bonus_amount))

            return True
        except Exception as e:
            print(f"Erro ao processar upgrade de indicação: {e}")
            return False

    def _create_referral_notification(self, referred_user, bonus_amount):
        """Cria notificação para o indicador"""
        try:
            # Importa aqui para evitar import circular
            from notifications.models import Notification

            message = f"Parabéns! {referred_user.first_name or referred_user.username} fez upgrade para plano pago"
            if bonus_amount > 0:
                message += f" e você ganhou R$ {bonus_amount:.2f} de bônus!"

            Notification.objects.create(
                user=self.user,
                title="Indicação realizada com sucesso!",
                message=message,
                notification_type='referral_bonus'
            )
        except (ImportError, Exception) as e:
            # Sistema de notificações não existe ou outro erro
            print(f"Sistema de notificações não disponível: {e}")

    def get_referral_stats(self):
        """Retorna estatísticas de indicação do usuário"""
        return {
            'total_referrals': self.total_referrals,
            'plan_upgrades': self.referral_plan_upgrades,
            'bonus_earned': float(self.referral_bonus_earned),
            'conversion_rate': (self.referral_plan_upgrades / self.total_referrals * 100) if self.total_referrals > 0 else 0,
            'referral_code': self.referral_code or self.generate_referral_code()
        }

    def add_referral(self, referred_user):
        """Adiciona um novo usuário indicado"""
        if referred_user.profile.referred_by is None:
            referred_user.profile.referred_by = self.user
            referred_user.profile.save()

            self.total_referrals += 1
            self.save()

            return True
        return False


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Cria automaticamente um perfil quando um usuário é criado"""
    if created:
        profile = UserProfile.objects.create(user=instance)
        # Gera código de indicação automaticamente
        profile.generate_referral_code()


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Salva o perfil quando o usuário é salvo"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


class PlanPricing(models.Model):
    """Preços dos planos"""

    plan = models.CharField(
        max_length=20,
        choices=UserProfile.PLAN_CHOICES,
        unique=True,
        verbose_name="Plano"
    )

    monthly_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Preço Mensal (R$)"
    )

    yearly_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Preço Anual (R$)"
    )

    features = models.JSONField(
        default=dict,
        verbose_name="Funcionalidades",
        help_text="Lista de funcionalidades do plano"
    )

    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Preço de Plano"
        verbose_name_plural = "Preços de Planos"
        ordering = ['monthly_price']

    def __str__(self):
        return f"{self.get_plan_display()} - R$ {self.monthly_price}/mês"


class Subscription(models.Model):
    """Assinatura do usuário"""

    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('active', 'Ativa'),
        ('cancelled', 'Cancelada'),
        ('expired', 'Expirada'),
        ('suspended', 'Suspensa'),
    ]

    BILLING_CYCLE_CHOICES = [
        ('monthly', 'Mensal'),
        ('yearly', 'Anual'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name="Usuário"
    )

    plan = models.CharField(
        max_length=20,
        choices=UserProfile.PLAN_CHOICES,
        verbose_name="Plano"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status"
    )

    billing_cycle = models.CharField(
        max_length=20,
        choices=BILLING_CYCLE_CHOICES,
        default='monthly',
        verbose_name="Ciclo de Cobrança"
    )

    start_date = models.DateTimeField(verbose_name="Data de Início")
    end_date = models.DateTimeField(verbose_name="Data de Fim")
    next_billing_date = models.DateTimeField(verbose_name="Próxima Cobrança")

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Assinatura"
        verbose_name_plural = "Assinaturas"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_plan_display()}"

    @property
    def is_active(self):
        """Verifica se a assinatura está ativa"""
        return (
            self.status == 'active' and
            self.end_date > timezone.now()
        )

    @property
    def days_remaining(self):
        """Dias restantes da assinatura"""
        if self.end_date > timezone.now():
            return (self.end_date - timezone.now()).days
        return 0


class Payment(models.Model):
    """Histórico de pagamentos"""

    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('processing', 'Processando'),
        ('completed', 'Concluído'),
        ('failed', 'Falhou'),
        ('cancelled', 'Cancelado'),
        ('refunded', 'Reembolsado'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Cartão de Crédito'),
        ('debit_card', 'Cartão de Débito'),
        ('pix', 'PIX'),
        ('boleto', 'Boleto Bancário'),
        ('paypal', 'PayPal'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="Usuário"
    )

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="Assinatura"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor"
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name="Método de Pagamento"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status"
    )

    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="ID da Transação"
    )

    gateway_response = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Resposta do Gateway"
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data do Pagamento"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - R$ {self.amount} - {self.get_status_display()}"


class PlanUpgradeRequest(models.Model):
    """Solicitações de upgrade de plano"""

    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
        ('cancelled', 'Cancelado'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='upgrade_requests',
        verbose_name="Usuário"
    )

    current_plan = models.CharField(
        max_length=20,
        choices=UserProfile.PLAN_CHOICES,
        verbose_name="Plano Atual"
    )

    requested_plan = models.CharField(
        max_length=20,
        choices=UserProfile.PLAN_CHOICES,
        verbose_name="Plano Solicitado"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status"
    )

    payment_method = models.CharField(
        max_length=20,
        choices=Payment.PAYMENT_METHOD_CHOICES,
        verbose_name="Método de Pagamento"
    )

    billing_cycle = models.CharField(
        max_length=20,
        choices=Subscription.BILLING_CYCLE_CHOICES,
        default='monthly',
        verbose_name="Ciclo de Cobrança"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor"
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observações"
    )

    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_upgrades',
        verbose_name="Processado por"
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Processamento"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Solicitação de Upgrade"
        verbose_name_plural = "Solicitações de Upgrade"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.current_plan} → {self.requested_plan}"

    def approve(self, processed_by=None):
        """Aprova a solicitação de upgrade"""
        self.status = 'approved'
        self.processed_by = processed_by
        self.processed_at = timezone.now()
        self.save()

        # Atualiza o plano do usuário
        profile = self.user.profile
        old_plan = profile.plan
        profile.plan = self.requested_plan

        # Atualiza limites baseado no plano
        if self.requested_plan == 'premium':
            profile.max_shortcuts = 500
            profile.max_ai_requests = 1000
        elif self.requested_plan == 'enterprise':
            profile.max_shortcuts = -1
            profile.max_ai_requests = -1

        profile.save()

        # Processar bônus de indicação se o usuário foi indicado
        if profile.referred_by and old_plan == 'free':
            referrer_profile = profile.referred_by.profile

            # Definir bônus baseado no plano
            bonus_amount = 0
            if self.requested_plan == 'premium':
                bonus_amount = 10.00  # R$ 10 de bônus
            elif self.requested_plan == 'enterprise':
                bonus_amount = 25.00  # R$ 25 de bônus

            # Processar o bônus de indicação
            referrer_profile.process_referral_upgrade(self.user, bonus_amount)

    def reject(self, processed_by=None, notes=""):
        """Rejeita a solicitação de upgrade"""
        self.status = 'rejected'
        self.processed_by = processed_by
        self.processed_at = timezone.now()
        if notes:
            self.notes = notes
        self.save()
