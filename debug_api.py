#!/usr/bin/env python3
"""
Script para debugar problemas da API do Symplifika Django
"""
import os
import sys
import json

# Configurar Django ANTES de importar qualquer coisa do Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'symplifika.settings')

import django
try:
    django.setup()
except Exception as e:
    print(f"❌ Erro ao configurar Django: {e}")
    sys.exit(1)

# Agora podemos importar do Django
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from shortcuts.models import Category, Shortcut
from users.models import UserProfile


def create_test_user():
    """Cria um usuário de teste"""
    try:
        # Remove usuário existente se houver
        User.objects.filter(username='testuser').delete()

        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        print(f"✅ Usuário de teste criado: {user.username}")
        print(f"✅ Profile criado: {user.profile.plan}")
        return user
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        return None


def test_authentication():
    """Testa autenticação"""
    print("\n📋 Testando Autenticação...")

    client = Client()

    # Login
    response = client.login(username='testuser', password='testpass123')
    print(f"Login successful: {response}")

    return client


def test_categories_api(client):
    """Testa a API de categorias"""
    print("\n📋 Testando API de Categorias...")

    # Test GET /shortcuts/api/categories/
    print("\n1. GET /shortcuts/api/categories/")
    response = client.get('/shortcuts/api/categories/')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    else:
        print(f"Error: {response.content.decode()}")

    # Test POST /shortcuts/api/categories/
    print("\n2. POST /shortcuts/api/categories/")

    # Teste com dados válidos
    valid_data = {
        'name': 'Categoria Teste',
        'description': 'Descrição da categoria teste',
        'color': '#ff5500'
    }

    response = client.post(
        '/shortcuts/api/categories/',
        data=json.dumps(valid_data),
        content_type='application/json'
    )
    print(f"Status (dados válidos): {response.status_code}")
    if response.status_code in [200, 201]:
        data = response.json()
        print(f"Success Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        category_id = data.get('id')
    else:
        print(f"Error Response: {response.content.decode()}")
        category_id = None

    # Teste com dados inválidos
    print("\n3. POST com dados inválidos")
    invalid_data = {
        'name': '',  # Nome vazio
        'color': 'invalid-color'  # Cor inválida
    }

    response = client.post(
        '/shortcuts/api/categories/',
        data=json.dumps(invalid_data),
        content_type='application/json'
    )
    print(f"Status (dados inválidos): {response.status_code}")
    print(f"Error Response: {response.content.decode()}")

    # Teste sem dados
    print("\n4. POST sem dados")
    response = client.post(
        '/shortcuts/api/categories/',
        data='{}',
        content_type='application/json'
    )
    print(f"Status (sem dados): {response.status_code}")
    print(f"Error Response: {response.content.decode()}")

    return category_id


def test_shortcuts_api(client, category_id=None):
    """Testa a API de atalhos"""
    print("\n📋 Testando API de Atalhos...")

    # Test GET /shortcuts/api/shortcuts/
    print("\n1. GET /shortcuts/api/shortcuts/")
    response = client.get('/shortcuts/api/shortcuts/')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    else:
        print(f"Error: {response.content.decode()}")

    # Test POST /shortcuts/api/shortcuts/
    print("\n2. POST /shortcuts/api/shortcuts/")

    valid_shortcut_data = {
        'trigger': '//test-shortcut',
        'title': 'Atalho de Teste',
        'content': 'Conteúdo do atalho de teste',
        'expansion_type': 'static',
        'category': category_id
    }

    response = client.post(
        '/shortcuts/api/shortcuts/',
        data=json.dumps(valid_shortcut_data),
        content_type='application/json'
    )
    print(f"Status: {response.status_code}")
    if response.status_code in [200, 201]:
        data = response.json()
        print(f"Success Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    else:
        print(f"Error Response: {response.content.decode()}")


def check_database_state():
    """Verifica o estado atual do banco de dados"""
    print("\n📋 Verificando Estado do Banco...")

    # Usuários
    user_count = User.objects.count()
    print(f"Total de usuários: {user_count}")

    # Profiles
    profile_count = UserProfile.objects.count()
    print(f"Total de profiles: {profile_count}")

    # Categorias
    category_count = Category.objects.count()
    print(f"Total de categorias: {category_count}")

    # Atalhos
    shortcut_count = Shortcut.objects.count()
    print(f"Total de atalhos: {shortcut_count}")

    # Usuário de teste
    test_user = User.objects.filter(username='testuser').first()
    if test_user:
        print(f"\n👤 Usuário de teste:")
        print(f"  - Username: {test_user.username}")
        print(f"  - Email: {test_user.email}")
        print(f"  - Profile plan: {test_user.profile.plan}")
        print(f"  - Max shortcuts: {test_user.profile.max_shortcuts}")
        print(f"  - Categorias: {test_user.categories.count()}")
        print(f"  - Atalhos: {test_user.shortcuts.count()}")


def test_pagination_warning():
    """Reproduz o warning de paginação"""
    print("\n📋 Testando Warning de Paginação...")

    # Criar usuário de teste
    user = User.objects.filter(username='testuser').first()
    if not user:
        print("❌ Usuário de teste não encontrado")
        return

    # Criar algumas categorias para testar paginação
    print("Criando categorias para teste...")
    for i in range(5):
        Category.objects.get_or_create(
            user=user,
            name=f'Categoria {i+1}',
            defaults={
                'description': f'Descrição da categoria {i+1}',
                'color': f'#00{i}{i}00'
            }
        )

    # Fazer requisição que pode gerar o warning
    client = Client()
    client.login(username='testuser', password='testpass123')

    print("Fazendo requisição GET para categorias...")
    response = client.get('/shortcuts/api/categories/')
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Categorias retornadas: {data.get('count', len(data))}")


def run_all_tests():
    """Executa todos os testes"""
    print("🚀 Iniciando Testes de Debug da API Symplifika")
    print("=" * 50)

    # 1. Verificar estado inicial
    check_database_state()

    # 2. Criar usuário de teste
    user = create_test_user()
    if not user:
        print("❌ Falha ao criar usuário de teste. Abortando...")
        return

    # 3. Testar autenticação
    client = test_authentication()
    if not client:
        print("❌ Falha na autenticação. Abortando...")
        return

    # 4. Testar API de categorias
    category_id = test_categories_api(client)

    # 5. Testar API de atalhos
    test_shortcuts_api(client, category_id)

    # 6. Testar warning de paginação
    test_pagination_warning()

    # 7. Estado final
    print("\n📋 Estado Final do Banco:")
    check_database_state()

    print("\n✅ Testes concluídos!")


if __name__ == '__main__':
    run_all_tests()
