#!/usr/bin/env python
"""
Script de teste para API do Symplifika
Execute: python test_api.py
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'symplifika.settings')
django.setup()

# Base URL da API
BASE_URL = 'http://localhost:8000'

class SymplifikaAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_data = None

    def print_header(self, title):
        print(f"\n{'=' * 60}")
        print(f"  {title}")
        print(f"{'=' * 60}")

    def print_result(self, method, endpoint, status_code, response_data=None):
        status_icon = "✅" if 200 <= status_code < 300 else "❌"
        print(f"{status_icon} {method} {endpoint} - Status: {status_code}")

        if response_data:
            if isinstance(response_data, dict):
                if 'error' in response_data or 'errors' in response_data:
                    print(f"   Error: {response_data}")
                elif 'message' in response_data:
                    print(f"   Message: {response_data['message']}")
                elif 'count' in response_data:
                    print(f"   Count: {response_data['count']}")
                else:
                    # Mostrar apenas alguns campos importantes
                    important_fields = ['id', 'username', 'trigger', 'title', 'name', 'token']
                    shown_data = {k: v for k, v in response_data.items() if k in important_fields}
                    if shown_data:
                        print(f"   Data: {shown_data}")
            elif isinstance(response_data, list) and response_data:
                print(f"   Items: {len(response_data)} items")
                if response_data and isinstance(response_data[0], dict):
                    first_item = response_data[0]
                    important_fields = ['id', 'trigger', 'title', 'name']
                    shown_data = {k: v for k, v in first_item.items() if k in important_fields}
                    print(f"   First item: {shown_data}")

    def test_authentication(self):
        self.print_header("TESTANDO AUTENTICAÇÃO")

        # 1. Teste de registro de usuário
        register_data = {
            "username": f"test_user_{datetime.now().strftime('%H%M%S')}",
            "email": f"test_{datetime.now().strftime('%H%M%S')}@test.com",
            "password": "testpassword123",
            "password_confirm": "testpassword123",
            "first_name": "Teste",
            "last_name": "Usuario"
        }

        response = self.session.post(f"{BASE_URL}/users/auth/register/", json=register_data)
        self.print_result("POST", "/users/auth/register/", response.status_code, response.json() if response.content else None)

        if response.status_code == 201:
            data = response.json()
            self.token = data.get('token')
            self.user_data = data.get('user')
            self.session.headers.update({'Authorization': f'Token {self.token}'})
            print(f"   🔑 Token obtido: {self.token[:20]}...")

        # 2. Teste de login com usuário demo
        if not self.token:
            login_data = {
                "username": "demo",
                "password": "demo123"
            }

            response = self.session.post(f"{BASE_URL}/users/auth/login/", json=login_data)
            self.print_result("POST", "/users/auth/login/", response.status_code, response.json() if response.content else None)

            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                self.user_data = data.get('user')
                self.session.headers.update({'Authorization': f'Token {self.token}'})
                print(f"   🔑 Token obtido: {self.token[:20]}...")

        # 3. Teste de dados do usuário
        if self.token:
            response = self.session.get(f"{BASE_URL}/users/api/users/me/")
            self.print_result("GET", "/users/api/users/me/", response.status_code, response.json() if response.content else None)

    def test_categories(self):
        self.print_header("TESTANDO CATEGORIAS")

        if not self.token:
            print("❌ Token não disponível. Execute teste de autenticação primeiro.")
            return

        # 1. Listar categorias
        response = self.session.get(f"{BASE_URL}/shortcuts/api/categories/")
        self.print_result("GET", "/shortcuts/api/categories/", response.status_code, response.json() if response.content else None)

        # 2. Criar nova categoria
        category_data = {
            "name": f"Teste {datetime.now().strftime('%H:%M:%S')}",
            "description": "Categoria criada pelo teste",
            "color": "#ff6b6b"
        }

        response = self.session.post(f"{BASE_URL}/shortcuts/api/categories/", json=category_data)
        self.print_result("POST", "/shortcuts/api/categories/", response.status_code, response.json() if response.content else None)

        created_category_id = None
        if response.status_code == 201:
            created_category_id = response.json().get('id')

        return created_category_id

    def test_shortcuts(self, category_id=None):
        self.print_header("TESTANDO ATALHOS")

        if not self.token:
            print("❌ Token não disponível. Execute teste de autenticação primeiro.")
            return

        # 1. Listar atalhos
        response = self.session.get(f"{BASE_URL}/shortcuts/api/shortcuts/")
        self.print_result("GET", "/shortcuts/api/shortcuts/", response.status_code, response.json() if response.content else None)

        # 2. Criar atalho estático
        shortcut_data = {
            "trigger": f"//teste-{datetime.now().strftime('%H%M%S')}",
            "title": "Atalho de Teste",
            "content": "Este é um atalho criado pelo teste automático.",
            "expansion_type": "static"
        }

        if category_id:
            shortcut_data["category"] = category_id

        response = self.session.post(f"{BASE_URL}/shortcuts/api/shortcuts/", json=shortcut_data)
        self.print_result("POST", "/shortcuts/api/shortcuts/", response.status_code, response.json() if response.content else None)

        created_shortcut_id = None
        if response.status_code == 201:
            created_shortcut_id = response.json().get('id')

        # 3. Criar atalho dinâmico
        dynamic_shortcut_data = {
            "trigger": f"//dinamico-{datetime.now().strftime('%H%M%S')}",
            "title": "Atalho Dinâmico de Teste",
            "content": "Olá {nome}, bem-vindo à {empresa}!",
            "expansion_type": "dynamic",
            "variables": {
                "nome": "Usuário",
                "empresa": "Symplifika"
            }
        }

        response = self.session.post(f"{BASE_URL}/shortcuts/api/shortcuts/", json=dynamic_shortcut_data)
        self.print_result("POST", "/shortcuts/api/shortcuts/", response.status_code, response.json() if response.content else None)

        # 4. Testar uso de atalho
        if created_shortcut_id:
            use_data = {
                "context": "teste_automatico"
            }
            response = self.session.post(f"{BASE_URL}/shortcuts/api/shortcuts/{created_shortcut_id}/use/", json=use_data)
            self.print_result("POST", f"/shortcuts/api/shortcuts/{created_shortcut_id}/use/", response.status_code, response.json() if response.content else None)

        # 5. Buscar atalhos
        search_data = {
            "query": "teste",
            "is_active": True
        }
        response = self.session.post(f"{BASE_URL}/shortcuts/api/shortcuts/search/", json=search_data)
        self.print_result("POST", "/shortcuts/api/shortcuts/search/", response.status_code, response.json() if response.content else None)

        return created_shortcut_id

    def test_statistics(self):
        self.print_header("TESTANDO ESTATÍSTICAS")

        if not self.token:
            print("❌ Token não disponível. Execute teste de autenticação primeiro.")
            return

        # 1. Estatísticas do usuário
        response = self.session.get(f"{BASE_URL}/users/api/users/stats/")
        self.print_result("GET", "/users/api/users/stats/", response.status_code, response.json() if response.content else None)

        # 2. Estatísticas dos atalhos
        response = self.session.get(f"{BASE_URL}/shortcuts/api/shortcuts/stats/")
        self.print_result("GET", "/shortcuts/api/shortcuts/stats/", response.status_code, response.json() if response.content else None)

        # 3. Dashboard
        response = self.session.get(f"{BASE_URL}/users/dashboard/")
        self.print_result("GET", "/users/dashboard/", response.status_code, response.json() if response.content else None)

        # 4. Atalhos mais usados
        response = self.session.get(f"{BASE_URL}/shortcuts/api/shortcuts/most-used/?days=30")
        self.print_result("GET", "/shortcuts/api/shortcuts/most-used/", response.status_code, response.json() if response.content else None)

    def test_profile_management(self):
        self.print_header("TESTANDO GERENCIAMENTO DE PERFIL")

        if not self.token:
            print("❌ Token não disponível. Execute teste de autenticação primeiro.")
            return

        # 1. Obter perfil
        response = self.session.get(f"{BASE_URL}/users/api/profile/")
        self.print_result("GET", "/users/api/profile/", response.status_code, response.json() if response.content else None)

        # 2. Atualizar configurações do perfil
        profile_data = {
            "theme": "dark",
            "email_notifications": False
        }
        response = self.session.patch(f"{BASE_URL}/users/api/profile/1/", json=profile_data)
        self.print_result("PATCH", "/users/api/profile/1/", response.status_code, response.json() if response.content else None)

    def test_api_endpoints(self):
        self.print_header("TESTANDO ENDPOINTS GERAIS")

        # 1. API Root
        response = self.session.get(f"{BASE_URL}/api/")
        self.print_result("GET", "/api/", response.status_code, response.json() if response.content else None)

        # 2. Admin (sem autenticação)
        response = self.session.get(f"{BASE_URL}/admin/")
        self.print_result("GET", "/admin/", response.status_code, None)

    def run_all_tests(self):
        print("🧪 INICIANDO TESTES DA API SYMPLIFIKA")
        print(f"📍 Base URL: {BASE_URL}")
        print(f"⏰ Timestamp: {datetime.now()}")

        try:
            # Executar todos os testes
            self.test_api_endpoints()
            self.test_authentication()
            category_id = self.test_categories()
            shortcut_id = self.test_shortcuts(category_id)
            self.test_statistics()
            self.test_profile_management()

            # Resumo final
            self.print_header("RESUMO DOS TESTES")
            print("✅ Testes de API executados com sucesso!")
            print(f"🔑 Token: {'✅ Obtido' if self.token else '❌ Não obtido'}")
            print(f"👤 Usuário: {self.user_data.get('username') if self.user_data else 'N/A'}")
            print(f"📝 Categoria criada: {'✅ Sim' if category_id else '❌ Não'}")
            print(f"⚡ Atalho criado: {'✅ Sim' if shortcut_id else '❌ Não'}")

            print(f"\n🌐 URLs úteis:")
            print(f"   Admin: {BASE_URL}/admin/")
            print(f"   API Root: {BASE_URL}/api/")
            print(f"   Documentação: {BASE_URL}/api/docs/ (se disponível)")

        except Exception as e:
            print(f"\n❌ ERRO durante os testes: {e}")
            import traceback
            traceback.print_exc()


def main():
    # Verificar se o servidor está rodando
    try:
        response = requests.get(f"{BASE_URL}/api/", timeout=5)
    except requests.exceptions.ConnectionError:
        print(f"❌ Erro: Servidor não está rodando em {BASE_URL}")
        print("   Execute: python manage.py runserver")
        return
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return

    # Executar testes
    tester = SymplifikaAPITester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
