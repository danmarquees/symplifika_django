#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Symplifika Integration Installer
Script para instalar e configurar automaticamente a integração de APIs
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Cores para output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def print_header(message):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print(f"🚀 {message}")
    print(f"{'='*60}{Colors.END}\n")

def check_requirements():
    """Verifica se os requisitos estão instalados"""
    print_header("Verificando Requisitos")

    # Verificar Python
    if sys.version_info < (3, 8):
        print_error("Python 3.8+ é necessário")
        return False

    print_success(f"Python {sys.version.split()[0]} encontrado")

    # Verificar Django
    try:
        import django
        print_success(f"Django {django.get_version()} encontrado")
    except ImportError:
        print_error("Django não encontrado. Execute: pip install django")
        return False

    # Verificar Django REST Framework
    try:
        import rest_framework
        print_success(f"Django REST Framework {rest_framework.VERSION} encontrado")
    except ImportError:
        print_error("Django REST Framework não encontrado. Execute: pip install djangorestframework")
        return False

    return True

def backup_existing_files():
    """Cria backup dos arquivos existentes"""
    print_header("Criando Backup")

    backup_dir = Path('backup_integration')
    backup_dir.mkdir(exist_ok=True)

    files_to_backup = [
        'static/js/app.js',
        'static/js/base.js',
        'templates/base.html',
        'templates/app.html',
    ]

    for file_path in files_to_backup:
        if Path(file_path).exists():
            backup_path = backup_dir / Path(file_path).name
            shutil.copy2(file_path, backup_path)
            print_success(f"Backup criado: {backup_path}")

    return True

def install_dependencies():
    """Instala dependências necessárias"""
    print_header("Instalando Dependências")

    dependencies = [
        'djangorestframework',
        'django-cors-headers',
        'django-filter',
    ]

    for dep in dependencies:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
            print_success(f"Instalado: {dep}")
        except subprocess.CalledProcessError:
            print_error(f"Erro ao instalar: {dep}")
            return False

    return True

def update_settings():
    """Atualiza configurações do Django"""
    print_header("Atualizando Configurações")

    settings_path = Path('symplifika/settings.py')

    if not settings_path.exists():
        print_error("Arquivo settings.py não encontrado")
        return False

    # Ler arquivo existente
    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Verificar se já tem as configurações
    if 'rest_framework' in content.lower():
        print_info("REST Framework já configurado")
        return True

    # Configurações a adicionar
    rest_framework_config = '''

# Django REST Framework
INSTALLED_APPS += [
    'rest_framework',
    'corsheaders',
]

MIDDLEWARE += [
    'corsheaders.middleware.CorsMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

CORS_ALLOW_CREDENTIALS = True
'''

    # Adicionar configurações
    with open(settings_path, 'a', encoding='utf-8') as f:
        f.write(rest_framework_config)

    print_success("Configurações do REST Framework adicionadas")
    return True

def create_directories():
    """Cria diretórios necessários"""
    print_header("Criando Estrutura de Diretórios")

    directories = [
        'static/js',
        'static/css',
        'templates',
        'static/images',
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print_success(f"Diretório criado/verificado: {directory}")

    return True

def verify_files():
    """Verifica se todos os arquivos necessários existem"""
    print_header("Verificando Arquivos da Integração")

    required_files = [
        'static/js/app.js',
        'static/js/symplifika-base.js',
        'static/js/test-integration.js',
        'static/js/demo-integration.js',
        'static/css/app.css',
        'templates/app.html',
        'templates/base.html',
    ]

    missing_files = []

    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"Arquivo encontrado: {file_path}")
        else:
            print_error(f"Arquivo faltando: {file_path}")
            missing_files.append(file_path)

    if missing_files:
        print_warning("Alguns arquivos estão faltando. Certifique-se de que todos os arquivos da integração foram criados.")
        return False

    return True

def run_migrations():
    """Executa migrações do Django"""
    print_header("Executando Migrações")

    try:
        # Fazer migrações
        subprocess.check_call([sys.executable, 'manage.py', 'makemigrations'])
        print_success("Migrações criadas")

        # Aplicar migrações
        subprocess.check_call([sys.executable, 'manage.py', 'migrate'])
        print_success("Migrações aplicadas")

        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Erro ao executar migrações: {e}")
        return False

def collect_static():
    """Coleta arquivos estáticos"""
    print_header("Coletando Arquivos Estáticos")

    try:
        subprocess.check_call([sys.executable, 'manage.py', 'collectstatic', '--noinput'])
        print_success("Arquivos estáticos coletados")
        return True
    except subprocess.CalledProcessError as e:
        print_warning(f"Erro ao coletar estáticos (pode ser ignorado em desenvolvimento): {e}")
        return True

def create_superuser():
    """Cria superusuário se não existir"""
    print_header("Configurando Superusuário")

    try:
        # Verificar se já existe superusuário
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'symplifika.settings')
        import django
        django.setup()

        from django.contrib.auth.models import User

        if User.objects.filter(is_superuser=True).exists():
            print_info("Superusuário já existe")
            return True

        print_info("Criando superusuário...")
        print_info("Use as credenciais: admin / admin123")

        # Criar superusuário programaticamente
        User.objects.create_superuser(
            username='admin',
            email='admin@symplifika.com',
            password='admin123'
        )

        print_success("Superusuário criado: admin / admin123")
        return True

    except Exception as e:
        print_warning(f"Erro ao criar superusuário: {e}")
        print_info("Você pode criar manualmente com: python manage.py createsuperuser")
        return True

