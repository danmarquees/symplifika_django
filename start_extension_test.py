#!/usr/bin/env python
"""
Script para iniciar o Django server otimizado para testes da extensão Chrome.
Este script configura o servidor para funcionar perfeitamente com a extensão.
"""

import os
import sys
import subprocess
from pathlib import Path

def find_venv_python():
    """Encontra o interpretador Python do ambiente virtual"""
    # Verifica se já está em um venv ativo
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        return sys.executable

    # Procura por venv na pasta atual
    venv_paths = [
        'venv/bin/python',      # Linux/Mac
        'venv/Scripts/python.exe',  # Windows
        '.venv/bin/python',     # Linux/Mac alternativo
        '.venv/Scripts/python.exe'  # Windows alternativo
    ]

    for venv_path in venv_paths:
        if Path(venv_path).exists():
            return str(Path(venv_path).absolute())

    # Fallback para python do sistema
    print("⚠️  Virtual environment não encontrado, usando Python do sistema")
    return sys.executable

def setup_environment():
    """Configura variáveis de ambiente para extensão"""
    os.environ['DEBUG'] = 'True'
    os.environ['ALLOWED_HOSTS'] = 'localhost,127.0.0.1,0.0.0.0,testserver'
    os.environ['CORS_ALLOW_ALL_ORIGINS'] = 'True'
    print("✅ Variáveis de ambiente configuradas para extensão")

def check_requirements():
    """Verifica se todas as dependências estão instaladas"""
    python_path = find_venv_python()

    try:
        # Usa o Python do venv para verificar dependências
        result = subprocess.run([
            python_path, '-c',
            'import django, corsheaders, rest_framework; print("Django", django.get_version())'
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ {result.stdout.strip()} instalado")
            print("✅ Dependências verificadas")
            return True, python_path
        else:
            print(f"❌ Erro ao verificar dependências: {result.stderr}")
            return False, python_path

    except Exception as e:
        print(f"❌ Erro ao verificar dependências: {e}")
        print("Execute: pip install -r requirements.txt")
        return False, python_path

def run_migrations(python_path):
    """Executa migrações se necessário"""
    try:
        print("🔄 Verificando migrações...")
        result = subprocess.run(
            [python_path, 'manage.py', 'migrate', '--check'],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("🔄 Executando migrações...")
            subprocess.run([python_path, 'manage.py', 'migrate'], check=True)
            print("✅ Migrações executadas")
        else:
            print("✅ Migrações já aplicadas")

    except subprocess.CalledProcessError:
        print("⚠️  Erro nas migrações, mas continuando...")

def create_superuser_if_needed(python_path):
    """Cria superusuário se não existir"""
    try:
        # Usa script Django para criar superusuário
        check_script = '''
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "symplifika.settings")
django.setup()
from django.contrib.auth.models import User
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser("admin", "admin@test.com", "admin123")
    print("✅ Usuário criado: admin / admin123")
else:
    print("✅ Superusuário já existe")
'''

        result = subprocess.run([python_path, '-c', check_script],
                              capture_output=True, text=True)

        if result.stdout:
            print(result.stdout.strip())
        if result.stderr:
            print(f"⚠️  Aviso: {result.stderr.strip()}")

    except Exception as e:
        print(f"⚠️  Erro ao criar superusuário: {e}")

def start_server(python_path):
    """Inicia o servidor Django"""
    print("\n" + "="*50)
    print("🚀 INICIANDO SERVIDOR PARA EXTENSÃO CHROME")
    print("="*50)
    print(f"📍 URL: http://127.0.0.1:8000")
    print(f"🔑 Admin: http://127.0.0.1:8000/admin/")
    print(f"📱 Dashboard: http://127.0.0.1:8000/dashboard/")
    print(f"🔌 API Token: http://127.0.0.1:8000/api/token/")
    print("="*50)
    print("💡 Para usar a extensão:")
    print("   1. Faça login na extensão")
    print("   2. Crie atalhos no dashboard")
    print("   3. Sincronize na extensão")
    print("   4. Digite !atalho + Espaço")
    print("="*50)
    print("⏹️  Pressione Ctrl+C para parar")
    print("\n")

    try:
        # Inicia servidor em 127.0.0.1 (mais compatível que 0.0.0.0)
        subprocess.run([
            python_path, 'manage.py', 'runserver', '127.0.0.1:8000'
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado pelo usuário")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao iniciar servidor: {e}")

def main():
    """Função principal"""
    print("🔧 SYMPLIFIKA - SETUP PARA EXTENSÃO CHROME")
    print("=" * 50)

    # Verifica se estamos no diretório correto
    if not Path('manage.py').exists():
        print("❌ Execute este script no diretório raiz do projeto Django")
        sys.exit(1)

    # Setup
    setup_environment()

    # Verifica dependências e obtém path do Python
    deps_ok, python_path = check_requirements()
    if not deps_ok:
        print("\n💡 Tente ativar o ambiente virtual primeiro:")
        print("   source venv/bin/activate  # Linux/Mac")
        print("   venv\\Scripts\\activate     # Windows")
        sys.exit(1)

    # Setup do Django
    run_migrations(python_path)
    create_superuser_if_needed(python_path)

    # Inicia servidor
    start_server(python_path)

if __name__ == '__main__':
    main()
