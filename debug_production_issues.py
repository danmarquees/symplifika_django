#!/usr/bin/env python
"""
Script de diagnóstico para problemas em produção
Identifica e resolve problemas comuns que podem causar erros 500
"""

import os
import sys
import django
from pathlib import Path
import traceback

# Configurar o ambiente Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'symplifika.settings')

try:
    django.setup()
except Exception as e:
    print(f"❌ Erro ao configurar Django: {e}")
    sys.exit(1)

from django.conf import settings
from django.db import connection
from django.contrib.auth import get_user_model
from django.test import RequestFactory
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database_connection():
    """Testa conexão com o banco de dados"""
    print("🔍 Verificando conexão com o banco de dados...")

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result[0] == 1:
                print("✅ Conexão com banco de dados OK")
                return True
    except Exception as e:
        print(f"❌ Erro na conexão com banco: {e}")
        return False

def check_database_tables():
    """Verifica se as tabelas necessárias existem"""
    print("\n🔍 Verificando tabelas do banco de dados...")

    required_tables = [
        'auth_user',
        'shortcuts_category',
        'shortcuts_shortcut',
        'shortcuts_shortcutusage',
        'users_userprofile'
    ]

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            existing_tables = [row[0] for row in cursor.fetchall()]

            missing_tables = []
            for table in required_tables:
                if table in existing_tables:
                    print(f"✅ Tabela {table} existe")
                else:
                    print(f"❌ Tabela {table} FALTANDO")
                    missing_tables.append(table)

            if missing_tables:
                print(f"\n⚠️  Execute: python manage.py migrate")
                return False
            return True

    except Exception as e:
        print(f"❌ Erro ao verificar tabelas: {e}")
        return False

def check_user_profiles():
    """Verifica se os perfis de usuário estão corretos"""
    print("\n🔍 Verificando perfis de usuário...")

    try:
        User = get_user_model()
        users_without_profile = []

        for user in User.objects.all():
            if not hasattr(user, 'profile'):
                users_without_profile.append(user.username)

        if users_without_profile:
            print(f"❌ Usuários sem perfil: {users_without_profile}")
            print("⚠️  Execute: python manage.py create_user_profiles")
            return False
        else:
            print("✅ Todos os usuários têm perfis")
            return True

    except Exception as e:
        print(f"❌ Erro ao verificar perfis: {e}")
        return False

def test_shortcuts_api():
    """Testa os endpoints da API de atalhos"""
    print("\n🔍 Testando endpoints da API de atalhos...")

    try:
        from shortcuts.views import ShortcutViewSet
        from django.contrib.auth import get_user_model
        from rest_framework.test import APIRequestFactory

        User = get_user_model()
        user = User.objects.first()

        if not user:
            print("⚠️  Nenhum usuário encontrado, criando usuário teste...")
            user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123'
            )

        factory = APIRequestFactory()

        # Teste endpoint stats
        print("  📊 Testando /shortcuts/api/shortcuts/stats/...")
        request = factory.get('/shortcuts/api/shortcuts/stats/')
        request.user = user

        view = ShortcutViewSet()
        view.request = request

        response = view.stats(request)

        if response.status_code == 200:
            print(f"  ✅ Stats OK - {len(response.data)} campos retornados")
        else:
            print(f"  ❌ Stats falhou - Status: {response.status_code}")
            return False

        # Teste endpoint list
        print("  📝 Testando /shortcuts/api/shortcuts/...")
        request = factory.get('/shortcuts/api/shortcuts/')
        request.user = user

        view.request = request
        response = view.list(request)

        if response.status_code == 200:
            print(f"  ✅ List OK")
        else:
            print(f"  ❌ List falhou - Status: {response.status_code}")
            return False

        return True

    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")
        traceback.print_exc()
        return False

