#!/usr/bin/env python3
"""
Script para configuração local do PostgreSQL para o projeto Symplifika
Este script ajuda a configurar um ambiente de desenvolvimento local com PostgreSQL
"""

import os
import sys
import subprocess
import psycopg2
from psycopg2 import sql
from django.core.management.utils import get_random_secret_key

def run_command(command, check=True):
    """Execute um comando no shell"""
    print(f"Executando: {command}")
    try:
        result = subprocess.run(command, shell=True, check=check,
                              capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar comando: {e}")
        if e.stderr:
            print(f"Erro: {e.stderr}")
        return False

def check_postgresql_installed():
    """Verifica se o PostgreSQL está instalado"""
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ PostgreSQL encontrado: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass

    print("❌ PostgreSQL não encontrado")
    return False

def install_postgresql():
    """Instala PostgreSQL baseado no sistema operacional"""
    print("📦 Instalando PostgreSQL...")

    # Detectar sistema operacional
    if sys.platform.startswith('linux'):
        # Ubuntu/Debian
        if run_command("which apt-get", check=False):
            commands = [
                "sudo apt-get update",
                "sudo apt-get install -y postgresql postgresql-contrib python3-dev libpq-dev"
            ]
        # CentOS/RHEL/Fedora
        elif run_command("which yum", check=False):
            commands = [
                "sudo yum install -y postgresql-server postgresql-contrib python3-devel postgresql-devel"
            ]
        elif run_command("which dnf", check=False):
            commands = [
                "sudo dnf install -y postgresql-server postgresql-contrib python3-devel postgresql-devel"
            ]
        else:
            print("❌ Sistema Linux não suportado automaticamente")
            return False

    elif sys.platform == 'darwin':
        # macOS
        if run_command("which brew", check=False):
            commands = ["brew install postgresql"]
        else:
            print("❌ Homebrew não encontrado. Instale o Homebrew primeiro.")
            return False

    else:
        print("❌ Sistema operacional não suportado")
        return False

    for cmd in commands:
        if not run_command(cmd):
            return False

    return True

def start_postgresql_service():
    """Inicia o serviço do PostgreSQL"""
    print("🚀 Iniciando serviço PostgreSQL...")

    if sys.platform.startswith('linux'):
        return run_command("sudo systemctl start postgresql")
    elif sys.platform == 'darwin':
        return run_command("brew services start postgresql")

    return True

def create_database_and_user():
    """Cria database e usuário para o projeto"""
    print("🗃️  Configurando database e usuário...")

    db_name = "symplifika_db"
    db_user = "symplifika_user"
    db_password = "symplifika_pass123"

    try:
        # Conectar como superuser postgres
        conn = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password=""  # Assumindo que não há senha para postgres local
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Criar usuário
        try:
            cursor.execute(
                sql.SQL("CREATE USER {} WITH PASSWORD %s").format(
                    sql.Identifier(db_user)
                ),
                [db_password]
            )
            print(f"✅ Usuário {db_user} criado")
        except psycopg2.errors.DuplicateObject:
            print(f"ℹ️  Usuário {db_user} já existe")

        # Criar database
        try:
            cursor.execute(
                sql.SQL("CREATE DATABASE {} OWNER {}").format(
                    sql.Identifier(db_name),
                    sql.Identifier(db_user)
                )
            )
            print(f"✅ Database {db_name} criado")
        except psycopg2.errors.DuplicateDatabase:
            print(f"ℹ️  Database {db_name} já existe")

        # Dar privilégios
        cursor.execute(
            sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
                sql.Identifier(db_name),
                sql.Identifier(db_user)
            )
        )

        cursor.close()
        conn.close()

        return db_name, db_user, db_password

    except psycopg2.Error as e:
        print(f"❌ Erro ao configurar database: {e}")
        return None, None, None

def create_env_file(db_name, db_user, db_password):
    """Cria arquivo .env com configurações do PostgreSQL"""
    print("📝 Criando arquivo .env...")

    env_content = f"""# Configurações do Django
DEBUG=True
SECRET_KEY={get_random_secret_key()}

# Configurações do PostgreSQL local
DATABASE_URL=postgresql://{db_user}:{db_password}@localhost:5432/{db_name}

# Configurações de CORS (para desenvolvimento)
CORS_ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000,http://127.0.0.1:3000
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# API Keys (configure conforme necessário)
GEMINI_API_KEY=your_gemini_api_key_here

# Configurações de email (opcional)
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your_email@gmail.com
# EMAIL_HOST_PASSWORD=your_app_password
"""

    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Arquivo .env criado com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar arquivo .env: {e}")
        return False

def install_python_dependencies():
    """Instala dependências Python incluindo psycopg2"""
    print("📦 Instalando dependências Python...")

    commands = [
        "pip install --upgrade pip",
        "pip install psycopg2-binary",
        "pip install python-decouple"
    ]

    for cmd in commands:
        if not run_command(cmd):
            return False

    return True

def run_django_setup():
    """Executa configurações iniciais do Django"""
    print("🔧 Configurando Django com PostgreSQL...")

    commands = [
        "python manage.py migrate",
        "python manage.py collectstatic --noinput"
    ]

    for cmd in commands:
        if not run_command(cmd):
            return False

    return True

def create_superuser():
    """Cria superusuário Django"""
    print("👤 Criando superusuário Django...")
    print("Você precisará fornecer informações para o superusuário:")

    return run_command("python manage.py createsuperuser")

def main():
    """Função principal"""
    print("🚀 Configuração do PostgreSQL para Symplifika Django")
    print("=" * 50)

    # Verificar se PostgreSQL está instalado
    if not check_postgresql_installed():
        print("📦 PostgreSQL não encontrado. Iniciando instalação...")
        if not install_postgresql():
            print("❌ Falha na instalação do PostgreSQL")
            sys.exit(1)

    # Iniciar serviço PostgreSQL
    if not start_postgresql_service():
        print("⚠️  Não foi possível iniciar o PostgreSQL automaticamente")
        print("Por favor, inicie manualmente o serviço PostgreSQL")

    # Instalar dependências Python
    if not install_python_dependencies():
        print("❌ Falha na instalação das dependências Python")
        sys.exit(1)

    # Configurar database e usuário
    db_name, db_user, db_password = create_database_and_user()
    if not all([db_name, db_user, db_password]):
        print("❌ Falha na configuração do database")
        sys.exit(1)

    # Criar arquivo .env
    if not create_env_file(db_name, db_user, db_password):
        print("❌ Falha na criação do arquivo .env")
        sys.exit(1)

    # Configurar Django
    if not run_django_setup():
        print("❌ Falha na configuração do Django")
        sys.exit(1)

    # Criar superusuário
    print("\n👤 Agora vamos criar um superusuário para acessar o admin do Django")
    create_superuser()

    print("\n🎉 Configuração concluída com sucesso!")
    print("=" * 50)
    print("📋 Resumo da configuração:")
    print(f"   • Database: {db_name}")
    print(f"   • Usuário: {db_user}")
    print(f"   • Host: localhost:5432")
    print(f"   • Arquivo .env criado com DATABASE_URL")
    print("\n🚀 Para iniciar o servidor de desenvolvimento:")
    print("   python manage.py runserver")
    print("\n📱 Para acessar o admin:")
    print("   http://127.0.0.1:8000/admin/")
    print("\n📄 Variáveis de ambiente salvas em .env")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Configuração interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)
