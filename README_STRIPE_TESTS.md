# 🧪 Testes do Stripe - Guia Rápido

## 🎯 Configuração em 5 Minutos

### 1️⃣ Obter Chaves de Teste
```bash
# Acesse: https://dashboard.stripe.com/test/apikeys
# Copie pk_test_... e sk_test_...
```

### 2️⃣ Configurar Ambiente
```bash
# Copiar arquivo de exemplo
cp .env.stripe.test .env

# Editar com suas chaves
nano .env
```

### 3️⃣ Setup Automático
```bash
# Executar script de configuração
./setup_stripe_test.sh
```

### 4️⃣ Verificar Sistema
```bash
# Testar se tudo está funcionando
python test_stripe_setup.py
```

### 5️⃣ Configurar Webhooks
```bash
# Método 1: Stripe CLI (Recomendado)
stripe listen --forward-to localhost:8000/payments/webhook/

# Método 2: Ngrok
ngrok http 8000
# Configure no Stripe Dashboard com URL HTTPS
```

## 🚀 Iniciar Testes

```bash
# Iniciar servidor
python manage.py runserver

# Acessar: http://localhost:8000
# Login → Clicar "Ver Planos" → Testar checkout
```

## 💳 Cartões de Teste

| Cartão | Resultado | Uso |
|--------|-----------|-----|
| `4242424242424242` | ✅ Sucesso | Testes gerais |
| `4000000000000002` | ❌ Falha | Testar erro |
| `4000002760003184` | 🔐 3D Secure | Testar autenticação |
| `4000000000000069` | ⏰ Expirado | Testar expiração |

**Dados complementares**: CVC: 123, Data: 12/30, Nome: Qualquer

## 🔍 Monitoramento

- **Stripe Dashboard**: https://dashboard.stripe.com/test/
- **Webhooks**: https://dashboard.stripe.com/test/webhooks  
- **Logs Django**: `tail -f logs/django.log`

## 🆘 Problemas Comuns

### "Preço não encontrado"
```bash
python manage.py setup_stripe_test --reset
```

### "Webhook não funciona"
```bash
# Verificar se está rodando
stripe listen --forward-to localhost:8000/payments/webhook/

# Ou configurar ngrok no Stripe Dashboard
```

### "Erro de autenticação"
```bash
# Verificar se chaves são de teste (sk_test_...)
echo $STRIPE_SECRET_KEY
```

## 📚 Arquivos Importantes

- `STRIPE_TEST_SETUP.md` - Guia completo detalhado
- `.env.stripe.test` - Exemplo de configuração
- `setup_stripe_test.sh` - Script de configuração
- `test_stripe_setup.py` - Verificação do sistema

## ✅ Checklist de Testes

- [ ] Chaves de teste configuradas
- [ ] Produtos criados no Stripe
- [ ] Webhooks funcionando
- [ ] Modal de upgrade abre
- [ ] Redirecionamento para Stripe funciona
- [ ] Pagamento com sucesso retorna corretamente
- [ ] Pagamento com falha mostra erro
- [ ] Plano é atualizado após pagamento

## 🔐 Segurança

⚠️ **IMPORTANTE**: Use apenas chaves de TESTE
- ✅ `pk_test_...` e `sk_test_...` 
- ❌ NUNCA use `pk_live_...` ou `sk_live_...`

## 📞 Suporte

1. Verificar logs: `python test_stripe_setup.py`
2. Consultar: `STRIPE_TEST_SETUP.md` (guia completo)
3. Documentação Stripe: https://stripe.com/docs/testing

---

🎉 **Sistema pronto para testes seguros sem dinheiro real!**