#!/usr/bin/env python
"""
Script de teste específico para API de atalhos
Diagnostica problemas na API que podem estar causando erros 500
"""

import os
import sys
import django
from pathlib import Path

# Configurar o ambiente Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'symplifika.settings')

try:
    django.setup()
except Exception as e:
    print(f"❌ Erro ao configurar Django: {e}")
    sys.exit(1)

import json
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from shortcuts.models import Category, Shortcut


def create_test_user():
    """Cria um usuário de teste"""
    User = get_user_model()

    # Remove usuário existente se houver
    User.objects.filter(username='testuser').delete()

    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

    # Garantir que o profile existe
    if not hasattr(user, 'profile'):
        from users.models import UserProfile
        UserProfile.objects.create(user=user)

    return user


def create_test_data(user):
    """Cria dados de teste"""
    # Criar categoria
    category = Category.objects.create(
        name='Teste',
        user=user
    )

    # Criar alguns atalhos
    shortcuts = []
    for i in range(3):
        shortcut = Shortcut.objects.create(
            trigger=f'//teste{i}',
            title=f'Teste {i}',
            content=f'Conteúdo de teste {i}',
            category=category,
            user=user
        )
        shortcuts.append(shortcut)

    return category, shortcuts


def test_stats_endpoint():
    """Testa o endpoint de estatísticas"""
    print("🔍 Testando endpoint de estatísticas...")

    user = create_test_user()
    category, shortcuts = create_test_data(user)

    client = APIClient()
    client.force_authenticate(user=user)

    try:
        response = client.get('/shortcuts/api/shortcuts/stats/')

        print(f"  Status Code: {response.status_code}")

        if response.status_code == 200:
            print("  ✅ Stats endpoint funcionando")
            data = response.data
            print(f"  📊 Total de atalhos: {data.get('total_shortcuts', 0)}")
            print(f"  📊 Atalhos ativos: {data.get('active_shortcuts', 0)}")
            print(f"  📊 Total de usos: {data.get('total_uses', 0)}")
            return True
        else:
            print(f"  ❌ Stats endpoint falhou")
            print(f"  Response: {response.content.decode()}")
            return False

    except Exception as e:
        print(f"  ❌ Erro no stats endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_list_endpoint():
    """Testa o endpoint de listagem"""
    print("\n🔍 Testando endpoint de listagem...")

    user = create_test_user()
    category, shortcuts = create_test_data(user)

    client = APIClient()
    client.force_authenticate(user=user)

    try:
        response = client.get('/shortcuts/api/shortcuts/')

        print(f"  Status Code: {response.status_code}")

        if response.status_code == 200:
            print("  ✅ List endpoint funcionando")
            data = response.data

            if 'results' in data:
                print(f"  📝 Atalhos retornados: {len(data['results'])}")
            else:
                print(f"  📝 Atalhos retornados: {len(data)}")

            return True
        else:
            print(f"  ❌ List endpoint falhou")
            print(f"  Response: {response.content.decode()}")
            return False

    except Exception as e:
        print(f"  ❌ Erro no list endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_create_endpoint():
    """Testa o endpoint de criação"""
    print("\n🔍 Testando endpoint de criação...")

    user = create_test_user()
    category, _ = create_test_data(user)

    client = APIClient()
    client.force_authenticate(user=user)

    try:
        data = {
            'trigger': '//novo-teste',
            'title': 'Novo Teste',
            'content': 'Conteúdo do novo teste',
            'category': category.id,
            'expansion_type': 'static'
        }

        response = client.post('/shortcuts/api/shortcuts/', data, format='json')

        print(f"  Status Code: {response.status_code}")

        if response.status_code == 201:
            print("  ✅ Create endpoint funcionando")
            created_data = response.data
            print(f"  📝 Atalho criado: {created_data.get('trigger', 'N/A')}")
            return True
        else:
            print(f"  ❌ Create endpoint falhou")
            print(f"  Response: {response.content.decode()}")
            return False

    except Exception as e:
        print(f"  ❌ Erro no create endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_use_endpoint():
    """Testa o endpoint de uso de atalho"""
    print("\n🔍 Testando endpoint de uso...")

    user = create_test_user()
    category, shortcuts = create_test_data(user)

    client = APIClient()
    client.force_authenticate(user=user)

    try:
        shortcut = shortcuts[0]
        data = {
            'context': 'Teste de uso'
        }

        response = client.post(f'/shortcuts/api/shortcuts/{shortcut.id}/use/', data, format='json')

        print(f"  Status Code: {response.status_code}")

        if response.status_code == 200:
            print("  ✅ Use endpoint funcionando")
            use_data = response.data
            print(f"  📊 Contagem de uso: {use_data.get('use_count', 0)}")
            return True
        else:
            print(f"  ❌ Use endpoint falhou")
            print(f"  Response: {response.content.decode()}")
            return False

    except Exception as e:
        print(f"  ❌ Erro no use endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_search_endpoint():
    """Testa o endpoint de busca"""
    print("\n🔍 Testando endpoint de busca...")

    user = create_test_user()
    category, shortcuts = create_test_data(user)

    client = APIClient()
    client.force_authenticate(user=user)

    try:
        data = {
            'query': 'teste',
            'category': category.id,
            'is_active': True
        }

        response = client.post('/shortcuts/api/shortcuts/search/', data, format='json')

        print(f"  Status Code: {response.status_code}")

        if response.status_code == 200:
            print("  ✅ Search endpoint funcionando")
            search_data = response.data

            if 'results' in search_data:
                print(f"  🔍 Resultados encontrados: {len(search_data['results'])}")
            else:
                print(f"  🔍 Resultados encontrados: {len(search_data)}")

            return True
        else:
            print(f"  ❌ Search endpoint falhou")
            print(f"  Response: {response.content.decode()}")
            return False

    except Exception as e:
        print(f"  ❌ Erro no search endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_categories_api():
    """Testa a API de categorias"""
    print("\n🔍 Testando API de categorias...")

    user = create_test_user()
    category, _ = create_test_data(user)

    client = APIClient()
    client.force_authenticate(user=user)

    try:
        response = client.get('/shortcuts/api/categories/')

        print(f"  Status Code: {response.status_code}")

        if response.status_code == 200:
            print("  ✅ Categories endpoint funcionando")
            data = response.data

            if 'results' in data:
                print(f"  📁 Categorias retornadas: {len(data['results'])}")
            else:
                print(f"  📁 Categorias retornadas: {len(data)}")

            return True
        else:
            print(f"  ❌ Categories endpoint falhou")
            print(f"  Response: {response.content.decode()}")
            return False

    except Exception as e:
        print(f"  ❌ Erro no categories endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_with_unauthenticated_request():
    """Testa endpoints sem autenticação"""
    print("\n🔍 Testando endpoints sem autenticação...")

    client = APIClient()
    # NÃO autenticar o cliente

    try:
        response = client.get('/shortcuts/api/shortcuts/stats/')

        print(f"  Status Code: {response.status_code}")

        if response.status_code == 401:
            print("  ✅ Autenticação está sendo validada corretamente")
            return True
        elif response.status_code == 403:
            print("  ✅ Permissões estão sendo validadas corretamente")
            return True
        else:
            print(f"  ⚠️  Resposta inesperada para request não autenticado")
            print(f"  Response: {response.content.decode()}")
            return False

    except Exception as e:
        print(f"  ❌ Erro no teste sem autenticação: {e}")
        import traceback
        traceback.print_exc()
        return False


def cleanup_test_data():
    """Remove dados de teste"""
    try:
        User = get_user_model()
        User.objects.filter(username='testuser').delete()
        print("  🧹 Dados de teste removidos")
    except Exception as e:
        print(f"  ⚠️  Erro ao limpar dados de teste: {e}")


def run_all_tests():
    """Executa todos os testes"""
    print("🚀 TESTE COMPLETO DA API DE ATALHOS")
    print("="*50)

    tests = [
        ("Estatísticas", test_stats_endpoint),
        ("Listagem", test_list_endpoint),
        ("Criação", test_create_endpoint),
        ("Uso de atalho", test_use_endpoint),
        ("Busca", test_search_endpoint),
        ("Categorias", test_categories_api),
        ("Autenticação", test_with_unauthenticated_request),
    ]

    results = []

    try:
        for test_name, test_function in tests:
            print(f"\n{'='*30}")
            print(f"TESTE: {test_name}")
            print('='*30)

            result = test_function()
            results.append((test_name, result))

            if not result:
                print(f"⚠️  Teste '{test_name}' falhou")

    except KeyboardInterrupt:
        print("\n⚠️  Testes interrompidos pelo usuário")
        return False

    finally:
        cleanup_test_data()

    # Resumo
    print(f"\n{'='*50}")
    print("📊 RESUMO DOS TESTES")
    print('='*50)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status} - {test_name}")
        if result:
            passed += 1

    print(f"\nResultado final: {passed}/{total} testes passaram")

    if passed == total:
        print("\n🎉 Todos os testes da API passaram!")
        print("A API está funcionando corretamente.")
    elif passed >= total * 0.7:
        print("\n⚠️  A maioria dos testes passou.")
        print("Há alguns problemas menores que devem ser investigados.")
    else:
        print("\n❌ Muitos testes falharam.")
        print("Há problemas significativos na API que precisam ser corrigidos.")

    # Sugestões
    print(f"\n💡 PRÓXIMOS PASSOS:")

    if passed < total:
        print("1. Analise os erros detalhados acima")
        print("2. Verifique as configurações do Django REST Framework")
        print("3. Execute: python manage.py migrate")
        print("4. Verifique as permissões e autenticação")
        print("5. Teste novamente após correções")

    if any([name for name, result in results if not result and 'tão' in name.lower()]):
        print("6. Configure GEMINI_API_KEY se necessário")

    return passed == total


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Erro fatal nos testes: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