def check_static_files():
    """Verifica configuração de arquivos estáticos"""
    print("\n🔍 Verificando arquivos estáticos...")

    try:
        print(f"  STATIC_URL: {settings.STATIC_URL}")
        print(f"  STATIC_ROOT: {settings.STATIC_ROOT}")
        print(f"  STATICFILES_DIRS: {settings.STATICFILES_DIRS}")

        # Verificar se o diretório static existe
        if settings.STATIC_ROOT and Path(settings.STATIC_ROOT).exists():
            print("  ✅ STATIC_ROOT existe")
        else:
            print("  ❌ STATIC_ROOT não existe")
            print("  ⚠️  Execute: python manage.py collectstatic")

        # Verificar favicon
        favicon_paths = [
            Path(settings.STATIC_ROOT or '') / 'images' / 'favicon.ico',
            Path('static') / 'images' / 'favicon.ico',
        ]

        favicon_exists = False
        for path in favicon_paths:
            if path.exists():
                print(f"  ✅ Favicon encontrado em: {path}")
                favicon_exists = True
                break

        if not favicon_exists:
            print("  ⚠️  Favicon não encontrado, será gerado automaticamente")

        return True

    except Exception as e:
        print(f"❌ Erro ao verificar arquivos estáticos: {e}")
        return False

def check_environment_variables():
    """Verifica variáveis de ambiente críticas"""
    print("\n🔍 Verificando variáveis de ambiente...")

    critical_vars = {
        'SECRET_KEY': 'Chave secreta do Django',
        'DEBUG': 'Modo de debug',
        'ALLOWED_HOSTS': 'Hosts permitidos',
        'DATABASE_URL': 'URL do banco de dados',
    }

    optional_vars = {
        'GEMINI_API_KEY': 'Chave da API Gemini',
        'RENDER_EXTERNAL_HOSTNAME': 'Hostname do Render',
    }

    issues = []

    for var, description in critical_vars.items():
        value = getattr(settings, var, None) or os.environ.get(var)
        if value:
            if var in ['SECRET_KEY']:
                print(f"  ✅ {var}: {str(value)[:10]}...")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: NÃO CONFIGURADA ({description})")
            issues.append(var)

    for var, description in optional_vars.items():
        value = getattr(settings, var, None) or os.environ.get(var)
        if value:
            print(f"  ✅ {var}: {str(value)[:10]}...")
        else:
            print(f"  ⚠️  {var}: Não configurada ({description})")

    return len(issues) == 0

def check_gemini_integration():
    """Verifica integração com Gemini"""
    print("\n🔍 Verificando integração com Gemini...")

    try:
        from shortcuts.services import AIService

        service = AIService()

        if not service.api_key:
            print("  ⚠️  GEMINI_API_KEY não configurada")
            print("  📝 Configure em: https://makersuite.google.com/app/apikey")
            return False

        print(f"  ✅ API Key configurada: {service.api_key[:10]}...")
        print(f"  📱 Modelo: {service.model_name}")

        # Teste básico
        status = service.check_api_status()

        if status['api_accessible']:
            print("  ✅ API Gemini acessível")
            return True
        else:
            print(f"  ❌ API Gemini inacessível: {status.get('error', 'Erro desconhecido')}")
            return False

    except Exception as e:
        print(f"  ❌ Erro na verificação Gemini: {e}")
        return False

def fix_common_issues():
    """Tenta corrigir problemas comuns automaticamente"""
    print("\n🔧 Tentando corrigir problemas comuns...")

    fixes_applied = []

    try:
        # 1. Criar profiles para usuários sem profile
        from django.contrib.auth import get_user_model
        from users.models import UserProfile

        User = get_user_model()
        users_without_profile = []

        for user in User.objects.all():
            if not hasattr(user, 'profile'):
                users_without_profile.append(user)

        if users_without_profile:
            for user in users_without_profile:
                UserProfile.objects.create(user=user)
                print(f"  ✅ Profile criado para usuário: {user.username}")
            fixes_applied.append(f"Profiles criados para {len(users_without_profile)} usuários")

        # 2. Criar diretório de imagens estáticas
        images_dir = Path('static/images')
        if not images_dir.exists():
            images_dir.mkdir(parents=True, exist_ok=True)
            print("  ✅ Diretório static/images criado")
            fixes_applied.append("Diretório de imagens criado")

        # 3. Verificar e migrar banco se necessário
        from django.core.management import call_command
        from django.db import connection

        # Verificar se há migrações pendentes
        try:
            from django.core.management.commands.migrate import Command as MigrateCommand
            # Se chegou até aqui, pode tentar migrate
            print("  🔄 Verificando migrações pendentes...")
            call_command('migrate', '--check', verbosity=0)
            print("  ✅ Todas as migrações estão aplicadas")
        except Exception:
            print("  🔄 Aplicando migrações pendentes...")
            try:
                call_command('migrate', verbosity=1)
                fixes_applied.append("Migrações aplicadas")
            except Exception as e:
                print(f"  ❌ Erro ao aplicar migrações: {e}")

    except Exception as e:
        print(f"❌ Erro ao aplicar correções: {e}")

    if fixes_applied:
        print(f"\n✅ Correções aplicadas:")
        for fix in fixes_applied:
            print(f"  • {fix}")
    else:
        print("\n📝 Nenhuma correção automática foi necessária")

