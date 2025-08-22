from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


class StripeCustomer(models.Model):
    """Cliente do Stripe"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='stripe_customer',
        verbose_name="Usuário"
    )
    
    stripe_customer_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="ID do Cliente Stripe"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cliente Stripe"
        verbose_name_plural = "Clientes Stripe"
    
    def __str__(self):
        return f"{self.user.username} - {self.stripe_customer_id}"


class StripeProduct(models.Model):
    """Produto do Stripe"""
    
    name = models.CharField(
        max_length=100,
        verbose_name="Nome"
    )
    
    stripe_product_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="ID do Produto Stripe"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Descrição"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Produto Stripe"
        verbose_name_plural = "Produtos Stripe"
    
    def __str__(self):
        return f"{self.name} - {self.stripe_product_id}"


class StripePrice(models.Model):
    """Preço do Stripe"""
    
    INTERVAL_CHOICES = [
        ('month', 'Mensal'),
        ('year', 'Anual'),
        ('one-time', 'Único'),
    ]
    
    product = models.ForeignKey(
        StripeProduct,
        on_delete=models.CASCADE,
        related_name='prices',
        verbose_name="Produto"
    )
    
    stripe_price_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="ID do Preço Stripe"
    )
    
    unit_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor Unitário (centavos)"
    )
    
    currency = models.CharField(
        max_length=3,
        default='brl',
        verbose_name="Moeda"
    )
    
    interval = models.CharField(
        max_length=20,
        choices=INTERVAL_CHOICES,
        verbose_name="Intervalo"
    )
    
    interval_count = models.PositiveIntegerField(
        default=1,
        verbose_name="Contador de Intervalo"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Preço Stripe"
        verbose_name_plural = "Preços Stripe"
    
    def __str__(self):
        return f"{self.product.name} - {self.get_interval_display()} - R$ {self.unit_amount / 100:.2f}"
    
    @property
    def amount_in_reais(self):
        """Retorna o valor em reais"""
        return self.unit_amount / 100


class StripeSubscription(models.Model):
    """Assinatura do Stripe"""
    
    STATUS_CHOICES = [
        ('incomplete', 'Incompleta'),
        ('incomplete_expired', 'Incompleta Expirada'),
        ('trialing', 'Período de Teste'),
        ('active', 'Ativa'),
        ('past_due', 'Vencida'),
        ('canceled', 'Cancelada'),
        ('unpaid', 'Não Paga'),
        ('paused', 'Pausada'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='stripe_subscriptions',
        verbose_name="Usuário"
    )
    
    stripe_subscription_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="ID da Assinatura Stripe"
    )
    
    price = models.ForeignKey(
        StripePrice,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name="Preço"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        verbose_name="Status"
    )
    
    current_period_start = models.DateTimeField(
        verbose_name="Início do Período Atual"
    )
    
    current_period_end = models.DateTimeField(
        verbose_name="Fim do Período Atual"
    )
    
    cancel_at_period_end = models.BooleanField(
        default=False,
        verbose_name="Cancelar no Fim do Período"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Assinatura Stripe"
        verbose_name_plural = "Assinaturas Stripe"
    
    def __str__(self):
        return f"{self.user.username} - {self.price.product.name} - {self.get_status_display()}"
    
    @property
    def is_active(self):
        """Verifica se a assinatura está ativa"""
        return self.status in ['active', 'trialing']
    
    @property
    def days_remaining(self):
        """Dias restantes da assinatura"""
        if self.current_period_end > timezone.now():
            return (self.current_period_end - timezone.now()).days
        return 0


class StripePaymentIntent(models.Model):
    """Intenção de Pagamento do Stripe"""
    
    STATUS_CHOICES = [
        ('requires_payment_method', 'Requer Método de Pagamento'),
        ('requires_confirmation', 'Requer Confirmação'),
        ('requires_action', 'Requer Ação'),
        ('processing', 'Processando'),
        ('requires_capture', 'Requer Captura'),
        ('canceled', 'Cancelado'),
        ('succeeded', 'Sucesso'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payment_intents',
        verbose_name="Usuário"
    )
    
    stripe_payment_intent_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="ID da Intenção de Pagamento Stripe"
    )
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor (centavos)"
    )
    
    currency = models.CharField(
        max_length=3,
        default='brl',
        verbose_name="Moeda"
    )
    
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        verbose_name="Status"
    )
    
    payment_method_types = models.JSONField(
        default=list,
        verbose_name="Tipos de Método de Pagamento"
    )
    
    client_secret = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Segredo do Cliente"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Intenção de Pagamento Stripe"
        verbose_name_plural = "Intenções de Pagamento Stripe"
    
    def __str__(self):
        return f"{self.user.username} - R$ {self.amount / 100:.2f} - {self.get_status_display()}"
    
    @property
    def amount_in_reais(self):
        """Retorna o valor em reais"""
        return self.amount / 100


class StripeWebhookEvent(models.Model):
    """Eventos de Webhook do Stripe"""
    
    stripe_event_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="ID do Evento Stripe"
    )
    
    event_type = models.CharField(
        max_length=100,
        verbose_name="Tipo do Evento"
    )
    
    data = models.JSONField(
        verbose_name="Dados do Evento"
    )
    
    processed = models.BooleanField(
        default=False,
        verbose_name="Processado"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Processamento"
    )
    
    class Meta:
        verbose_name = "Evento de Webhook Stripe"
        verbose_name_plural = "Eventos de Webhook Stripe"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.event_type} - {self.stripe_event_id}" 