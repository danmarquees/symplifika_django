#!/usr/bin/env python3

"""
Teste de debug para o endpoint de login
"""

import requests
import json

def test_login_debug():
    """Testa o endpoint de login com diferentes formatos de dados"""
    
    url = 'http://127.0.0.1:8000/api/token/'
    
    # Teste 1: Dados como a extensão envia
    print("🧪 Teste 1: Dados da extensão Chrome")
    headers = {
        'Content-Type': 'application/json',
        'Origin': 'chrome-extension://deehgnjaebcffjbpmabnncphlpjglloa',
    }
    
    data = {
        'email': 'admin',  # Como a extensão envia
        'username': 'admin',  # Como a extensão envia
        'login': 'admin',  # Como a extensão envia
        'password': 'admin123'
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        print()
    except Exception as e:
        print(f"Erro: {e}")
        print()
    
    # Teste 2: Dados simples
    print("🧪 Teste 2: Dados simples")
    data2 = {
        'login': 'admin',
        'password': 'admin123'
    }
    
    try:
        response = requests.post(url, headers=headers, json=data2, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        print()
    except Exception as e:
        print(f"Erro: {e}")
        print()
    
    # Teste 3: Dados como username
    print("🧪 Teste 3: Campo username")
    data3 = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        response = requests.post(url, headers=headers, json=data3, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        print()
    except Exception as e:
        print(f"Erro: {e}")
        print()
    
    # Teste 4: Verificar se usuário existe
    print("🧪 Teste 4: Verificar usuários no sistema")
    try:
        admin_url = 'http://127.0.0.1:8000/admin/'
        response = requests.get(admin_url, timeout=5)
        print(f"Admin accessible: {response.status_code == 200}")
    except Exception as e:
        print(f"Admin não acessível: {e}")

if __name__ == "__main__":
    test_login_debug()
