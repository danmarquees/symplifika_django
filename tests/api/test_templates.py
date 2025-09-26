#!/usr/bin/env python
"""
Script para testar as views e templates criados
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'symplifika.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from users.models import UserProfile

def test_templates():
    """Testa se todas as views e templates estão funcionando"""
    client = Client()
    
    # Criar usuário de teste
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    
    # Criar perfil do usuário
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    print("🧪 Testando templates e views...")
    
    # Testes de páginas públicas
    public_pages = [
        ('core:index', 'Página inicial'),
        ('core:help', 'Central de ajuda'),
        ('core:privacy', 'Política de privacidade'),
        ('core:terms', 'Termos de serviço'),
        ('core:pricing', 'Preços'),
    ]
    
    for url_name, description in public_pages:
        try:
            url = reverse(url_name)
            response = client.get(url)
            status = "✅" if response.status_code == 200 else f"❌ ({response.status_code})"
            print(f"{status} {description}: {url}")
        except Exception as e:
            print(f"❌ {description}: Erro - {e}")
    
    # Login do usuário de teste
    client.login(username='testuser', password='testpass123')
    
    # Testes de páginas autenticadas
    auth_pages = [
        ('core:dashboard', 'Dashboard'),
        ('core:profile', 'Perfil do usuário'),
        ('core:settings', 'Configurações'),
        ('users:subscription', 'Gerenciar assinatura'),
        ('core:support', 'Suporte'),
        ('core:feedback', 'Feedback'),
        ('core:about', 'Sobre'),
        ('core:contact', 'Contato'),
    ]
    
    for url_name, description in auth_pages:
        try:
            url = reverse(url_name)
            response = client.get(url)
            status = "✅" if response.status_code == 200 else f"❌ ({response.status_code})"
            print(f"{status} {description}: {url}")
        except Exception as e:
            print(f"❌ {description}: Erro - {e}")
    
    # Testes de APIs
    api_endpoints = [
        ('core:api-status', 'API Status'),
        ('core:health-check', 'Health Check'),
        ('core:usage-stats-api', 'Estatísticas de uso'),
    ]
    
    for url_name, description in api_endpoints:
        try:
            url = reverse(url_name)
            response = client.get(url)
            status = "✅" if response.status_code == 200 else f"❌ ({response.status_code})"
            print(f"{status} {description}: {url}")
        except Exception as e:
            print(f"❌ {description}: Erro - {e}")
    
    # Teste de API com parâmetros
    try:
        url = reverse('core:user-activity-api', kwargs={'user_id': user.id})
        response = client.get(url)
        status = "✅" if response.status_code == 200 else f"❌ ({response.status_code})"
        print(f"{status} API de atividade do usuário: {url}")
    except Exception as e:
        print(f"❌ API de atividade do usuário: Erro - {e}")
    
    print("\n🎯 Resumo dos templates criados:")
    templates = [
        'templates/core/profile/profile.html - Perfil do usuário com estatísticas',
        'templates/users/subscription.html - Gerenciamento de assinatura',
        'templates/core/settings.html - Configurações do usuário',
        'templates/help.html - Central de ajuda (já existia)',
        'templates/privacy.html - Política de privacidade (já existia)',
        'templates/terms.html - Termos de serviço (já existia)'
    ]
    
    for template in templates:
        print(f"📄 {template}")
    
    print("\n🔗 URLs configuradas:")
    urls = [
        '/profile/ - Perfil do usuário logado',
        '/profile/<id>/ - Perfil de usuário específico',
        '/settings/ - Configurações',
        '/users/subscription/ - Gerenciar assinatura',
        '/help/ - Central de ajuda',
        '/privacy/ - Política de privacidade',
        '/terms/ - Termos de serviço'
    ]
    
    for url in urls:
        print(f"🌐 {url}")
    
    print("\n🚀 APIs criadas:")
    apis = [
        '/api/users/<id>/activity/ - Timeline de atividades',
        '/api/users/<id>/categories/ - Categorias favoritas',
        '/api/users/usage-stats/ - Estatísticas de uso',
        '/api/payments/billing-history/ - Histórico de faturamento'
    ]
    
    for api in apis:
        print(f"⚡ {api}")
    
    # Cleanup
    user.delete()
    
    print("\n✨ Teste concluído!")

if __name__ == '__main__':
    test_templates()
