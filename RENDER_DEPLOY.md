# Deploy no Render.com - Versão Gratuita

Este guia mostra como fazer deploy da aplicação Symplifika Django no Render.com usando a versão gratuita.

## Pré-requisitos

1. Conta no [Render.com](https://render.com)
2. Repositório Git com o código (GitHub, GitLab, ou Bitbucket)
3. Chave API do OpenAI (se necessário)

## Passos para Deploy

### 1. Preparar o Repositório

Certifique-se de que todos os arquivos estão commitados no seu repositório:

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Criar o Web Service no Render

1. Acesse [render.com](https://render.com) e faça login
2. Clique em "New +" → "Web Service"
3. Conecte seu repositório Git
4. Configure as seguintes opções:

**Configurações Básicas:**
- **Name**: `symplifika-django`
- **Region**: `Oregon (US West)` (ou sua preferência)
- **Branch**: `main`
- **Runtime**: `Python 3`

**Build & Deploy:**
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn symplifika.wsgi:application`

### 3. Configurar Variáveis de Ambiente

No painel do Render, vá para "Environment" e adicione:

**Obrigatórias:**
```
DEBUG=False
SECRET_KEY=[gerar uma chave secreta nova]
PYTHON_VERSION=3.11.0
```

**Opcionais:**
```
OPENAI_API_KEY=sua-chave-openai
```

### 4. Criar o Banco de Dados PostgreSQL

1. No dashboard do Render, clique em "New +" → "PostgreSQL"
2. Configure:
   - **Name**: `symplifika-db`
   - **Database**: `symplifika`
   - **User**: `symplifika`
   - **Region**: Same as your web service
   - **PostgreSQL Version**: `15`

3. Após criar, copie a **Internal Database URL**

### 5. Conectar Banco ao Web Service

1. Volte ao seu Web Service
2. Em "Environment", adicione:
```
DATABASE_URL=[cole a Internal Database URL aqui]
```

### 6. Deploy Automático

O deploy será iniciado automaticamente. Aguarde alguns minutos.

## Configurações Adicionais

### Domínio Personalizado (Opcional)

Se quiser usar um domínio próprio:
1. Vá em "Settings" → "Custom Domains"
2. Adicione seu domínio
3. Configure os DNS conforme instruções

### Logs e Monitoramento

- **Logs**: Acesse pela aba "Logs" no dashboard
- **Métricas**: Disponível na aba "Metrics"

## Limitações da Versão Gratuita

- **Sleep Mode**: O serviço "dorme" após 15 minutos de inatividade
- **Build Minutes**: 500 minutos por mês
- **Bandwidth**: Unlimited
- **Database**: 1 GB de storage, conexões limitadas

## Troubleshooting

### Problema: Build falha
**Solução**: Verifique os logs na aba "Logs" e certifique-se de que:
- O arquivo `build.sh` tem permissões de execução
- Todas as dependências estão no `requirements.txt`

### Problema: Static files não carregam
**Solução**: Certifique-se de que:
- `whitenoise` está instalado
- `STATICFILES_STORAGE` está configurado corretamente

### Problema: Erro de database
**Solução**: Verifique se:
- A `DATABASE_URL` está configurada corretamente
- As migrações foram executadas no build

### Problema: CORS errors
**Solução**: 
- Certifique-se de que o domínio do Render está em `CORS_ALLOWED_ORIGINS`
- Verifique `CSRF_TRUSTED_ORIGINS`

## Comandos Úteis para Debug

Para executar comandos Django na produção, use o Render Console:

```bash
# Criar superuser
python manage.py createsuperuser

# Executar migrações manualmente
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Shell Django
python manage.py shell
```

## Monitoramento de Custos

A versão gratuita inclui:
- 750 horas de runtime por mês (suficiente para sempre ativo)
- 500 minutos de build por mês
- 1 GB PostgreSQL storage

## Próximos Passos

1. Configure monitoramento de erros (ex: Sentry)
2. Configure backups automáticos do banco
3. Implemente CI/CD com GitHub Actions
4. Configure domínio personalizado
5. Otimize performance (cache, CDN)

## Suporte

- Documentação oficial: [render.com/docs](https://render.com/docs)
- Community: [community.render.com](https://community.render.com)

---

**Nota**: Lembre-se de que na versão gratuita, o serviço pode ter latência inicial devido ao "cold start" após períodos de inatividade.