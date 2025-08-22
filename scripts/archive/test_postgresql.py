#!/usr/bin/env python3
"""
Script para testar a configuração do PostgreSQL
Este script verifica se a conexão com PostgreSQL está funcionando corretamente
"""

import os
import sys
import django
from django.db import connection
from django.core.management import execute_from_command_line

def setup_django():
    """Configura Django para uso standalone"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'symplifika.settings')
    django.setup()

def test_database_connection():
    """Testa a conexão com o database"""
    print("🔍 Testando conexão com o database...")

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()

        if result and result[0] == 1:
            print("✅ Conexão com database estabelecida com sucesso!")
            return True
        else:
            print("❌ Problema na resposta do database")
            return False

    except Exception as e:
        print(f"❌ Erro na conexão com database: {e}")
        return False

def get_database_info():
    """Obtém informações sobre o database configurado"""
    from django.conf import settings

    db_config = settings.DATABASES['default']

    print("📊 Informações do Database:")
    print(f"   Engine: {db_config['ENGINE']}")

    if 'postgresql' in db_config['ENGINE']:
        print(f"   Host: {db_config.get('HOST', 'localhost')}")
        print(f"   Port: {db_config.get('PORT', '5432')}")
        print(f"   Database: {db_config.get('NAME', 'N/A')}")
        print(f"   User: {db_config.get('USER', 'N/A')}")
        print("   Password: [HIDDEN]")
    else:
        print(f"   Path: {db_config.get('NAME', 'N/A')}")

def test_database_tables():
    """Testa se as tabelas Django existem"""
    print("🗂️  Verificando tabelas do Django...")

    try:
        from django.contrib.auth.models import User

        # Tenta fazer uma query simples
        user_count = User.objects.count()
        print(f"✅ Tabelas encontradas! Usuários cadastrados: {user_count}")
        return True

    except Exception as e:
        print(f"⚠️  Problema com tabelas Django: {e}")
        print("   Talvez seja necessário executar: python manage.py migrate")
        return False

def test_write_operation():
    """Testa operação de escrita no database"""
    print("✍️  Testando operação de escrita...")

    try:
        from django.contrib.auth.models import User

        # Tenta criar um usuário de teste
        test_user, created = User.objects.get_or_create(
            username='test_postgresql',
            defaults={
                'email': 'test@postgresql.com',
                'first_name': 'Test',
                'last_name': 'PostgreSQL'
            }
        )

        if created:
            print("✅ Usuário de teste criado com sucesso!")
            # Remove o usuário de teste
            test_user.delete()
            print("🗑️  Usuário de teste removido")
        else:
            print("✅ Operação de escrita funcionando (usuário já existia)")

        return True

    except Exception as e:
        print(f"❌ Erro na operação de escrita: {e}")
        return False

def test_app_models():
    """Testa os models específicos do app"""
    print("📱 Testando models do app...")

    try:
        # Testa models do app shortcuts
        from shortcuts.models import Shortcut, Category

        shortcut_count = Shortcut.objects.count()
        category_count = Category.objects.count()

        print(f"✅ Model Shortcut: {shortcut_count} registros")
        print(f"✅ Model Category: {category_count} registros")

        return True

    except Exception as e:
        print(f"⚠️  Problema com models do app: {e}")
        return False

def run_performance_test():
    """Executa teste simples de performance"""
    print("⚡ Executando teste de performance...")

    import time
    from django.contrib.auth.models import User

    try:
        start_time = time.time()

        # Query simples
        users = list(User.objects.all()[:10])

        end_time = time.time()
        duration = (end_time - start_time) * 1000  # em milissegundos

        print(f"✅ Query executada em {duration:.2f}ms")

        if duration < 100:
            print("🚀 Performance excelente!")
        elif duration < 500:
            print("👍 Performance boa")
        else:
            print("⚠️  Performance pode ser melhorada")

        return True

    except Exception as e:
        print(f"❌ Erro no teste de performance: {e}")
        return False

def check_migrations():
    """Verifica status das migrações"""
    print("🔄 Verificando status das migrações...")

    try:
        from django.core.management import call_command
        from io import StringIO

        # Captura output do comando showmigrations
        out = StringIO()
        call_command('showmigrations', stdout=out)
        migrations_output = out.getvalue()

        # Verifica se há migrações não aplicadas
        if '[ ]' in migrations_output:
            print("⚠️  Há migrações pendentes:")
            print(migrations_output)
            return False
        else:
            print("✅ Todas as migrações estão aplicadas")
            return True

    except Exception as e:
        print(f"❌ Erro ao verificar migrações: {e}")
        return False

def main():
    """Função principal"""
    print("🐘 Teste de Configuração PostgreSQL")
    print("=" * 50)

    # Configurar Django
    try:
        setup_django()
        print("✅ Django configurado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao configurar Django: {e}")
        sys.exit(1)

    # Lista de testes
    tests = [
        ("Informações do Database", get_database_info),
        ("Conexão com Database", test_database_connection),
        ("Status das Migrações", check_migrations),
        ("Tabelas do Django", test_database_tables),
        ("Operação de Escrita", test_write_operation),
        ("Models do App", test_app_models),
        ("Teste de Performance", run_performance_test),
    ]

    results = []

    # Executar testes
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)

        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro inesperado em {test_name}: {e}")
            results.append((test_name, False))

    # Resumo dos resultados
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status} - {test_name}")
        if result:
            passed += 1

    print(f"\n📈 Resultado: {passed}/{total} testes passaram")

    if passed == total:
        print("🎉 Todos os testes passaram! PostgreSQL está configurado corretamente.")
        return True
    else:
        print("⚠️  Alguns testes falharam. Verifique a configuração.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)
