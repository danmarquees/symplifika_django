#!/usr/bin/env python
"""
Script de teste para verificar a integração com Google Gemini
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

from shortcuts.services import AIService
from django.conf import settings
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)

def test_environment():
    """Testa as configurações do ambiente"""
    print("🔍 Verificando configurações do ambiente...")

    # Verificar se a API key está configurada
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        print("❌ GEMINI_API_KEY não está configurada")
        return False

    print(f"✅ GEMINI_API_KEY configurada: {api_key[:10]}...")

    # Verificar se a biblioteca está instalada
    try:
        import google.generativeai as genai
        print("✅ google-generativeai instalado corretamente")
    except ImportError:
        print("❌ google-generativeai não está instalado")
        print("   Execute: pip install google-generativeai")
        return False

    return True

def test_ai_service_initialization():
    """Testa a inicialização do serviço de IA"""
    print("\n🔍 Testando inicialização do AIService...")

    try:
        service = AIService()
        print(f"✅ AIService inicializado com modelo: {service.model_name}")

        if service.model:
            print("✅ Modelo Gemini configurado corretamente")
        else:
            print("❌ Modelo Gemini não foi configurado")
            return False

        return True
    except Exception as e:
        print(f"❌ Erro ao inicializar AIService: {e}")
        return False

def test_api_status():
    """Testa o status da API"""
    print("\n🔍 Verificando status da API...")

    try:
        service = AIService()
        status = service.check_api_status()

        print(f"API configurada: {status['api_configured']}")
        print(f"Modelo: {status['model']}")
        print(f"API acessível: {status['api_accessible']}")

        if status['error']:
            print(f"Erro: {status['error']}")

        return status['api_accessible']
    except Exception as e:
        print(f"❌ Erro ao verificar status da API: {e}")
        return False

def test_text_enhancement():
    """Testa a funcionalidade de expansão de texto"""
    print("\n🔍 Testando expansão de texto...")

    test_text = "Olá, obrigado pelo seu email."

    try:
        service = AIService()
        enhanced = service.enhance_text(test_text)

        print(f"Texto original: {test_text}")
        print(f"Texto expandido: {enhanced}")

        if enhanced and enhanced != test_text:
            print("✅ Expansão de texto funcionando")
            return True
        else:
            print("❌ Expansão de texto não funcionou como esperado")
            return False

    except Exception as e:
        print(f"❌ Erro na expansão de texto: {e}")
        return False

def test_email_template():
    """Testa a geração de template de email"""
    print("\n🔍 Testando geração de template de email...")

    try:
        service = AIService()
        template = service.generate_email_template("boas-vindas", "profissional")

        print("Template gerado:")
        print("-" * 50)
        print(template)
        print("-" * 50)

        if template and "assunto" in template.lower():
            print("✅ Geração de template funcionando")
            return True
        else:
            print("❌ Template não foi gerado corretamente")
            return False

    except Exception as e:
        print(f"❌ Erro na geração de template: {e}")
        return False

def test_shortcuts_suggestions():
    """Testa as sugestões de atalhos"""
    print("\n🔍 Testando sugestões de atalhos...")

    test_text = "Preciso enviar um email de agradecimento para o cliente"

    try:
        service = AIService()
        suggestions = service.suggest_shortcuts(test_text, 3)

        print(f"Texto: {test_text}")
        print("Sugestões:")

        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion['trigger']} - {suggestion['title']}")
            print(f"     {suggestion['description']}")

        if suggestions and len(suggestions) > 0:
            print("✅ Sugestões de atalhos funcionando")
            return True
        else:
            print("❌ Nenhuma sugestão foi gerada")
            return False

    except Exception as e:
        print(f"❌ Erro nas sugestões de atalhos: {e}")
        return False

def test_fallback_functionality():
    """Testa funcionalidades de fallback"""
    print("\n🔍 Testando funcionalidades de fallback...")

    try:
        # Simular API key inválida
        original_key = settings.GEMINI_API_KEY
        settings.GEMINI_API_KEY = ''

        service = AIService()

        # Testar template de fallback
        template = service.generate_email_template("agradecimento")

        if template and "agradecimento" in template.lower():
            print("✅ Fallback de template funcionando")
            fallback_works = True
        else:
            print("❌ Fallback de template não funciona")
            fallback_works = False

        # Restaurar API key
        settings.GEMINI_API_KEY = original_key

        return fallback_works

    except Exception as e:
        print(f"❌ Erro no teste de fallback: {e}")
        # Restaurar API key mesmo em caso de erro
        settings.GEMINI_API_KEY = original_key if 'original_key' in locals() else settings.GEMINI_API_KEY
        return False

def run_all_tests():
    """Executa todos os testes"""
    print("🚀 Iniciando testes de integração com Google Gemini\n")

    tests = [
        ("Configurações do ambiente", test_environment),
        ("Inicialização do serviço", test_ai_service_initialization),
        ("Status da API", test_api_status),
        ("Expansão de texto", test_text_enhancement),
        ("Template de email", test_email_template),
        ("Sugestões de atalhos", test_shortcuts_suggestions),
        ("Funcionalidades de fallback", test_fallback_functionality)
    ]

    results = []

    for test_name, test_function in tests:
        print(f"\n{'='*60}")
        print(f"TESTE: {test_name}")
        print('='*60)

        try:
            result = test_function()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro inesperado no teste '{test_name}': {e}")
            results.append((test_name, False))

    # Resumo dos resultados
    print(f"\n{'='*60}")
    print("RESUMO DOS TESTES")
    print('='*60)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status} - {test_name}")
        if result:
            passed += 1

    print(f"\nResultado: {passed}/{total} testes passaram")

    if passed == total:
        print("\n🎉 Todos os testes passaram! A integração com Gemini está funcionando.")
    elif passed >= total * 0.7:  # 70% dos testes
        print("\n⚠️  A maioria dos testes passou. Verifique os erros acima.")
    else:
        print("\n❌ Muitos testes falharam. Revise a configuração.")

    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
