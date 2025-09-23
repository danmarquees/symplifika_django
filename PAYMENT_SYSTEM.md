# Sistema de Pagamentos Symplifika

Este documento descreve como usar o sistema de pagamentos integrado com Stripe implementado no Symplifika.

## Visão Geral

O sistema permite que usuários façam upgrade de seus planos diretamente através do dashboard, com redirecionamento seguro para o Stripe Checkout.

## Configuração Inicial

### 1. Variáveis de Ambiente

Adicione as seguintes variáveis ao seu arquivo `.env`:

```
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_RETURN_URL=http://localhost:8000/users/subscription-success/
```

### 2. Configuração dos Produtos no Stripe

Execute o comando para criar os produtos e preços padrão:

```bash
python manage.py setup_stripe_products
```

Este comando criará:
- **Premium**: R$ 29,90/mês ou R$ 299,00/ano
- **Enterprise**: R$ 99,90/mês ou R$ 999,00/ano

## Como Funciona

### 1. Interface do Usuário

No dashboard, usuários com plano gratuito verão um card "Upgrade to Pro" na sidebar. Ao clicar em "Ver Planos", um modal será aberto com as opções de upgrade.

### 2. Fluxo de Pagamento

1. **Seleção do Plano**: Usuário escolhe entre Premium ou Enterprise
2. **Tipo de Cobrança**: Pode alternar entre mensal e anual
3. **Checkout**: Redirecionamento para Stripe Checkout
4. **Confirmação**: Retorno para página de sucesso após pagamento

### 3. Endpoints Disponíveis

#### Listar Planos
```
GET /payments/plans/
```

#### Criar Sessão de Checkout
```
POST /payments/create-checkout-session/
{
  "plan": "premium",
  "billing_cycle": "month"
}
```

#### Portal do Cliente (para gerenciar assinatura)
```
POST /payments/customer-portal/
```

### 4. Webhooks

Configure o webhook no Stripe para o endpoint:
```
POST /payments/webhook/
```

Eventos processados:
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.payment_succeeded`
- `invoice.payment_failed`

## Estrutura dos Arquivos

### Templates
- `templates/dashboard.html` - Contém o modal de upgrade
- `templates/users/subscription_success.html` - Página de sucesso
- `templates/users/plan_upgrade.html` - Página de upgrade de planos

### JavaScript
- `static/js/app.js` - Contém as funções de checkout e modal

### Backend
- `payments/models.py` - Modelos do Stripe
- `payments/views.py` - Views das APIs de pagamento
- `payments/services.py` - Serviços para integração com Stripe
- `payments/urls.py` - URLs dos endpoints de pagamento

## Uso no Frontend

### Abrir Modal de Upgrade
```javascript
window.app.showUpgradeModal()
```

### Iniciar Checkout
```javascript
window.app.startCheckout('premium', 'monthly')
```

### Alternar Tipo de Cobrança
```javascript
window.app.setBilling('yearly')
```

## Modelos de Dados

### StripeCustomer
- `user` - Usuário associado
- `stripe_customer_id` - ID do cliente no Stripe

### StripeProduct
- `name` - Nome do produto
- `stripe_product_id` - ID do produto no Stripe
- `description` - Descrição do produto

### StripePrice
- `product` - Produto associado
- `stripe_price_id` - ID do preço no Stripe
- `unit_amount` - Valor em centavos
- `currency` - Moeda (BRL)
- `interval` - Intervalo de cobrança (month/year)

### StripeSubscription
- `user` - Usuário associado
- `stripe_subscription_id` - ID da assinatura no Stripe
- `price` - Preço associado
- `status` - Status da assinatura
- `current_period_start` - Início do período atual
- `current_period_end` - Fim do período atual

## Funcionalidades dos Planos

### Gratuito
- 50 atalhos
- 100 expansões IA/mês
- Funcionalidades básicas

### Premium (R$ 29,90/mês)
- 500 atalhos
- 1.000 expansões IA/mês
- Estatísticas avançadas
- Suporte prioritário

### Enterprise (R$ 99,90/mês)
- Atalhos ilimitados
- 10.000 expansões IA/mês
- API personalizada
- Suporte dedicado

## Segurança

- Todas as transações são processadas pelo Stripe
- Webhooks são verificados com assinatura
- Tokens CSRF são validados em todas as requisições
- Dados sensíveis não são armazenados localmente

## Testes

Para testar o sistema:

1. Use as chaves de teste do Stripe
2. Use cartões de teste do Stripe (ex: 4242424242424242)
3. Verifique os webhooks no painel do Stripe
4. Monitore os logs para debug

## Monitoramento

- Logs são salvos para todas as operações
- Eventos de webhook são armazenados para auditoria
- Status das assinaturas são sincronizados automaticamente

## Troubleshooting

### Erro "Preço não encontrado"
Verifique se os produtos foram criados com o comando `setup_stripe_products`

### Webhook não funciona
1. Verifique se o endpoint está acessível publicamente
2. Confirme se o webhook secret está correto
3. Verifique os logs do Stripe

### Redirecionamento não funciona
Verifique se `STRIPE_RETURN_URL` está configurado corretamente

## Próximos Passos

1. Implementar cupons de desconto
2. Adicionar métricas de conversão
3. Implementar testes de integração
4. Adicionar notificações por email para mudanças de plano