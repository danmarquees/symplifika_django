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
- **Start Command**: `gunicorn symplifika.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120`

### 3. Configurar Variáveis de Ambiente

No painel do Render, vá para "Environment" e adicione:

**Obrigatórias:**
```
DEBUG=False
SECRET_KEY=[gerar uma chave secreta nova]
PYTHON_VERSION=3.13.4
DJANGO_SETTINGS_MODULE=symplifika.production_settings
```

**Opcionais:**
```
OPENAI_API_KEY=sua-chave-openai
```

### 4. Deploy Automático

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

## Arquivos de Diagnóstico

Para ajudar com problemas, o projeto inclui:

### Script de Verificação
Execute para diagnosticar problemas:
```bash
python check_environment.py
```

### Logs Detalhados
O script de build (`build.sh`) agora inclui logs detalhados para facilitar o troubleshooting.

## Limitações da Versão Gratuita

- **Sleep Mode**: O serviço "dorme" após 15 minutos de inatividade
- **Build Minutes**: 500 minutos por mês
- **Bandwidth**: Unlimited
- **Storage**: Files são temporários (reset a cada deploy)

## Troubleshooting

### Problema: Build falha com erro de PostgreSQL
**Solução**: A configuração foi simplificada para usar SQLite por padrão, evitando problemas de compatibilidade:
1. Certifique-se de que está usando `DJANGO_SETTINGS_MODULE=symplifika.production_settings`
2. Verifique se o arquivo `build.sh` tem permissões de execução

### Problema: Build falha na instalação de dependências
**Solução**: 
- Verifique se o `runtime.txt` especifica Python 3.13.4
- Certifique-se de que todas as dependências estão no `requirements.txt`
- Verifique os logs de build para erros específicos

### Problema: Static files não carregam
**Solução**: 
- Certifique-se de que `whitenoise` está instalado
- Verifique se `STATICFILES_STORAGE` está configurado nas configurações de produção
- Execute `python manage.py collectstatic` localmente para testar

### Problema: Erro de database
**Solução**: 
- O projeto usa SQLite por padrão para máxima compatibilidade
- Dados são temporários e resetados a cada deploy (adequado para demos/testes)
- Para dados persistentes, considere usar um banco externo

### Problema: Erro "Unable to configure handler 'file'"
**Solução**: Use as configurações de produção que têm logging simplificado:
```bash
DJANGO_SETTINGS_MODULE=symplifika.production_settings
```

### Problema: CORS errors
**Solução**: 
- As configurações de produção configuram CORS automaticamente baseado em `RENDER_EXTERNAL_HOSTNAME`
- Certifique-se de que está usando `symplifika.production_settings`

### Problema: Timeout no build
**Solução**: 
- O script de build foi otimizado com timeouts apropriados
- Se ainda falhar, verifique se há dependências que demoram muito para instalar

## Comandos Úteis para Debug

### No Render Console (produção):
```bash
# Verificar ambiente
python check_environment.py

# Criar superuser
python manage.py createsuperuser

# Executar migrações manualmente
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Verificar configuração de deploy
python manage.py check --deploy

# Shell Django
python manage.py shell
```

### Para desenvolvimento local:
```bash
# Setup completo do ambiente local
./local_setup.sh

# Verificar ambiente local
python check_environment.py
```

## Monitoramento de Custos

A versão gratuita inclui:
- 750 horas de runtime por mês (suficiente para sempre ativo)
- 500 minutos de build por mês
- Storage temporário (dados resetados a cada deploy)

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

## Mudanças Importantes na Configuração

### Configurações de Produção Separadas
- Criado `symplifika/production_settings.py` específico para produção
- Usa SQLite por padrão para máxima compatibilidade
- Configurações de logging simplificadas para evitar erros
- Configurações de segurança otimizadas para Render

### Script de Build Melhorado
- Verificações de ambiente detalhadas
- Criação automática de diretórios necessários
- Logs detalhados para facilitar troubleshooting

### Versão do Python
- Atualizado para Python 3.13.4 (compatível com Render)
- Runtime especificado em `runtime.txt`

**Notas Importantes**: 
- Na versão gratuita, o serviço pode ter latência inicial devido ao "cold start" após períodos de inatividade
- **Dados SQLite são temporários**: Todos os dados (usuários, posts, etc.) são perdidos a cada deploy
- Para aplicações com dados persistentes, considere usar um banco de dados externo ou upgrade para plano pago