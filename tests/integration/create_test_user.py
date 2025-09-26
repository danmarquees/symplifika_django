#!/usr/bin/env python
"""
Script para criar usuário de teste para a extensão Chrome
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'symplifika.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile
from shortcuts.models import Category, Shortcut

def create_test_user():
    """Criar usuário de teste com alguns atalhos"""
    print("🔧 Criando usuário de teste...")
    
    # Criar usuário
    user, created = User.objects.get_or_create(
        username='test',
        defaults={
            'email': 'test@symplifika.com',
            'first_name': 'Usuário',
            'last_name': 'Teste',
            'is_active': True
        }
    )
    
    if created:
        user.set_password('test123')
        user.save()
        print("✅ Usuário 'test' criado com senha 'test123'")
    else:
        # Atualizar senha se usuário já existe
        user.set_password('test123')
        user.save()
        print("✅ Usuário 'test' já existe - senha atualizada para 'test123'")
    
    # Criar perfil
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'theme': 'light',
            'email_notifications': True,
            'ai_enabled': True,
            'plan': 'free'
        }
    )
    
    if created:
        print("✅ Perfil criado para usuário test")
    else:
        print("✅ Perfil já existe para usuário test")
    
    # Criar categoria de teste
    category, created = Category.objects.get_or_create(
        name='Teste',
        user=user,
        defaults={
            'description': 'Categoria de teste para extensão',
            'color': '#10b981'
        }
    )
    
    if created:
        print("✅ Categoria 'Teste' criada")
    else:
        print("✅ Categoria 'Teste' já existe")
    
    # Criar alguns atalhos de teste
    test_shortcuts = [
        {
            'title': 'Saudação',
            'trigger': '!oi',
            'content': 'Olá! Como posso ajudá-lo hoje?',
            'description': 'Saudação amigável'
        },
        {
            'title': 'Email Profissional',
            'trigger': '!email',
            'content': 'Prezado(a),\n\nEspero que esteja bem.\n\nAtenciosamente,\n{{user.name}}',
            'description': 'Template de email profissional'
        },
        {
            'title': 'Assinatura',
            'trigger': '!ass',
            'content': 'Atenciosamente,\n{{user.name}}\n{{user.email}}\nSymplifika - Atalhos Inteligentes',
            'description': 'Assinatura padrão'
        }
    ]
    
    for shortcut_data in test_shortcuts:
        shortcut, created = Shortcut.objects.get_or_create(
            trigger=shortcut_data['trigger'],
            user=user,
            defaults={
                'title': shortcut_data['title'],
                'content': shortcut_data['content'],
                'description': shortcut_data['description'],
                'category': category,
                'is_active': True,
                'expansion_type': 'simple'
            }
        )
        
        if created:
            print(f"✅ Atalho '{shortcut_data['title']}' ({shortcut_data['trigger']}) criado")
        else:
            print(f"✅ Atalho '{shortcut_data['title']}' ({shortcut_data['trigger']}) já existe")
    
    print(f"\n📊 Resumo:")
    print(f"   Username: {user.username}")
    print(f"   Password: test123")
    print(f"   Email: {user.email}")
    print(f"   Atalhos: {Shortcut.objects.filter(user=user).count()}")
    print(f"   Categorias: {Category.objects.filter(user=user).count()}")
    
    return user

def test_api_endpoints():
    """Testar endpoints da API"""
    print("\n🧪 Testando endpoints da API...")
    
    import requests
    import json
    
    base_url = 'http://127.0.0.1:8000'
    
    try:
        # Teste de login
        login_data = {
            'login': 'test',
            'password': 'test123'
        }
        
        response = requests.post(
            f'{base_url}/api/token/',
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login API funcionando")
            print(f"   Token obtido: {token_data.get('access', 'N/A')[:20]}...")
            
            # Teste de atalhos
            headers = {
                'Authorization': f"Bearer {token_data['access']}",
                'Content-Type': 'application/json'
            }
            
            shortcuts_response = requests.get(
                f'{base_url}/shortcuts/api/shortcuts/',
                headers=headers
            )
            
            if shortcuts_response.status_code == 200:
                shortcuts_data = shortcuts_response.json()
                print("✅ API de atalhos funcionando")
                print(f"   Atalhos encontrados: {len(shortcuts_data.get('results', []))}")
            else:
                print(f"❌ Erro na API de atalhos: {shortcuts_response.status_code}")
                print(f"   Resposta: {shortcuts_response.text}")
                
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")

if __name__ == '__main__':
    try:
        user = create_test_user()
        test_api_endpoints()
        print("\n🎉 Configuração de teste concluída!")
        print("\n📋 Para testar a extensão:")
        print("   1. Carregue a extensão no Chrome (pasta dist/)")
        print("   2. Use as credenciais: test / test123")
        print("   3. Teste os atalhos: !oi, !email, !ass")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)
