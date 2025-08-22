#!/usr/bin/env python3
"""
Script de teste da integração Django-Frontend para Symplifika
Este script testa se todas as funcionalidades estão funcionando corretamente.
"""

import os
import sys
import django
import requests
import json
from time import sleep

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'symplifika.settings')
django.setup()

from django.contrib.auth.models import User
from shortcuts.models import Category, Shortcut
from users.models import UserProfile

class SymplifikaIntegrationTest:
    def __init__(self):
        self.base_url = 'http://127.0.0.1:8000'
        self.token = None
        self.user_id = None
        self.test_results = []

    def log(self, message, status="INFO"):
        """Log de mensagens com status"""
        print(f"[{status}] {message}")
        self.test_results.append({"message": message, "status": status})

    def test_server_running(self):
        """Testa se o servidor Django está rodando"""
        try:
            response = requests.get(self.base_url, timeout=5)
            if response.status_code == 200:
                self.log("✅ Servidor Django está rodando", "PASS")
                return True
            else:
                self.log(f"❌ Servidor retornou status {response.status_code}", "FAIL")
                return False
        except requests.exceptions.ConnectionError:
            self.log("❌ Não foi possível conectar ao servidor Django", "FAIL")
            return False
        except Exception as e:
            self.log(f"❌ Erro ao testar servidor: {e}", "FAIL")
            return False

    def test_frontend_template(self):
        """Testa se o template frontend está sendo servido"""
        try:
            response = requests.get(self.base_url)
            if 'symplifika' in response.text and 'app.js' in response.text:
                self.log("✅ Template frontend está sendo servido corretamente", "PASS")
                return True
            else:
                self.log("❌ Template frontend não está completo", "FAIL")
                return False
        except Exception as e:
            self.log(f"❌ Erro ao verificar template: {e}", "FAIL")
            return False

    def test_static_files(self):
        """Testa se os arquivos estáticos estão sendo servidos"""
        try:
            js_response = requests.get(f"{self.base_url}/static/js/app.js")
            if js_response.status_code == 200 and 'SymplifikaApp' in js_response.text:
                self.log("✅ Arquivo JavaScript está sendo servido", "PASS")
                return True
            else:
                self.log("❌ Arquivo JavaScript não encontrado ou inválido", "FAIL")
                return False
        except Exception as e:
            self.log(f"❌ Erro ao verificar arquivos estáticos: {e}", "FAIL")
            return False

    def test_user_creation(self):
        """Testa criação de usuário via API"""
        try:
            # Dados do usuário de teste
            user_data = {
                'username': 'test_integration',
                'email': 'test@symplifika.com',
                'password': 'testpass123',
                'first_name': 'Test',
                'last_name': 'User'
            }

            response = requests.post(
                f"{self.base_url}/users/auth/register/",
                json=user_data,
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 201:
                self.log("✅ Criação de usuário via API funcionando", "PASS")
                return True
            else:
                self.log(f"❌ Falha na criação de usuário: {response.status_code} - {response.text}", "FAIL")
                return False
        except Exception as e:
            self.log(f"❌ Erro ao testar criação de usuário: {e}", "FAIL")
            return False

    def test_user_login(self):
        """Testa login de usuário via API"""
        try:
            # Usar usuário demo existente
            login_data = {
                'username': 'demo',
                'password': 'demo123'
            }

            response = requests.post(
                f"{self.base_url}/users/auth/login/",
                json=login_data,
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 200:
                data = response.json()
                if 'token' in data:
                    self.token = data['token']
                    self.user_id = data.get('user', {}).get('id')
                    self.log("✅ Login via API funcionando", "PASS")
                    return True
                else:
                    self.log("❌ Token não retornado no login", "FAIL")
                    return False
            else:
                self.log(f"❌ Falha no login: {response.status_code} - {response.text}", "FAIL")
                return False
        except Exception as e:
            self.log(f"❌ Erro ao testar login: {e}", "FAIL")
            return False

    def test_authenticated_requests(self):
        """Testa requisições autenticadas"""
        if not self.token:
            self.log("❌ Token não disponível para testes autenticados", "FAIL")
            return False

        try:
            headers = {'Authorization': f'Token {self.token}'}

            # Testar endpoint de usuário
            response = requests.get(f"{self.base_url}/users/api/users/me/", headers=headers)
            if response.status_code == 200:
                self.log("✅ Requisições autenticadas funcionando", "PASS")
                return True
            else:
                self.log(f"❌ Falha em requisição autenticada: {response.status_code}", "FAIL")
                return False
        except Exception as e:
            self.log(f"❌ Erro ao testar requisições autenticadas: {e}", "FAIL")
            return False

    def test_shortcuts_api(self):
        """Testa API de atalhos"""
        if not self.token:
            self.log("❌ Token não disponível para testar API de atalhos", "FAIL")
            return False

        try:
            headers = {
                'Authorization': f'Token {self.token}',
                'Content-Type': 'application/json'
            }

            # Listar atalhos
            response = requests.get(f"{self.base_url}/shortcuts/api/shortcuts/", headers=headers)
            if response.status_code == 200:
                self.log("✅ API de listagem de atalhos funcionando", "PASS")

                # Criar atalho de teste
                shortcut_data = {
                    'trigger': '//test-integration',
                    'title': 'Teste de Integração',
                    'content': 'Este é um atalho de teste criado durante a integração.',
                    'expansion_type': 'static'
                }

                create_response = requests.post(
                    f"{self.base_url}/shortcuts/api/shortcuts/",
                    json=shortcut_data,
                    headers=headers
                )

                if create_response.status_code == 201:
                    self.log("✅ Criação de atalhos via API funcionando", "PASS")
                    return True
                else:
                    self.log(f"❌ Falha na criação de atalho: {create_response.status_code}", "FAIL")
                    return False
            else:
                self.log(f"❌ Falha na listagem de atalhos: {response.status_code}", "FAIL")
                return False
        except Exception as e:
            self.log(f"❌ Erro ao testar API de atalhos: {e}", "FAIL")
            return False

    def test_categories_api(self):
        """Testa API de categorias"""
        if not self.token:
            self.log("❌ Token não disponível para testar API de categorias", "FAIL")
            return False

        try:
            headers = {
                'Authorization': f'Token {self.token}',
                'Content-Type': 'application/json'
            }

            # Listar categorias
            response = requests.get(f"{self.base_url}/shortcuts/api/categories/", headers=headers)
            if response.status_code == 200:
                self.log("✅ API de categorias funcionando", "PASS")
                return True
            else:
                self.log(f"❌ Falha na API de categorias: {response.status_code}", "FAIL")
                return False
        except Exception as e:
            self.log(f"❌ Erro ao testar API de categorias: {e}", "FAIL")
            return False

    def test_admin_access(self):
        """Testa acesso ao admin Django"""
        try:
            response = requests.get(f"{self.base_url}/admin/")
            if response.status_code == 200 or response.status_code == 302:
                self.log("✅ Admin Django acessível", "PASS")
                return True
            else:
                self.log(f"❌ Admin Django não acessível: {response.status_code}", "FAIL")
                return False
        except Exception as e:
            self.log(f"❌ Erro ao testar admin: {e}", "FAIL")
            return False

    def test_database_models(self):
        """Testa se os modelos do banco estão funcionando"""
        try:
            # Verificar se existem dados de demonstração
            user_count = User.objects.count()
            shortcut_count = Shortcut.objects.count()
            category_count = Category.objects.count()

            self.log(f"✅ Banco de dados funcionando: {user_count} usuários, {shortcut_count} atalhos, {category_count} categorias", "PASS")
            return True
        except Exception as e:
            self.log(f"❌ Erro ao testar modelos do banco: {e}", "FAIL")
            return False

    def cleanup_test_data(self):
        """Remove dados de teste criados"""
        try:
            # Remover usuário de teste se criado
            User.objects.filter(username='test_integration').delete()

            # Remover atalho de teste
            Shortcut.objects.filter(trigger='//test-integration').delete()

            self.log("✅ Dados de teste removidos", "PASS")
        except Exception as e:
            self.log(f"⚠️ Erro ao limpar dados de teste: {e}", "WARN")

    def run_all_tests(self):
        """Executa todos os testes"""
        self.log("🚀 Iniciando testes de integração Symplifika Django-Frontend", "INFO")
        self.log("=" * 60, "INFO")

        tests = [
            self.test_server_running,
            self.test_frontend_template,
            self.test_static_files,
            self.test_database_models,
            self.test_admin_access,
            self.test_user_login,
            self.test_authenticated_requests,
            self.test_shortcuts_api,
            self.test_categories_api,
        ]

        passed = 0
        failed = 0

        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log(f"❌ Erro inesperado no teste {test.__name__}: {e}", "FAIL")
                failed += 1

            # Pequena pausa entre testes
            sleep(0.5)

        # Limpar dados de teste
        self.cleanup_test_data()

        self.log("=" * 60, "INFO")
        self.log(f"📊 RESULTADO FINAL:", "INFO")
        self.log(f"   ✅ Testes passou: {passed}", "INFO")
        self.log(f"   ❌ Testes falharam: {failed}", "INFO")
        self.log(f"   📈 Taxa de sucesso: {(passed/(passed+failed)*100):.1f}%", "INFO")

        if failed == 0:
            self.log("🎉 INTEGRAÇÃO DJANGO-FRONTEND CONCLUÍDA COM SUCESSO!", "PASS")
            self.log("✅ Todas as funcionalidades estão operacionais", "PASS")
            self.log("🌐 Acesse: http://127.0.0.1:8000 para usar a aplicação", "INFO")
        else:
            self.log("⚠️ Alguns testes falharam. Verifique os logs acima.", "WARN")

        return failed == 0

def main():
    """Função principal"""
    print("Symplifika - Teste de Integração Django-Frontend")
    print("=" * 50)

    tester = SymplifikaIntegrationTest()
    success = tester.run_all_tests()

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
