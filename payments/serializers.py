from rest_framework import serializers
from .models import (
    StripeCustomer,
    StripeProduct,
    StripePrice,
    StripeSubscription,
    StripePaymentIntent
)
from users.models import UserProfile


class StripeProductSerializer(serializers.ModelSerializer):
    """Serializer para produtos do Stripe"""
    
    class Meta:
        model = StripeProduct
        fields = ['id', 'name', 'description', 'is_active']


class StripePriceSerializer(serializers.ModelSerializer):
    """Serializer para preços do Stripe"""
    
    product = StripeProductSerializer(read_only=True)
    amount_in_reais = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    
    class Meta:
        model = StripePrice
        fields = [
            'id', 'product', 'stripe_price_id', 'unit_amount',
            'currency', 'interval', 'interval_count', 'is_active',
            'amount_in_reais'
        ]


class StripeCustomerSerializer(serializers.ModelSerializer):
    """Serializer para clientes do Stripe"""
    
    user = serializers.StringRelatedField()
    
    class Meta:
        model = StripeCustomer
        fields = ['id', 'user', 'stripe_customer_id', 'created_at']


class StripeSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer para assinaturas do Stripe"""
    
    user = serializers.StringRelatedField()
    price = StripePriceSerializer(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = StripeSubscription
        fields = [
            'id', 'user', 'price', 'status', 'current_period_start',
            'current_period_end', 'cancel_at_period_end', 'days_remaining',
            'created_at'
        ]


class StripePaymentIntentSerializer(serializers.ModelSerializer):
    """Serializer para intenções de pagamento do Stripe"""
    
    user = serializers.StringRelatedField()
    amount_in_reais = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    
    class Meta:
        model = StripePaymentIntent
        fields = [
            'id', 'user', 'stripe_payment_intent_id', 'amount',
            'currency', 'status', 'payment_method_types', 'client_secret',
            'amount_in_reais', 'created_at'
        ]


class CreateSubscriptionSerializer(serializers.Serializer):
    """Serializer para criar assinatura"""
    
    price_id = serializers.CharField(
        help_text="ID do preço do Stripe"
    )
    payment_method_id = serializers.CharField(
        help_text="ID do método de pagamento do Stripe"
    )
    billing_cycle = serializers.ChoiceField(
        choices=[('month', 'Mensal'), ('year', 'Anual')],
        default='month',
        help_text="Ciclo de cobrança"
    )


class CancelSubscriptionSerializer(serializers.Serializer):
    """Serializer para cancelar assinatura"""
    
    cancel_at_period_end = serializers.BooleanField(
        default=True,
        help_text="Cancelar no fim do período atual"
    )


class PaymentMethodSerializer(serializers.Serializer):
    """Serializer para métodos de pagamento"""
    
    payment_method_id = serializers.CharField(
        help_text="ID do método de pagamento do Stripe"
    )
    is_default = serializers.BooleanField(
        default=False,
        help_text="Definir como método padrão"
    )


class PlanUpgradeSerializer(serializers.Serializer):
    """Serializer para upgrade de plano"""
    
    plan = serializers.ChoiceField(
        choices=UserProfile.PLAN_CHOICES,
        help_text="Plano desejado"
    )
    billing_cycle = serializers.ChoiceField(
        choices=[('month', 'Mensal'), ('year', 'Anual')],
        default='month',
        help_text="Ciclo de cobrança"
    )
    payment_method_id = serializers.CharField(
        required=False,
        help_text="ID do método de pagamento (opcional se já existir)"
    ) 