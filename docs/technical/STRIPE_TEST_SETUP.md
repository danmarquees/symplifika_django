# Guia de Configuração de Testes do Stripe

Este guia irá te ajudar a configurar o ambiente de testes do Stripe para o Symplifika de forma segura e eficiente.

## 🎯 Objetivo

Configurar um ambiente sandbox completo para testar pagamentos sem usar dinheiro real, incluindo:
- Produtos de teste no Stripe
- Webhooks funcionais
- Fluxo completo de pagamento
- Monitoramento e debug

## 📋 Pré-requisitos

1. **Conta Stripe (gratuita)**
   - Crie em: https://dashboard.stripe.com/register
   - Acesse o dashboard: https://dashboard.stripe.com/

2. **Ferramentas necessárias**
   - Python 3.8+ com Django
   - Stripe CLI ou Ngrok (para webhooks)
   - Git (opcional, para backup)

## 🔧 Passo 1: Configuração das Chaves do Stripe

### 1.1 Obter Chaves de Teste

1. Acesse o **Dashboard do Stripe**: https://dashboard.stripe.com/test/
2. Vá em **Developers** > **API keys**
3. Copie as seguintes chaves:
   - **Publishable key** (começa com `pk_test_`)
   - **Secret key** (começa com `sk_test_`)

⚠️ **IMPORTANTE**: Use apenas chaves de TESTE!

### 1.2 Configurar Arquivo .env

Copie o arquivo de exemplo:
```bash
cp .env.stripe.test .env
```

Edite o arquivo `.env` e substitua as chaves:
```env
STRIPE_PUBLISHABLE_KEY=pk_test_51ABC123...sua_chave_aqui
STRIPE_SECRET_KEY=sk_test_51ABC123...sua_chave_aqui
STRIPE_WEBHOOK_SECRET=whsec_ABC123...será_preenchido_depois
```

## 🛠️ Passo 2: Configuração Automática (Recomendado)

Execute o script de setup automático:

```bash
chmod +x setup_stripe_test.sh
./setup_stripe_test.sh
```

Este script irá:
- ✅ Verificar se as chaves são de teste
- ✅ Criar produtos Premium e Enterprise no Stripe
- ✅ Configurar preços mensais e anuais
- ✅ Executar migrações necessárias
- ✅ Exibir cartões de teste disponíveis

## 🔧 Passo 3: Configuração Manual (Alternativa)

Se preferir configurar manualmente:

### 3.1 Executar Migrações
```bash
python manage.py migrate
```

### 3.2 Criar Produtos de Teste
```bash
python manage.py setup_stripe_test
```

### 3.3 Ver Informações de Webhooks
```bash
python manage.py setup_stripe_test --webhook-info
```

## 🌐 Passo 4: Configurar Webhooks

Os webhooks são essenciais para sincronizar pagamentos. Escolha um método:

### Método 1: Stripe CLI (Recomendado)

1. **Instalar Stripe CLI**: https://stripe.com/docs/stripe-cli
2. **Fazer login**:
   ```bash
   stripe login
   ```
3. **Escutar webhooks**:
   ```bash
   stripe listen --forward-to localhost:8000/payments/webhook/
   ```
4. **Copiar o webhook secret** exibido no terminal
5. **Adicionar ao .env**:
   ```env
   STRIPE_WEBHOOK_SECRET=whsec_ABC123...
   ```

### Método 2: Ngrok

1. **Instalar ngrok**: https://ngrok.com/
2. **Executar**:
   ```bash
   ngrok http 8000
   ```
