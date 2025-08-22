#!/usr/bin/env python3
"""
Test script para verificar se a API de categorias está funcionando corretamente.
Execute: python test_category_api.py
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'symplifika.settings')
django.setup()

import requests
import json
from django.contrib.auth.models import User
from django.test import Client
from shortcuts.models import Category

def test_category_api():
    """Testa a API de categorias"""
    print("🧪 Testando API de categorias...")

    # Criar ou obter usuário de teste
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )

    if created:
        user.set_password('testpass123')
        user.save()
        print("✅ Usuário de teste criado")
    else:
        print("✅ Usuário de teste já existe")

    # Não é necessário token para Client, pois usamos force_login

    # Cliente de teste Django
    client = Client()
    client.force_login(user)

    # Teste 1: GET /shortcuts/api/categories/ (listar categorias)
    print("\n📋 Teste 1: Listar categorias")
    response = client.get('/shortcuts/api/categories/')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Categorias encontradas: {data.get('count', 0)}")
        print("✅ GET categories OK")
    else:
        print(f"❌ GET categories FALHOU: {response.content}")
        return False

    # Teste 2: POST /shortcuts/api/categories/ (criar categoria)
    print("\n📝 Teste 2: Criar categoria")

    # Limpar categorias existentes de teste
    Category.objects.filter(user=user, name__startswith='Teste').delete()

    category_data = {
        'name': 'Teste API',
        'description': 'Categoria criada via API de teste',
        'color': '#ff6b35'
    }

    response = client.post(
        '/shortcuts/api/categories/',
        data=json.dumps(category_data),
        content_type='application/json',
        HTTP_X_CSRFTOKEN=client.session.get('csrftoken', '')
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {response.content.decode()}")

    if response.status_code == 201:
        created_category = response.json()
        print(f"✅ Categoria criada: {created_category['name']}")
        category_id = created_category['id']

        # Teste 3: PUT /shortcuts/api/categories/{id}/ (atualizar categoria)
        print("\n✏️ Teste 3: Atualizar categoria")

        update_data = {
            'name': 'Teste API Atualizado',
            'description': 'Categoria atualizada via API de teste',
            'color': '#35a7ff'
        }

        response = client.put(
            f'/shortcuts/api/categories/{category_id}/',
            data=json.dumps(update_data),
            content_type='application/json',
            HTTP_X_CSRFTOKEN=client.session.get('csrftoken', '')
        )

        print(f"Status: {response.status_code}")
        print(f"Response: {response.content.decode()}")

        if response.status_code == 200:
            updated_category = response.json()
            print(f"✅ Categoria atualizada: {updated_category['name']}")
        else:
            print(f"❌ PUT category FALHOU")
            return False

        # Teste 4: DELETE /shortcuts/api/categories/{id}/ (deletar categoria)
        print("\n🗑️ Teste 4: Deletar categoria")

        response = client.delete(
            f'/shortcuts/api/categories/{category_id}/',
            HTTP_X_CSRFTOKEN=client.session.get('csrftoken', '')
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 204:
            print("✅ Categoria deletada com sucesso")
        else:
            print(f"❌ DELETE category FALHOU: {response.content}")
            return False

    else:
        print(f"❌ POST category FALHOU")
        print(f"Response content: {response.content.decode()}")

        # Tentar entender o erro
        try:
            error_data = response.json()
            print(f"Dados de erro: {json.dumps(error_data, indent=2)}")
        except:
            print("Não foi possível parsear resposta como JSON")

        return False

    # Teste 5: Validações (nome duplicado)
    print("\n🔍 Teste 5: Validação de nome duplicado")

    # Criar categoria
    Category.objects.create(user=user, name='Categoria Duplicada', color='#ff0000')

    # Tentar criar outra com mesmo nome
    duplicate_data = {
        'name': 'Categoria Duplicada',
        'description': 'Esta deveria falhar',
        'color': '#00ff00'
    }

    response = client.post(
        '/shortcuts/api/categories/',
        data=json.dumps(duplicate_data),
        content_type='application/json',
        HTTP_X_CSRFTOKEN=client.session.get('csrftoken', '')
    )

    print(f"Status: {response.status_code}")

    if response.status_code == 400:
        error_data = response.json()
        print(f"✅ Validação funcionando: {error_data}")
    else:
        print(f"❌ Validação de duplicata FALHOU")
        return False

    # Limpeza
    Category.objects.filter(user=user, name__startswith='Categoria').delete()

    print("\n🎉 Todos os testes passaram!")
    return True

def test_csrf_token():
    """Testa se o CSRF token está sendo obtido corretamente"""
    print("\n🔒 Testando CSRF Token...")

    client = Client()

    # Fazer uma requisição GET para obter o CSRF token
    response = client.get('/shortcuts/api/categories/')
    csrf_token = client.cookies.get('csrftoken')

    if csrf_token:
        print(f"✅ CSRF Token obtido: {csrf_token.value[:10]}...")
    else:
        print("⚠️ CSRF Token não encontrado nos cookies")

    # Verificar se há token no contexto da sessão
    session_csrf = client.session.get('csrftoken')
    if session_csrf:
        print(f"✅ CSRF Token na sessão: {session_csrf[:10]}...")
    else:
        print("⚠️ CSRF Token não encontrado na sessão")

def debug_category_serializer():
    """Debug do serializer de categoria"""
    print("\n🔧 Debug do CategorySerializer...")

    from shortcuts.serializers import CategorySerializer
    from django.contrib.auth.models import User

    # Criar usuário de teste
    user = User.objects.get_or_create(username='test_debug')[0]

    # Dados de teste
    test_data = {
        'name': 'Debug Category',
        'description': 'Categoria para debug',
        'color': '#123456'
    }

    # Criar contexto de request mock
    class MockRequest:
        def __init__(self, user):
            self.user = user

    context = {'request': MockRequest(user)}

    # Testar serializer
    serializer = CategorySerializer(data=test_data, context=context)

    print(f"Dados de entrada: {test_data}")
    print(f"Serializer válido: {serializer.is_valid()}")

    if not serializer.is_valid():
        print(f"Erros de validação: {serializer.errors}")
    else:
        print("✅ Serializer validou com sucesso")

        # Tentar salvar
        try:
            category = serializer.save()
            print(f"✅ Categoria salva: {category}")
            category.delete()  # Limpar
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")

if __name__ == '__main__':
    print("🚀 Iniciando testes da API de categorias...\n")

    try:
        # Executar testes
        test_csrf_token()
        debug_category_serializer()
        success = test_category_api()

        if success:
            print("\n✅ Todos os testes concluídos com sucesso!")
            sys.exit(0)
        else:
            print("\n❌ Alguns testes falharam!")
            sys.exit(1)

    except Exception as e:
        print(f"\n💥 Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
