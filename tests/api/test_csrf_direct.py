#!/usr/bin/env python3

"""
Teste direto das configurações CSRF para extensões Chrome
"""

import requests
import json

def test_csrf_fix():
    """Testa se o CSRF foi corrigido para extensões Chrome"""
    
    # URL do endpoint de login
    url = 'http://127.0.0.1:8000/api/token/'
    
    # Headers simulando extensão Chrome
    headers = {
        'Content-Type': 'application/json',
        'Origin': 'chrome-extension://deehgnjaebcffjbpmabnncphlpjglloa',
        'User-Agent': 'Chrome Extension Symplifika/1.0',
    }
    
    # Dados de login
    data = {
        'login': 'admin',
        'password': 'admin123'
    }
    
    print("🧪 Testando correção CSRF para extensão Chrome...")
    print(f"📡 URL: {url}")
    print(f"🌐 Origin: {headers['Origin']}")
    
    try:
        # Fazer requisição POST
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        print(f"\n📊 Resultado:")
        print(f"Status Code: {response.status_code}")
        print(f"Headers de Resposta:")
        for header, value in response.headers.items():
            if 'access-control' in header.lower() or 'cors' in header.lower():
                print(f"  {header}: {value}")
        
        if response.status_code == 200:
            print("✅ SUCESSO! Login funcionou sem erro CSRF")
            try:
                json_response = response.json()
                if 'access' in json_response:
                    print("✅ Token JWT recebido com sucesso")
                    print(f"Token (primeiros 20 chars): {json_response['access'][:20]}...")
                else:
                    print("⚠️  Resposta sem token JWT")
            except:
                print("⚠️  Resposta não é JSON válido")
                
        elif response.status_code == 403:
            print("❌ FALHA! Ainda há erro CSRF (403 Forbidden)")
            print("Resposta:", response.text[:200])
            
        elif response.status_code == 401:
            print("🔐 Credenciais inválidas (mas CSRF OK)")
            print("Resposta:", response.text[:200])
            
        else:
            print(f"❓ Status inesperado: {response.status_code}")
            print("Resposta:", response.text[:200])
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor")
        print("💡 Certifique-se de que o Django está rodando em 127.0.0.1:8000")
        
    except requests.exceptions.Timeout:
        print("❌ Erro: Timeout na conexão")
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_csrf_fix()
