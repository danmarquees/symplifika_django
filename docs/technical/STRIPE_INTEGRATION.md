# Integração com Stripe - Sistema de Pagamentos

Este documento explica como configurar e usar o sistema de pagamentos integrado com Stripe no projeto Symplifika.

## Configuração Inicial

### 1. Configuração das Variáveis de Ambiente

Adicione as seguintes variáveis ao seu arquivo `.env`:

```bash
# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
STRIPE_RETURN_URL=http://localhost:3000/account
```

### 2. Obtenção das Chaves do Stripe

1. Acesse o [Dashboard do Stripe](https://dashboard.stripe.com/)
2. Vá para **Developers > API keys**
3. Copie as chaves de teste (test keys) para desenvolvimento
4. Para produção, use as chaves live

### 3. Configuração do Webhook

1. No Dashboard do Stripe, vá para **Developers > Webhooks**
2. Clique em **Add endpoint**
3. Configure a URL: `https://seu-dominio.com/payments/webhook/`
4. Selecione os eventos:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Copie o **Signing secret** para `STRIPE_WEBHOOK_SECRET`

## Estrutura do Sistema

### Modelos Criados

- **StripeCustomer**: Cliente no Stripe
- **StripeProduct**: Produtos/planos disponíveis
- **StripePrice**: Preços dos produtos
- **StripeSubscription**: Assinaturas ativas
- **StripePaymentIntent**: Intenções de pagamento
- **StripeWebhookEvent**: Eventos de webhook processados

### Serviços Principais

- **StripeService**: Integração direta com a API do Stripe
- **PlanService**: Gerenciamento de planos e funcionalidades

## Endpoints da API

### Planos e Assinaturas

- `GET /payments/plans/` - Lista planos disponíveis
- `GET /payments/user-plan/` - Informações do plano do usuário
- `POST /payments/create-subscription/` - Criar assinatura
- `POST /payments/cancel-subscription/` - Cancelar assinatura
- `POST /payments/plan-upgrade/` - Fazer upgrade de plano

### Pagamentos

- `POST /payments/create-payment-intent/` - Criar intenção de pagamento

### Portal do Cliente

- `POST /payments/customer-portal/` - Acessar portal do cliente Stripe

### Webhooks

- `POST /payments/webhook/` - Endpoint para webhooks do Stripe

### Views Auxiliares

- `GET /payments/subscription-status/` - Status da assinatura
- `GET /payments/user-subscriptions/` - Histórico de assinaturas
- `GET /payments/payment-history/` - Histórico de pagamentos

## Uso no Frontend

### 1. Configuração do Stripe.js

```javascript
import { loadStripe } from '@stripe/stripe-js';

const stripePromise = loadStripe('sua_chave_publica_aqui');
```

### 2. Criação de Assinatura

```javascript
const createSubscription = async (priceId, paymentMethodId) => {
  const response = await fetch('/payments/create-subscription/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),
    },
    body: JSON.stringify({
      price_id: priceId,
      payment_method_id: paymentMethodId,
      billing_cycle: 'month'
    })
  });
  
  return response.json();
};
```

### 3. Verificação de Status

```javascript
const checkSubscriptionStatus = async () => {
  const response = await fetch('/payments/subscription-status/');
  const data = await response.json();
  
  if (data.success) {
    console.log('Status da assinatura:', data.status);
  }
};
```

## Fluxo de Pagamento

### 1. Criação de Assinatura

1. Usuário seleciona um plano
2. Frontend cria PaymentMethod no Stripe
3. Frontend envia `price_id` e `payment_method_id` para `/payments/create-subscription/`
4. Backend cria assinatura no Stripe
5. Usuário é redirecionado para confirmação de pagamento se necessário

### 2. Processamento de Webhooks

1. Stripe envia eventos para `/payments/webhook/`
2. Sistema processa eventos e atualiza status local
3. Perfil do usuário é atualizado automaticamente
4. Limites de funcionalidades são ajustados conforme o plano

### 3. Cancelamento

1. Usuário solicita cancelamento
2. Sistema cancela assinatura no Stripe
3. Perfil é revertido para plano gratuito
4. Limites são ajustados automaticamente

## Configuração de Planos

### Estrutura de Preços

```python
# Exemplo de configuração de preços
premium_monthly = StripePrice.objects.create(
    product=premium_product,
    stripe_price_id='price_premium_monthly',
    unit_amount=2990,  # R$ 29,90
    currency='brl',
    interval='month'
)

premium_yearly = StripePrice.objects.create(
    product=premium_product,
    stripe_price_id='price_premium_yearly',
    unit_amount=29900,  # R$ 299,00
    currency='brl',
    interval='year'
)
```

### Limites por Plano

- **Free**: 50 atalhos, 100 requisições IA/mês
- **Premium**: 500 atalhos, 1000 requisições IA/mês
- **Enterprise**: Ilimitado

## Segurança

### 1. Verificação de Webhooks

Todos os webhooks são verificados usando `STRIPE_WEBHOOK_SECRET`

### 2. Autenticação

Endpoints sensíveis requerem autenticação (`IsAuthenticated`)

### 3. Validação de Dados

Todos os dados são validados antes de serem processados

## Testes

### Executar Testes

```bash
python manage.py test payments
```

### Testes Disponíveis

- Testes de modelos
- Testes de API
- Testes de integração

## Monitoramento

### Logs

O sistema registra logs para:
- Criação de assinaturas
- Processamento de webhooks
- Erros de pagamento
- Atualizações de status

### Dashboard do Stripe

Use o dashboard do Stripe para monitorar:
- Transações
- Assinaturas ativas
- Falhas de pagamento
- Métricas de receita

## Troubleshooting

### Problemas Comuns

1. **Webhook não processado**
   - Verifique `STRIPE_WEBHOOK_SECRET`
   - Confirme URL do webhook no Stripe

2. **Assinatura não criada**
   - Verifique `STRIPE_SECRET_KEY`
   - Confirme `price_id` válido

3. **Erro de autenticação**
   - Verifique se o usuário está logado
   - Confirme permissões da API

### Logs de Debug

Ative logs detalhados em desenvolvimento:

```python
LOGGING = {
    'loggers': {
        'payments': {
            'level': 'DEBUG',
        },
    },
}
```

## Próximos Passos

1. Configurar planos e preços no Stripe
2. Implementar interface de pagamento no frontend
3. Configurar webhooks para produção
4. Implementar sistema de notificações
5. Adicionar relatórios de faturamento

## Suporte

Para dúvidas sobre a integração:
- Consulte a [documentação do Stripe](https://stripe.com/docs)
- Verifique os logs do sistema
- Teste em ambiente de desenvolvimento primeiro 