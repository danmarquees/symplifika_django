# App Payments - Sistema de Pagamentos via Stripe

Este app implementa a integração completa com o Stripe para gerenciar assinaturas e pagamentos no projeto Symplifika.

## Funcionalidades

- ✅ Integração completa com Stripe
- ✅ Gerenciamento de assinaturas
- ✅ Processamento de webhooks
- ✅ Portal do cliente Stripe
- ✅ Histórico de pagamentos
- ✅ Sistema de planos (Free, Premium, Enterprise)
- ✅ Suporte a pagamentos recorrentes (mensal/anual)
- ✅ Métodos de pagamento: Cartão, PIX

## Estrutura do App

```
payments/
├── models.py              # Modelos do Stripe
├── views.py               # Views da API
├── serializers.py         # Serializers para DRF
├── services.py            # Serviços de integração
├── admin.py               # Interface administrativa
├── urls.py                # URLs do app
├── tests.py               # Testes automatizados
├── migrations/            # Migrações do banco
└── management/            # Comandos de gerenciamento
    └── commands/
        └── setup_stripe_products.py
```

## Modelos Principais

### StripeCustomer
Gerencia clientes no Stripe, vinculando usuários locais com contas Stripe.

### StripeProduct
Representa produtos/planos disponíveis para assinatura.

### StripePrice
Define preços para cada produto, com suporte a diferentes intervalos de cobrança.

### StripeSubscription
Controla assinaturas ativas dos usuários.

### StripePaymentIntent
Gerencia intenções de pagamento para transações únicas.

### StripeWebhookEvent
Registra e processa eventos recebidos do Stripe via webhooks.

## API Endpoints

### Autenticados
- `POST /payments/create-subscription/` - Criar assinatura
- `POST /payments/cancel-subscription/` - Cancelar assinatura
- `POST /payments/plan-upgrade/` - Fazer upgrade de plano
- `POST /payments/create-payment-intent/` - Criar intenção de pagamento
- `POST /payments/customer-portal/` - Acessar portal do cliente

### Públicos
- `GET /payments/plans/` - Listar planos disponíveis
- `POST /payments/webhook/` - Endpoint para webhooks do Stripe

### Auxiliares
- `GET /payments/user-plan/` - Informações do plano do usuário
- `GET /payments/subscription-status/` - Status da assinatura
- `GET /payments/user-subscriptions/` - Histórico de assinaturas
- `GET /payments/payment-history/` - Histórico de pagamentos

## Configuração

### 1. Variáveis de Ambiente

```bash
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_RETURN_URL=http://localhost:3000/account
```

### 2. Instalação de Dependências

```bash
pip install stripe==8.10.0
```

### 3. Configuração do Stripe

Execute o comando para criar produtos e preços padrão:

```bash
python manage.py setup_stripe_products
```

## Uso

### Criação de Assinatura

```python
from payments.services import StripeService

# Criar assinatura
subscription = StripeService.create_subscription(
    user=request.user,
    price_id='price_123',
    payment_method_id='pm_123',
    billing_cycle='month'
)
```

### Verificação de Status

```python
# Verificar status da assinatura
status = StripeService.get_subscription_status(user)
if status['has_active_subscription']:
    print(f"Plano: {status['plan']}")
```

### Gerenciamento de Planos

```python
from payments.services import PlanService

# Obter planos disponíveis
plans = PlanService.get_available_plans()

# Obter informações do plano do usuário
plan_info = PlanService.get_user_plan_info(user)
```

## Webhooks

O sistema processa automaticamente os seguintes eventos:

- `customer.subscription.created` - Nova assinatura criada
- `customer.subscription.updated` - Assinatura atualizada
- `customer.subscription.deleted` - Assinatura cancelada
- `invoice.payment_succeeded` - Pagamento realizado com sucesso
- `invoice.payment_failed` - Falha no pagamento

## Segurança

- ✅ Verificação de assinatura de webhooks
- ✅ Autenticação obrigatória para endpoints sensíveis
- ✅ Validação de dados em todas as operações
- ✅ Logs detalhados para auditoria
- ✅ Tratamento seguro de erros

## Testes

Execute os testes do app:

```bash
python manage.py test payments
```

## Monitoramento

### Logs
O sistema registra logs para todas as operações importantes:
- Criação/cancelamento de assinaturas
- Processamento de webhooks
- Erros de pagamento
- Atualizações de status

### Dashboard Stripe
Use o dashboard do Stripe para monitorar:
- Transações em tempo real
- Assinaturas ativas
- Métricas de receita
- Falhas de pagamento

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

### Debug

Ative logs detalhados:

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

- [ ] Implementar sistema de cupons/descontos
- [ ] Adicionar suporte a pagamentos em grupo
- [ ] Implementar sistema de notificações por email
- [ ] Criar relatórios de faturamento
- [ ] Adicionar suporte a múltiplas moedas
- [ ] Implementar sistema de reembolsos

## Suporte

Para dúvidas sobre a integração:
- Consulte a [documentação do Stripe](https://stripe.com/docs)
- Verifique os logs do sistema
- Teste em ambiente de desenvolvimento primeiro
- Consulte o arquivo `STRIPE_INTEGRATION.md` na raiz do projeto 