def generate_summary_report():
    """Gera um relatório resumo dos problemas encontrados"""
    print("\n" + "="*60)
    print("📋 RELATÓRIO DE DIAGNÓSTICO")
    print("="*60)

    tests = [
        ("Conexão com banco de dados", check_database_connection),
        ("Tabelas do banco", check_database_tables),
        ("Perfis de usuário", check_user_profiles),
        ("API de atalhos", test_shortcuts_api),
        ("Arquivos estáticos", check_static_files),
        ("Variáveis de ambiente", check_environment_variables),
        ("Integração Gemini", check_gemini_integration),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro no teste '{test_name}': {e}")
            results.append((test_name, False))

    print("\n📊 RESUMO:")
    passed = 0
    total = len(results)

    critical_failures = []
    warnings = []

    for test_name, result in results:
        if result:
            print(f"✅ {test_name}")
            passed += 1
        else:
            print(f"❌ {test_name}")
            if test_name in ["Conexão com banco de dados", "Tabelas do banco", "API de atalhos"]:
                critical_failures.append(test_name)
            else:
                warnings.append(test_name)

    print(f"\nResultado: {passed}/{total} testes passaram")

    if critical_failures:
        print(f"\n🚨 PROBLEMAS CRÍTICOS:")
        for failure in critical_failures:
            print(f"  • {failure}")
        print("\nEsses problemas podem causar erros 500 na aplicação!")

    if warnings:
        print(f"\n⚠️  AVISOS:")
        for warning in warnings:
            print(f"  • {warning}")

    if passed == total:
        print("\n🎉 Todos os testes passaram! A aplicação deve funcionar corretamente.")
    elif len(critical_failures) == 0:
        print("\n✅ Não há problemas críticos, mas algumas otimizações podem ser feitas.")
    else:
        print("\n❌ Problemas críticos encontrados. Resolva-os antes de colocar em produção.")

    # Sugestões de correção
    print(f"\n💡 PRÓXIMOS PASSOS:")
    if critical_failures:
        print("1. Resolva os problemas críticos listados acima")
        print("2. Execute: python manage.py migrate")
        print("3. Execute: python manage.py collectstatic --noinput")
        print("4. Reinicie o servidor")

    if 'Integração Gemini' in [name for name, result in results if not result]:
        print("5. Configure GEMINI_API_KEY em https://makersuite.google.com/app/apikey")

    print("6. Execute novamente este script para verificar as correções")

    return len(critical_failures) == 0

def main():
    """Função principal do diagnóstico"""
    print("🔍 DIAGNÓSTICO DE PRODUÇÃO - Symplifika")
    print("="*60)
    print("Este script identifica problemas que podem causar erros 500\n")

    try:
        # Executar correções automáticas primeiro
        fix_common_issues()

        # Gerar relatório
        success = generate_summary_report()

        return success

    except KeyboardInterrupt:
        print("\n⚠️  Diagnóstico interrompido pelo usuário")
        return False
    except Exception as e:
        print(f"\n❌ Erro inesperado no diagnóstico: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Erro fatal: {e}")
        sys.exit(1)
