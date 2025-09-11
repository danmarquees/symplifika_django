# Configuração do PostgreSQL no Render.com

Este guia explica como configurar o projeto Symplifika Django para usar PostgreSQL no Render.com para maior persistência de dados.

## 🎯 Visão Geral

O projeto foi configurado para usar:
- **PostgreSQL** em produção (Render.com) 
- **SQLite** em desenvolvimento local (como fallback)

## 🚀 Configuração no Render.com

### 1. Criar Database PostgreSQL

1. Acesse seu dashboard do Render.com
2. Clique em "New +" → "PostgreSQL"
3. Configure os seguintes parâmetros:
   - **Name**: `symplifika-postgres-db`
   - **Database**: `symplifika_db`
   - **User**: `symplifika_user`
   - **Region**: Escolha a mesma região do seu web service
   - **PostgreSQL Version**: 15 (recomendado)
   - **Plan**: Free ou pago conforme necessário

4. Clique em "Create Database"
5. **Importante**: Anote a `Internal Database URL` que será gerada

### 2. Configurar Web Service

1. Acesse seu web service no Render
2. Vá em "Environment" → "Environment Variables"
3. Adicione as seguintes variáveis:

```bash
DATABASE_URL=postgresql://symplifika_user:password@hostname:5432/symplifika_db
DJANGO_SETTINGS_MODULE=symplifika.production_settings
DEBUG=False
```

**Importante**: Substitua a `DATABASE_URL` pela URL interna do seu database PostgreSQL criado no passo anterior.

### 3. Configurar Build Command

Certifique-se que seu `render.yaml` está configurado corretamente:

```yaml
services:
  - type: web
    name: symplifika-django
    env: python
    buildCommand: "./build.sh"
    startCommand: "gunicorn symplifika.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120"
    envVars:
      - key: PYTHON_VERSION
        value: 3.13.4
      - key: DJANGO_SETTINGS_MODULE
        value: symplifika.production_settings
      - key: DEBUG
        value: False
      - key: SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: symplifika-postgres-db
          property: connectionString
```

### 4. Deploy

1. Faça commit das mudanças no seu repositório
2. O Render detectará automaticamente as mudanças
3. O deploy será executado com as novas configurações PostgreSQL

## 🖥️ Desenvolvimento Local com PostgreSQL

### Opção 1: Script Automático

Execute o script de configuração automática:

```bash
python setup_postgresql.py
```

Este script irá:
- Instalar PostgreSQL (se necessário)
- Criar database e usuário
- Gerar arquivo `.env` com configurações
- Executar migrações Django
- Criar superusuário

### Opção 2: Configuração Manual

1. **Instalar PostgreSQL**:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib python3-dev libpq-dev

# macOS com Homebrew
brew install postgresql

# Instalar driver Python
pip install psycopg2-binary
```

2. **Criar Database e Usuário**:

```sql
-- Conectar como postgres
sudo -u postgres psql

-- Criar usuário
CREATE USER symplifika_user WITH PASSWORD 'symplifika_pass123';

-- Criar database
CREATE DATABASE symplifika_db OWNER symplifika_user;

-- Dar privilégios
GRANT ALL PRIVILEGES ON DATABASE symplifika_db TO symplifika_user;

-- Sair
\q
```

3. **Criar arquivo `.env`**:

```bash
# Configurações do Django
DEBUG=True
SECRET_KEY=your_secret_key_here

# PostgreSQL local
DATABASE_URL=postgresql://symplifika_user:symplifika_pass123@localhost:5432/symplifika_db

# CORS para desenvolvimento
CORS_ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
```

4. **Executar Migrações**:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## 📊 Verificação da Configuração

### Verificar Conexão com Database

Execute este comando para verificar se o Django está conectando corretamente:

```bash
python manage.py dbshell
```

### Verificar Configurações

```bash
python check_environment.py
```

### Logs do Render

No dashboard do Render, você pode verificar os logs para confirmar:
- Database conectado com sucesso
- Migrações executadas
- Configurações carregadas corretamente

## 🔧 Troubleshooting

### Erro: "could not connect to server"

1. Verifique se a `DATABASE_URL` está correta
2. Confirme que o database PostgreSQL está rodando
3. Verifique se o web service e database estão na mesma região

### Erro: "relation does not exist"

Execute as migrações manualmente:

```bash
# No Render Console ou localmente
python manage.py migrate --run-syncdb
```

### Performance Issues

Para melhorar a performance do PostgreSQL:

1. **Configurar Connection Pooling** (arquivo `settings.py`):

```python
DATABASES = {
    'default': dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,  # 10 minutos
        conn_health_checks=True,
    )
}
```

2. **Otimizar Queries**:
   - Use `select_related()` e `prefetch_related()`
   - Implemente cache para queries frequentes
   - Monitore queries lentas

### Backup do Database

Para fazer backup do database PostgreSQL no Render:

1. Acesse o dashboard do database
2. Vá em "Info" tab
3. Use as informações de conexão para fazer dump:

```bash
pg_dump postgresql://username:password@hostname:port/database > backup.sql
```

## 📈 Benefícios do PostgreSQL

Ao migrar do SQLite para PostgreSQL, você obtém:

- **Persistência**: Dados não são perdidos entre deploys
- **Performance**: Melhor performance para queries complexas
- **Concorrência**: Suporte a múltiplas conexões simultâneas
- **Funcionalidades**: Recursos avançados como índices, triggers, etc.
- **Escalabilidade**: Adequado para crescimento do projeto
- **Backup**: Ferramentas robustas de backup e recovery

## 🔒 Segurança

- Nunca exponha credenciais do database no código
- Use variáveis de ambiente para configurações sensíveis
- Configure SSL/TLS para conexões em produção
- Mantenha o PostgreSQL atualizado
- Monitore acessos e atividades suspeitas

## 📚 Recursos Adicionais

- [Documentação PostgreSQL](https://www.postgresql.org/docs/)
- [Django Database Documentation](https://docs.djangoproject.com/en/5.2/ref/databases/)
- [Render PostgreSQL Guide](https://render.com/docs/databases)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)

## 🆘 Suporte

Se encontrar problemas:

1. Verifique os logs do Render
2. Teste a conexão localmente
3. Consulte a documentação do Django e PostgreSQL
4. Verifique os fóruns da comunidade Render

---

**Nota**: Este guia assume que você já tem um projeto Django funcionando no Render. Se precisar de ajuda com o deploy inicial, consulte o arquivo `RENDER_DEPLOY.md`.