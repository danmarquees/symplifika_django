#!/usr/bin/env python3
"""
Test script para simular o comportamento de múltiplas submissões do frontend
e verificar se as correções estão funcionando.
Execute: python test_multiple_submissions.py
"""

import os
import sys
import django
import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'symplifika.settings')
django.setup()

import json
from django.contrib.auth.models import User
from django.test import Client
from shortcuts.models import Category

def create_category_request(client, category_data, request_id):
    """Simula uma requisição de criação de categoria"""
    print(f"🔄 Requisição {request_id}: Iniciando...")

    start_time = time.time()

    response = client.post(
        '/shortcuts/api/categories/',
        data=json.dumps(category_data),
        content_type='application/json',
        HTTP_X_CSRFTOKEN=client.session.get('csrftoken', '')
    )

    end_time = time.time()
    duration = end_time - start_time

    print(f"📊 Requisição {request_id}: Status {response.status_code} em {duration:.3f}s")

    if response.status_code == 201:
        created_category = response.json()
        print(f"✅ Requisição {request_id}: Categoria criada - ID {created_category['id']}")
        return {
            'success': True,
            'status': response.status_code,
            'data': created_category,
            'duration': duration,
            'request_id': request_id
        }
    else:
        try:
            error_data = response.json()
        except:
            error_data = response.content.decode()

        print(f"❌ Requisição {request_id}: Falhou - {error_data}")
        return {
            'success': False,
            'status': response.status_code,
            'error': error_data,
            'duration': duration,
            'request_id': request_id
        }

def test_simultaneous_submissions():
    """Testa múltiplas submissões simultâneas"""
    print("🧪 Testando submissões simultâneas de categoria...")

    # Criar usuário de teste
    user, created = User.objects.get_or_create(
        username='test_multiple_user',
        defaults={
            'email': 'test_multiple@example.com',
            'first_name': 'Test',
            'last_name': 'Multiple'
        }
    )

    if created:
        user.set_password('testpass123')
        user.save()

    # Limpar categorias existentes
    Category.objects.filter(user=user, name__startswith='Teste Simultâneo').delete()

    # Cliente de teste
    client = Client()
    client.force_login(user)

    # Dados da categoria que será criada múltiplas vezes
    category_data = {
        'name': 'Teste Simultâneo',
        'description': 'Categoria para testar submissões simultâneas',
        'color': '#ff6b35'
    }

    print(f"📝 Dados da categoria: {category_data}")
    print("🚀 Iniciando 3 requisições simultâneas...")

    # Executar múltiplas requisições simultâneas
    results = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []

        for i in range(3):
            future = executor.submit(create_category_request, client, category_data, i+1)
            futures.append(future)

        # Coletar resultados
        for future in futures:
            result = future.result()
            results.append(result)

    print("\n📊 Resultados das requisições simultâneas:")

    successful_requests = [r for r in results if r['success']]
    failed_requests = [r for r in results if not r['success']]

    print(f"✅ Requisições bem-sucedidas: {len(successful_requests)}")
    print(f"❌ Requisições com erro: {len(failed_requests)}")

    # Verificar se apenas uma categoria foi criada
    categories_created = Category.objects.filter(user=user, name='Teste Simultâneo').count()
    print(f"📦 Categorias realmente criadas no banco: {categories_created}")

    # Analisar os erros
    if failed_requests:
        print("\n🔍 Análise dos erros:")
        for req in failed_requests:
            print(f"   Requisição {req['request_id']}: Status {req['status']}")
            if isinstance(req['error'], dict) and 'name' in req['error']:
                print(f"   → Erro de validação: {req['error']['name']}")
            else:
                print(f"   → Erro: {req['error']}")

    # Verificar se o comportamento está correto
    expected_behavior = len(successful_requests) == 1 and len(failed_requests) == 2

    if expected_behavior:
        print("\n🎉 Comportamento CORRETO!")
        print("   ✓ Apenas uma requisição foi bem-sucedida")
        print("   ✓ As outras duas foram rejeitadas por nome duplicado")
        print("   ✓ Apenas uma categoria foi criada no banco de dados")
    else:
        print("\n⚠️ Comportamento INESPERADO!")
        print(f"   Esperado: 1 sucesso, 2 falhas")
        print(f"   Atual: {len(successful_requests)} sucessos, {len(failed_requests)} falhas")

        if categories_created > 1:
            print(f"   ❌ PROBLEMA: {categories_created} categorias foram criadas (esperado: 1)")

    # Limpeza
    Category.objects.filter(user=user, name='Teste Simultâneo').delete()

    return expected_behavior

