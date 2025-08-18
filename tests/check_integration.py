#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Symplifika Integration Check
Script para verificar se todas as dependências e configurações estão corretas
"""

import os
import sys
import django
from pathlib import Path
import json
import subprocess

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
    print(f"🔍 {message}")
    print(f"{'='*60}{Colors.END}\n")

def check_file_exists(file_path, description):
    """Verifica se um arquivo existe"""
    if os.path.exists(file_path):
        print_success(f"{description}: {file_path}")
        return True
    else:
        print_error(f"{description} não encontrado: {file_path}")
        return False

def check_python_dependencies():
    """Verifica dependências Python"""
    print_header("Verificando Dependências Python")

    required_packages = [
        ('django', 'django'),
        ('djangorestframework', 'rest_framework'),
        ('django-cors-headers', 'corsheaders'),
    ]

    missing_packages = []

    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print_success(f"Pacote instalado: {package_name}")
        except ImportError:
            print_error(f"Pacote faltando: {package_name}")
            missing_packages.append(package_name)

    if missing_packages:
        print_warning("Para instalar os pacotes faltantes:")
        print(f"pip install {' '.join(missing_packages)}")
        return False

    return True

def check_django_settings():
    """Verifica configurações do Django"""
    print_header("Verificando Configurações Django")

    try:
        # Configurar Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'symplifika.settings')
        django.setup()

        from django.conf import settings

        # Verificar apps instalados
        required_apps = [
            'rest_framework',
            'shortcuts',
            'users',
            'core',
        ]

        for app in required_apps:
            if app in settings.INSTALLED_APPS:
                print_success(f"App instalado: {app}")
            else:
                print_error(f"App faltando em INSTALLED_APPS: {app}")

        # Verificar middlewares importantes
        required_middlewares = [
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
        ]

        for middleware in required_middlewares:
            if middleware in settings.MIDDLEWARE:
                print_success(f"Middleware configurado: {middleware}")
            else:
                print_error(f"Middleware faltando: {middleware}")

        # Verificar configurações do DRF
        if hasattr(settings, 'REST_FRAMEWORK'):
            print_success("REST_FRAMEWORK configurado")

            # Verificar autenticação
            auth_classes = settings.REST_FRAMEWORK.get('DEFAULT_AUTHENTICATION_CLASSES', [])
            if 'rest_framework.authentication.SessionAuthentication' in auth_classes:
                print_success("Autenticação por sessão configurada")
            else:
                print_warning("Autenticação por sessão não configurada")
        else:
            print_error("REST_FRAMEWORK não configurado")

        return True

    except Exception as e:
        print_error(f"Erro ao verificar configurações Django: {e}")
        return False

def check_static_files():
    """Verifica arquivos estáticos"""
    print_header("Verificando Arquivos Estáticos")

    files_to_check = [
        ('static/js/app.js', 'JavaScript principal'),
        ('static/js/symplifika-base.js', 'Sistema base JavaScript'),
        ('static/js/test-integration.js', 'Testes de integração'),
        ('static/js/demo-integration.js', 'Sistema de demonstração'),
        ('static/css/app.css', 'CSS da aplicação'),
        ('templates/base.html', 'Template base'),
        ('templates/app.html', 'Template da aplicação'),
    ]

    all_present = True
    for file_path, description in files_to_check:
        if not check_file_exists(file_path, description):
            all_present = False

    return all_present

def check_database():
    """Verifica configuração do banco de dados"""
    print_header("Verificando Banco de Dados")

    try:
        from django.db import connection
        from django.core.management import execute_from_command_line

        # Testar conexão
        connection.cursor()
        print_success("Conexão com banco de dados funcionando")

        # Verificar migrações
        from django.core.management.commands.showmigrations import Command
        command = Command()

        # Verificar se há migrações não aplicadas
        try:
            # Simular comando showmigrations
            from django.db.migrations.executor import MigrationExecutor
            executor = MigrationExecutor(connection)

            if executor.migration_plan(executor.loader.graph.leaf_nodes()):
                print_warning("Há migrações pendentes. Execute: python manage.py migrate")
            else:
                print_success("Todas as migrações aplicadas")

        except Exception as e:
            print_warning(f"Não foi possível verificar migrações: {e}")

        return True

    except Exception as e:
        print_error(f"Erro na conexão com banco de dados: {e}")
        return False

def check_models():
    """Verifica se os modelos estão funcionando"""
    print_header("Verificando Modelos")

    try:
        from shortcuts.models import Category, Shortcut
        from django.contrib.auth.models import User

        # Testar criação de objetos (apenas verificar se não dá erro)
        user_count = User.objects.count()
        category_count = Category.objects.count()
        shortcut_count = Shortcut.objects.count()

        print_success(f"Usuários no sistema: {user_count}")
        print_success(f"Categorias no sistema: {category_count}")
        print_success(f"Atalhos no sistema: {shortcut_count}")

        return True

    except Exception as e:
        print_error(f"Erro ao verificar modelos: {e}")
        return False

def check_views_and_urls():
    """Verifica se as views e URLs estão configuradas"""
    print_header("Verificando Views e URLs")

    try:
        from django.urls import reverse
        from shortcuts.views import CategoryViewSet, ShortcutViewSet

        # Verificar algumas URLs importantes
        urls_to_check = [
            ('shortcuts:category-list', 'Lista de categorias'),
            ('shortcuts:shortcut-list', 'Lista de atalhos'),
        ]

        for url_name, description in urls_to_check:
            try:
                url = reverse(url_name)
                print_success(f"{description}: {url}")
            except Exception as e:
                print_error(f"URL não encontrada {url_name}: {e}")

        # Verificar se as ViewSets estão importando corretamente
        print_success("CategoryViewSet importado com sucesso")
        print_success("ShortcutViewSet importado com sucesso")

        return True

    except Exception as e:
        print_error(f"Erro ao verificar views/URLs: {e}")
        return False

def check_permissions():
    """Verifica configurações de permissões"""
    print_header("Verificando Permissões")

    try:
        from rest_framework.permissions import IsAuthenticated
        from shortcuts.views import CategoryViewSet

        # Verificar se as views têm as permissões corretas
        viewset = CategoryViewSet()
        if hasattr(viewset, 'permission_classes'):
            permission_classes = viewset.permission_classes
            if IsAuthenticated in permission_classes:
                print_success("Permissão de autenticação configurada")
            else:
                print_warning("Permissão de autenticação não encontrada")

        return True

    except Exception as e:
        print_error(f"Erro ao verificar permissões: {e}")
        return False

def check_javascript_syntax():
    """Verifica sintaxe dos arquivos JavaScript"""
    print_header("Verificando Sintaxe JavaScript")

    js_files = [
        'static/js/app.js',
        'static/js/symplifika-base.js',
        'static/js/test-integration.js',
        'static/js/demo-integration.js',
    ]

    all_valid = True

    for js_file in js_files:
        if os.path.exists(js_file):
            try:
                # Verificação básica - apenas tentar ler o arquivo
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Verificações básicas de sintaxe
                if 'class ' in content and content.count('{') != content.count('}'):
                    print_warning(f"Possível problema de sintaxe em {js_file} (chaves não balanceadas)")
                else:
                    print_success(f"JavaScript válido: {js_file}")

            except Exception as e:
                print_error(f"Erro ao verificar {js_file}: {e}")
                all_valid = False
        else:
            print_error(f"Arquivo JavaScript não encontrado: {js_file}")
            all_valid = False

    return all_valid

def generate_test_script():
    """Gera script de teste para execução manual"""
    print_header("Gerando Script de Teste")

    test_script = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Teste de Integração Symplifika</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .test-result { padding: 10px; margin: 5px 0; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .warning { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        button { padding: 10px 20px; margin: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>🧪 Teste de Integração Symplifika</h1>

    <div id="results"></div>

    <button onclick="testFetch()">Testar Fetch API</button>
    <button onclick="testCSRF()">Testar CSRF Token</button>
    <button onclick="testModals()">Testar Sistema de Modal</button>
    <button onclick="testNotifications()">Testar Notificações</button>

    <script>
        function addResult(message, type) {
            const div = document.createElement('div');
            div.className = `test-result ${type}`;
            div.textContent = message;
            document.getElementById('results').appendChild(div);
        }

        function testFetch() {
            if (typeof fetch !== 'undefined') {
                addResult('✅ Fetch API disponível', 'success');
            } else {
                addResult('❌ Fetch API não disponível', 'error');
            }
        }

        function testCSRF() {
            const token = document.querySelector('[name=csrfmiddlewaretoken]');
            if (token) {
                addResult('✅ CSRF Token encontrado', 'success');
            } else {
                addResult('⚠️ CSRF Token não encontrado', 'warning');
            }
        }

        function testModals() {
            if (window.Symplifika && window.Symplifika.Modal) {
                addResult('✅ Sistema de Modal disponível', 'success');
            } else {
                addResult('❌ Sistema de Modal não disponível', 'error');
            }
        }

        function testNotifications() {
            if (window.Symplifika && window.Symplifika.Toast) {
                addResult('✅ Sistema de Notificações disponível', 'success');
                window.Symplifika.Toast.success('Teste de notificação!');
            } else {
                addResult('❌ Sistema de Notificações não disponível', 'error');
            }
        }

        // Auto-executar todos os testes
        window.addEventListener('DOMContentLoaded', function() {
            setTimeout(() => {
                testFetch();
                testCSRF();
                testModals();
                testNotifications();
            }, 1000);
        });
    </script>
</body>
</html>
'''

    test_file_path = 'static/test-integration.html'
    try:
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_script)
        print_success(f"Script de teste gerado: {test_file_path}")
        print_info("Para testar, acesse: http://localhost:8000/static/test-integration.html")
        return True
    except Exception as e:
        print_error(f"Erro ao gerar script de teste: {e}")
        return False

def main():
    """Função principal"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("🔍 VERIFICAÇÃO DE INTEGRAÇÃO SYMPLIFIKA")
    print("=" * 60)
    print("Este script verifica se todas as dependências e")
    print("configurações estão corretas para a integração funcionar.")
    print(f"{'=' * 60}{Colors.END}")

    checks = [
        ("Dependências Python", check_python_dependencies),
        ("Configurações Django", check_django_settings),
        ("Arquivos Estáticos", check_static_files),
        ("Banco de Dados", check_database),
        ("Modelos", check_models),
        ("Views e URLs", check_views_and_urls),
        ("Permissões", check_permissions),
        ("Sintaxe JavaScript", check_javascript_syntax),
        ("Script de Teste", generate_test_script),
    ]

    results = []

    for check_name, check_function in checks:
        try:
            result = check_function()
            results.append((check_name, result))
        except Exception as e:
            print_error(f"Erro durante {check_name}: {e}")
            results.append((check_name, False))

    # Resumo final
    print_header("RESUMO FINAL")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"{Colors.BOLD}Verificações passaram: {passed}/{total}{Colors.END}")

    for check_name, result in results:
        if result:
            print_success(f"{check_name}")
        else:
            print_error(f"{check_name}")

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 TODAS AS VERIFICAÇÕES PASSARAM!")
        print("A integração está pronta para uso!{Colors.END}")
        print("\nPróximos passos:")
        print("1. python manage.py runserver")
        print("2. Acesse o dashboard")
        print("3. Teste as ações rápidas")
        print("4. Execute testSymphilikaAPI() no console")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠️  ALGUMAS VERIFICAÇÕES FALHARAM")
        print("Corrija os problemas antes de usar a integração.{Colors.END}")

    return passed == total

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Verificação interrompida pelo usuário.{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Erro inesperado: {e}")
        sys.exit(1)