def run_tests():
    """Executa testes básicos"""
    print_header("Executando Testes Básicos")

    try:
        # Testar importações
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'symplifika.settings')
        import django
        django.setup()

        # Testar modelos
        from shortcuts.models import Category, Shortcut
        print_success("Modelos importados com sucesso")

        # Testar views
        from shortcuts.views import CategoryViewSet, ShortcutViewSet
        print_success("Views importadas com sucesso")

        # Testar URLs
        from django.urls import reverse
        reverse('shortcuts:category-list')
        print_success("URLs configuradas corretamente")

        return True

    except Exception as e:
        print_error(f"Erro nos testes: {e}")
        return False

def generate_usage_instructions():
    """Gera instruções de uso"""
    print_header("Gerando Instruções de Uso")

    instructions = """
# 🚀 SYMPLIFIKA - INTEGRAÇÃO INSTALADA COM SUCESSO!

## Como usar:

### 1. Iniciar o servidor
```bash
python manage.py runserver
```

### 2. Acessar o dashboard
```
http://localhost:8000/
```

### 3. Fazer login
- Usuário: admin
- Senha: admin123

### 4. Testar as funcionalidades
- Clique em "Criar Novo Atalho"
- Clique em "Nova Categoria"
- Use os atalhos recentes

### 5. Executar testes
No console do navegador:
```javascript
testSymphilikaAPI()
```

### 6. Demonstração
No console do navegador:
```javascript
startSymphilikaDemo()
```

## URLs importantes:
- Dashboard: http://localhost:8000/
- Admin: http://localhost:8000/admin/
- API Categorias: http://localhost:8000/shortcuts/api/categories/
- API Atalhos: http://localhost:8000/shortcuts/api/shortcuts/

## Arquivos modificados:
- static/js/app.js (aplicação principal)
- static/js/symplifika-base.js (sistema base)
- static/css/app.css (estilos)
- templates/base.html (template base)
- symplifika/settings.py (configurações)

## Suporte:
- Execute: python check_integration.py
- Verifique logs do console (F12)
- Consulte: README_INTEGRATION.md

Aproveite sua nova integração! 🎉
"""

    with open('INTEGRATION_INSTALLED.md', 'w', encoding='utf-8') as f:
        f.write(instructions)

    print_success("Instruções salvas em: INTEGRATION_INSTALLED.md")
    return True

def main():
    """Função principal do instalador"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("🚀 INSTALADOR DE INTEGRAÇÃO SYMPLIFIKA")
    print("=" * 60)
    print("Este script instala automaticamente todas as")
    print("dependências e configurações necessárias.")
    print(f"{'=' * 60}{Colors.END}")

    # Verificar se estamos no diretório correto
    if not Path('manage.py').exists():
        print_error("Execute este script no diretório raiz do projeto Django")
        return False

    steps = [
        ("Verificar Requisitos", check_requirements),
        ("Criar Backup", backup_existing_files),
        ("Instalar Dependências", install_dependencies),
        ("Criar Diretórios", create_directories),
        ("Verificar Arquivos", verify_files),
        ("Atualizar Configurações", update_settings),
        ("Executar Migrações", run_migrations),
        ("Coletar Estáticos", collect_static),
        ("Configurar Superusuário", create_superuser),
        ("Executar Testes", run_tests),
        ("Gerar Instruções", generate_usage_instructions),
    ]

    results = []

    for step_name, step_function in steps:
        try:
            result = step_function()
            results.append((step_name, result))

            if not result:
                print_error(f"Falha em: {step_name}")
                break

        except Exception as e:
            print_error(f"Erro em {step_name}: {e}")
            results.append((step_name, False))
            break

    # Resumo final
    print_header("RESULTADO DA INSTALAÇÃO")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"{Colors.BOLD}Etapas concluídas: {passed}/{total}{Colors.END}")

    for step_name, result in results:
        if result:
            print_success(f"{step_name}")
        else:
            print_error(f"{step_name}")

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!{Colors.END}")
        print("\nPróximos passos:")
        print("1. python manage.py runserver")
        print("2. Acesse: http://localhost:8000/")
        print("3. Login: admin / admin123")
        print("4. Teste as ações rápidas!")
        print("5. Leia: INTEGRATION_INSTALLED.md")

        # Perguntar se quer iniciar o servidor
        try:
            choice = input(f"\n{Colors.BLUE}Iniciar servidor agora? (s/N): {Colors.END}").lower()
            if choice in ['s', 'sim', 'y', 'yes']:
                print_info("Iniciando servidor...")
                subprocess.call([sys.executable, 'manage.py', 'runserver'])
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Instalação concluída!{Colors.END}")

    else:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠️  INSTALAÇÃO INCOMPLETA{Colors.END}")
        print("Corrija os problemas e execute novamente.")
        print("Backup dos arquivos em: backup_integration/")

    return passed == total

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Instalação interrompida pelo usuário.{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
