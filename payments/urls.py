from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Planos e assinaturas
    path('plans/', views.PlansView.as_view(), name='plans'),
    path('user-plan/', views.UserPlanView.as_view(), name='user-plan'),
    path('create-subscription/', views.CreateSubscriptionView.as_view(), name='create-subscription'),
    path('cancel-subscription/', views.CancelSubscriptionView.as_view(), name='cancel-subscription'),
    path('plan-upgrade/', views.PlanUpgradeView.as_view(), name='plan-upgrade'),
    
    # Pagamentos
    path('create-payment-intent/', views.CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path('create-checkout-session/', views.CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    
    # Portal do cliente
    path('customer-portal/', views.CustomerPortalView.as_view(), name='customer-portal'),
    
    # Webhooks
    path('webhook/', views.WebhookView.as_view(), name='webhook'),
    
    # Views auxiliares
    path('subscription-status/', views.subscription_status, name='subscription-status'),
    path('user-subscriptions/', views.user_subscriptions, name='user-subscriptions'),
    path('payment-history/', views.payment_history, name='payment-history'),
] 