def test_rapid_sequential_submissions():
    """Testa submissões sequenciais rápidas"""
    print("\n🧪 Testando submissões sequenciais rápidas...")

    # Criar usuário de teste
    user = User.objects.get_or_create(username='test_sequential_user')[0]

    # Limpar categorias existentes
    Category.objects.filter(user=user, name__startswith='Teste Sequencial').delete()

    client = Client()
    client.force_login(user)

    category_data = {
        'name': 'Teste Sequencial',
        'description': 'Categoria para testar submissões sequenciais',
        'color': '#35a7ff'
    }

    print("🚀 Fazendo 3 requisições sequenciais rápidas...")

    results = []
    for i in range(3):
        print(f"📤 Enviando requisição {i+1}...")
        result = create_category_request(client, category_data, i+1)
        results.append(result)
        time.sleep(0.1)  # Pequeno delay para simular cliques rápidos

    print("\n📊 Resultados das requisições sequenciais:")

    successful_requests = [r for r in results if r['success']]
    failed_requests = [r for r in results if not r['success']]

    print(f"✅ Requisições bem-sucedidas: {len(successful_requests)}")
    print(f"❌ Requisições com erro: {len(failed_requests)}")

    categories_created = Category.objects.filter(user=user, name='Teste Sequencial').count()
    print(f"📦 Categorias criadas no banco: {categories_created}")

    expected_behavior = len(successful_requests) == 1 and categories_created == 1

    if expected_behavior:
        print("🎉 Comportamento sequencial CORRETO!")
    else:
        print("⚠️ Comportamento sequencial INESPERADO!")

    # Limpeza
    Category.objects.filter(user=user, name='Teste Sequencial').delete()

    return expected_behavior

def test_different_names_simultaneous():
    """Testa submissões simultâneas com nomes diferentes (deve funcionar)"""
    print("\n🧪 Testando submissões simultâneas com nomes diferentes...")

    user = User.objects.get_or_create(username='test_different_names')[0]

    # Limpar categorias existentes
    Category.objects.filter(user=user, name__startswith='Teste Diferente').delete()

    client = Client()
    client.force_login(user)

    # Dados diferentes para cada requisição
    categories_data = [
        {
            'name': 'Teste Diferente 1',
            'description': 'Primeira categoria',
            'color': '#ff0000'
        },
        {
            'name': 'Teste Diferente 2',
            'description': 'Segunda categoria',
            'color': '#00ff00'
        },
        {
            'name': 'Teste Diferente 3',
            'description': 'Terceira categoria',
            'color': '#0000ff'
        }
    ]

    print("🚀 Criando 3 categorias com nomes diferentes simultaneamente...")

    results = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []

        for i, data in enumerate(categories_data):
            future = executor.submit(create_category_request, client, data, i+1)
            futures.append(future)

        for future in futures:
            result = future.result()
            results.append(result)

    successful_requests = [r for r in results if r['success']]
    failed_requests = [r for r in results if not r['success']]

    categories_created = Category.objects.filter(user=user, name__startswith='Teste Diferente').count()

    print(f"✅ Requisições bem-sucedidas: {len(successful_requests)}")
    print(f"❌ Requisições com erro: {len(failed_requests)}")
    print(f"📦 Categorias criadas no banco: {categories_created}")

    expected_behavior = len(successful_requests) == 3 and categories_created == 3

    if expected_behavior:
        print("🎉 Criação simultânea com nomes diferentes FUNCIONOU!")
    else:
        print("⚠️ Problema na criação simultânea com nomes diferentes!")

    # Limpeza
    Category.objects.filter(user=user, name__startswith='Teste Diferente').delete()

    return expected_behavior

def main():
    print("🚀 Iniciando testes de múltiplas submissões...\n")

    try:
        # Executar todos os testes
        test1_ok = test_simultaneous_submissions()
        test2_ok = test_rapid_sequential_submissions()
        test3_ok = test_different_names_simultaneous()

        print("\n" + "="*60)
        print("📋 RESUMO DOS TESTES:")
        print("="*60)
        print(f"✅ Submissões simultâneas (mesmo nome): {'PASSOU' if test1_ok else 'FALHOU'}")
        print(f"✅ Submissões sequenciais rápidas: {'PASSOU' if test2_ok else 'FALHOU'}")
        print(f"✅ Submissões simultâneas (nomes diferentes): {'PASSOU' if test3_ok else 'FALHOU'}")

        all_tests_ok = test1_ok and test2_ok and test3_ok

        if all_tests_ok:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            print("✅ O sistema está corretamente prevenindo submissões duplicadas")
            sys.exit(0)
        else:
            print("\n❌ ALGUNS TESTES FALHARAM!")
            print("⚠️  Pode haver problemas com submissões múltiplas")
            sys.exit(1)

    except Exception as e:
        print(f"\n💥 Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