3. **Copiar URL HTTPS** (ex: https://abc123.ngrok.io)
4. **No Stripe Dashboard**:
   - Vá em **Developers** > **Webhooks**
   - Clique em **Add endpoint**
   - URL: `https://sua-url.ngrok.io/payments/webhook/`
   - Eventos: selecione todos os `customer.subscription.*` e `invoice.*`
5. **Copiar signing secret** para o `.env`

### Eventos Necessários
Configure estes eventos no webhook:
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.payment_succeeded`
- `invoice.payment_failed`
- `checkout.session.completed`

## 🚀 Passo 5: Iniciar Testes

### 5.1 Iniciar Servidor
```bash
python manage.py runserver
```

### 5.2 Acessar Dashboard
1. Vá para: http://localhost:8000
2. Faça login (ou crie uma conta)
3. Na sidebar, clique em **"Ver Planos"** no card de upgrade

### 5.3 Testar Modal de Pagamento
1. Escolha um plano (Premium ou Enterprise)
2. Selecione cobrança mensal ou anual
3. Clique em **"Escolher [Plano]"**
4. Será redirecionado para o Stripe Checkout

## 💳 Cartões de Teste

Use estes cartões para simular diferentes cenários:

### Sucesso
- **Visa**: `4242424242424242`
- **Mastercard**: `5555555555554444`
- **American Express**: `378282246310005`

### Falhas
- **Genérica**: `4000000000000002`
- **Saldo insuficiente**: `4000000000009995`
- **Cartão expirado**: `4000000000000069`
- **CVC incorreto**: `4000000000000127`

### Autenticação 3D Secure
- **Requer autenticação**: `4000002760003184`
- **Autenticação falha**: `4000008400001629`

### Dados Complementares
Para qualquer cartão:
- **CVC**: Qualquer 3 dígitos (ex: 123)
- **Data de expiração**: Qualquer data futura (ex: 12/30)
- **Nome**: Qualquer nome
- **CEP**: Qualquer CEP válido

## 📊 Monitoramento

### Dashboard do Stripe
- **Pagamentos**: https://dashboard.stripe.com/test/payments
- **Assinaturas**: https://dashboard.stripe.com/test/subscriptions
- **Webhooks**: https://dashboard.stripe.com/test/webhooks
- **Logs**: https://dashboard.stripe.com/test/logs

### Logs do Django
```bash
# Em um terminal separado
tail -f logs/django.log

# Ou verificar no console se não tiver arquivo de log
```

### Comandos de Debug
```bash
# Verificar produtos criados
python manage.py shell
>>> from payments.models import StripeProduct, StripePrice
>>> StripeProduct.objects.all()
>>> StripePrice.objects.all()

# Testar conexão com Stripe
>>> import stripe
>>> from django.conf import settings
>>> stripe.api_key = settings.STRIPE_SECRET_KEY
>>> stripe.Product.list(limit=5)
```

## 🧪 Cenários de Teste

### Teste 1: Pagamento com Sucesso
1. Use cartão `4242424242424242`
2. Complete o checkout
3. Verifique se volta para página de sucesso
4. Confirme no Stripe Dashboard que o pagamento foi processado

### Teste 2: Pagamento com Falha
1. Use cartão `4000000000000002`
2. Tente completar checkout
3. Verifique se mostra erro apropriado
4. Confirme que não foi criada assinatura

### Teste 3: Webhook
1. Complete um pagamento com sucesso
2. Verifique logs do webhook (Stripe CLI ou ngrok)
3. Confirme que o plano do usuário foi atualizado no Django

### Teste 4: 3D Secure
1. Use cartão `4000002760003184`
2. Siga fluxo de autenticação
3. Verifique se completa corretamente

## ⚠️ Troubleshooting

### Problema: "Preço não encontrado"
**Solução**:
```bash
python manage.py setup_stripe_test --reset
```

### Problema: Webhook não funciona
**Verificar**:
1. URL está acessível (teste com curl)
2. STRIPE_WEBHOOK_SECRET está correto
3. Eventos estão configurados no Stripe Dashboard

### Problema: Erro de autenticação
**Verificar**:
1. Chaves estão corretas no .env
2. Chaves são de TESTE (começam com sk_test_)
3. Não há espaços extras nas chaves

### Problema: Redirecionamento não funciona
**Verificar**:
1. URLs de sucesso/cancelamento estão corretas
2. Servidor está rodando na porta correta
3. CORS está configurado (se necessário)

## 📈 Próximos Passos

Após confirmar que os testes funcionam:

1. **Documentar cenários específicos** do seu negócio
2. **Configurar ambiente de staging** (opcional)
3. **Preparar migração para produção**
4. **Configurar monitoramento** (logs, alertas)
5. **Treinar equipe** nos fluxos de teste

## 🔐 Segurança

### ✅ Boas Práticas
- Sempre use chaves de teste (`sk_test_`, `pk_test_`)
- Nunca commite chaves no Git
- Use webhooks com verificação de assinatura
- Monitore logs por atividades suspeitas

### ❌ Nunca Fazer
- Usar chaves de produção em testes
- Expor chaves em código fonte
- Desabilitar verificação de webhook
- Testar com dados reais de clientes

## 📚 Recursos Adicionais

- **Documentação do Stripe**: https://stripe.com/docs
- **Cartões de teste**: https://stripe.com/docs/testing#cards
- **Webhooks**: https://stripe.com/docs/webhooks
- **Stripe CLI**: https://stripe.com/docs/stripe-cli
- **Dashboard de teste**: https://dashboard.stripe.com/test/

## 🆘 Suporte

Se tiver problemas:

1. **Verifique logs** do Django e do Stripe
2. **Consulte documentação** do Stripe
3. **Use comandos de debug** fornecidos neste guia
4. **Teste com curl** para verificar endpoints

---

✅ **Ambiente de testes configurado com sucesso!**

Agora você pode testar pagamentos com segurança, sem usar dinheiro real, e ter confiança de que o sistema funcionará corretamente em produção.