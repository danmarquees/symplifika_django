from django.contrib import admin
from .models import (
    StripeCustomer,
    StripeProduct,
    StripePrice,
    StripeSubscription,
    StripePaymentIntent,
    StripeWebhookEvent
)


@admin.register(StripeCustomer)
class StripeCustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'stripe_customer_id', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email', 'stripe_customer_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(StripeProduct)
class StripeProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'stripe_product_id', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'stripe_product_id', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']


@admin.register(StripePrice)
class StripePriceAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'stripe_price_id', 'unit_amount', 'currency',
        'interval', 'is_active'
    ]
    list_filter = ['is_active', 'currency', 'interval', 'created_at']
    search_fields = ['stripe_price_id', 'product__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['product__name', 'unit_amount']


@admin.register(StripeSubscription)
class StripeSubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'price', 'status', 'current_period_end',
        'cancel_at_period_end', 'created_at'
    ]
    list_filter = ['status', 'cancel_at_period_end', 'created_at']
    search_fields = ['user__username', 'stripe_subscription_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'price__product')


@admin.register(StripePaymentIntent)
class StripePaymentIntentAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'amount', 'currency', 'status', 'created_at'
    ]
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['user__username', 'stripe_payment_intent_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(StripeWebhookEvent)
class StripeWebhookEventAdmin(admin.ModelAdmin):
    list_display = [
        'event_type', 'stripe_event_id', 'processed', 'created_at'
    ]
    list_filter = ['processed', 'event_type', 'created_at']
    search_fields = ['stripe_event_id', 'event_type']
    readonly_fields = ['created_at', 'processed_at']
    ordering = ['-created_at']
    
    def mark_as_processed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(processed=True, processed_at=timezone.now())
        self.message_user(request, f'{updated} eventos marcados como processados.')
    
    mark_as_processed.short_description = "Marcar como processado"
    
    actions = ['mark_as_processed'] 