from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.test import APIClient
from .models import (
    StripeCustomer,
    StripeProduct,
    StripePrice,
    StripeSubscription
)


class PaymentsModelsTest(TestCase):
    """Testes para os modelos do app payments"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.product = StripeProduct.objects.create(
            name='Premium',
            stripe_product_id='prod_test123',
            description='Plano Premium'
        )
        
        self.price = StripePrice.objects.create(
            product=self.product,
            stripe_price_id='price_test123',
            unit_amount=2990,  # R$ 29,90
            currency='brl',
            interval='month'
        )
    
    def test_stripe_customer_creation(self):
        """Testa criação de cliente Stripe"""
        customer = StripeCustomer.objects.create(
            user=self.user,
            stripe_customer_id='cus_test123'
        )
        
        self.assertEqual(customer.user, self.user)
        self.assertEqual(customer.stripe_customer_id, 'cus_test123')
        self.assertIsNotNone(customer.created_at)
    
    def test_stripe_product_creation(self):
        """Testa criação de produto Stripe"""
        self.assertEqual(self.product.name, 'Premium')
        self.assertEqual(self.product.stripe_product_id, 'prod_test123')
        self.assertTrue(self.product.is_active)
    
    def test_stripe_price_creation(self):
        """Testa criação de preço Stripe"""
        self.assertEqual(self.price.product, self.product)
        self.assertEqual(self.price.unit_amount, 2990)
        self.assertEqual(self.price.currency, 'brl')
        self.assertEqual(self.price.interval, 'month')
        self.assertEqual(self.price.amount_in_reais, 29.90)
    
    def test_stripe_subscription_creation(self):
        """Testa criação de assinatura Stripe"""
        from django.utils import timezone
        
        subscription = StripeSubscription.objects.create(
            user=self.user,
            stripe_subscription_id='sub_test123',
            price=self.price,
            status='active',
            current_period_start=timezone.now(),
            current_period_end=timezone.now() + timezone.timedelta(days=30)
        )
        
        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.price, self.price)
        self.assertEqual(subscription.status, 'active')
        self.assertTrue(subscription.is_active)


class PaymentsAPITest(APITestCase):
    """Testes para a API do app payments"""
    
    def setUp(self):
        """Configuração inicial para os testes da API"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.product = StripeProduct.objects.create(
            name='Premium',
            stripe_product_id='prod_test123',
            description='Plano Premium'
        )
        
        self.price = StripePrice.objects.create(
            product=self.product,
            stripe_price_id='price_test123',
            unit_amount=2990,
            currency='brl',
            interval='month'
        )
    
    def test_plans_view_unauthenticated(self):
        """Testa acesso à view de planos sem autenticação"""
        url = reverse('payments:plans')
        response = self.client.get(url)
        
        # Deve permitir acesso sem autenticação
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_plan_view_authenticated(self):
        """Testa acesso à view de plano do usuário com autenticação"""
        self.client.force_authenticate(user=self.user)
        url = reverse('payments:user-plan')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('plan_info', response.data)
    
    def test_user_plan_view_unauthenticated(self):
        """Testa acesso à view de plano do usuário sem autenticação"""
        url = reverse('payments:user-plan')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_subscription_view_authenticated(self):
        """Testa criação de assinatura com autenticação"""
        self.client.force_authenticate(user=self.user)
        url = reverse('payments:create-subscription')
        
        data = {
            'price_id': 'price_test123',
            'payment_method_id': 'pm_test123',
            'billing_cycle': 'month'
        }
        
        response = self.client.post(url, data)
        
        # Deve falhar porque não é um price_id real do Stripe
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_500_INTERNAL_SERVER_ERROR])
    
    def test_create_subscription_view_unauthenticated(self):
        """Testa criação de assinatura sem autenticação"""
        url = reverse('payments:create-subscription')
        data = {
            'price_id': 'price_test123',
            'payment_method_id': 'pm_test123',
            'billing_cycle': 'month'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_cancel_subscription_view_authenticated(self):
        """Testa cancelamento de assinatura com autenticação"""
        self.client.force_authenticate(user=self.user)
        url = reverse('payments:cancel-subscription')
        
        data = {
            'cancel_at_period_end': True
        }
        
        response = self.client.post(url, data)
        
        # Deve falhar porque não há assinatura ativa
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_subscription_status_view_authenticated(self):
        """Testa view de status da assinatura com autenticação"""
        self.client.force_authenticate(user=self.user)
        url = reverse('payments:subscription-status')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
    
    def test_user_subscriptions_view_authenticated(self):
        """Testa view de assinaturas do usuário com autenticação"""
        self.client.force_authenticate(user=self.user)
        url = reverse('payments:user-subscriptions')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('subscriptions', response.data)
    
    def test_payment_history_view_authenticated(self):
        """Testa view de histórico de pagamentos com autenticação"""
        self.client.force_authenticate(user=self.user)
        url = reverse('payments:payment-history')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('payments', response.data)


class PaymentsIntegrationTest(TestCase):
    """Testes de integração para o app payments"""
    
    def setUp(self):
        """Configuração inicial para os testes de integração"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_stripe_customer_integration(self):
        """Testa integração com cliente Stripe"""
        # Este teste seria executado apenas em ambiente de teste com Stripe
        # Por enquanto, apenas testamos a criação local
        customer = StripeCustomer.objects.create(
            user=self.user,
            stripe_customer_id='cus_test123'
        )
        
        self.assertIsNotNone(customer)
        self.assertEqual(customer.user, self.user)
    
    def test_product_price_relationship(self):
        """Testa relacionamento entre produto e preço"""
        product = StripeProduct.objects.create(
            name='Enterprise',
            stripe_product_id='prod_enterprise',
            description='Plano Enterprise'
        )
        
        price = StripePrice.objects.create(
            product=product,
            stripe_price_id='price_enterprise',
            unit_amount=9990,  # R$ 99,90
            currency='brl',
            interval='month'
        )
        
        self.assertEqual(price.product, product)
        self.assertEqual(product.prices.first(), price)
        self.assertEqual(price.amount_in_reais, 99.90) 