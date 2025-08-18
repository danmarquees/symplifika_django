#!/usr/bin/env python3
"""
Script de demonstração da integração Django-Frontend do Symplifika
Este script mostra como usar o sistema completo.
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def print_banner():
    """Exibe banner do sistema"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                         SYMPLIFIKA                          ║
║                Sistema de Atalhos Inteligentes              ║
║                                                              ║
║             🎉 INTEGRAÇÃO DJANGO-FRONTEND 🎉                ║
║                     ✅ CONCLUÍDA ✅                         ║
╚══════════════════════════════════════════════════════════════╝
    """)

def check_requirements():
    """Verifica se os requisitos estão instalados"""
    print("🔍 Verificando requisitos...")

    try:
        import django
        print(f"  ✅ Django {django.get_version()} instalado")
    except ImportError:
        print("  ❌ Django não encontrado. Execute: pip install -r requirements.txt")
        return False

    try:
        import rest_framework
        print("  ✅ Django REST Framework instalado")
    except ImportError:
        print("  ❌ DRF não encontrado. Execute: pip install -r requirements.txt")
        return False

    # Verificar se arquivos essenciais existem
    files_to_check = [
        'manage.py',
        'templates/frontend.html',
        'static/js/app.js',
        'symplifika/settings.py'
    ]

    for file_path in files_to_check:
        if Path(file_path).exists():
            print(f"  ✅ {file_path} encontrado")
        else:
            print(f"  ❌ {file_path} não encontrado")
            return False

    return True

def setup_database():
    """Configura o banco de dados"""
    print("\n🗄️ Configurando banco de dados...")

    try:
        # Executar migrações
        result = subprocess.run([
            sys.executable, 'manage.py', 'migrate', '--verbosity=0'
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("  ✅ Migrações aplicadas")
        else:
            print(f"  ❌ Erro nas migrações: {result.stderr}")
            return False

        # Verificar se admin existe
        result = subprocess.run([
            sys.executable, 'manage.py', 'shell', '-c',
            "from django.contrib.auth.models import User; print(User.objects.filter(username='admin').exists())"
        ], capture_output=True, text=True)

        if 'True' in result.stdout:
            print("  ✅ Usuário admin já existe")
        else:
            print("  ⚠️ Criando usuário admin...")
            subprocess.run([
                sys.executable, 'manage.py', 'create_admin'
            ], capture_output=True)

        return True

    except Exception as e:
        print(f"  ❌ Erro na configuração do banco: {e}")
        return False

def collect_static():
    """Coleta arquivos estáticos"""
    print("\n📁 Coletando arquivos estáticos...")

    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'collectstatic', '--noinput', '--verbosity=0'
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("  ✅ Arquivos estáticos coletados")
            return True
        else:
            print(f"  ❌ Erro ao coletar estáticos: {result.stderr}")
            return False

    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def start_server():
    """Inicia o servidor Django"""
    print("\n🚀 Iniciando servidor Django...")

    try:
        # Iniciar servidor em background
        process = subprocess.Popen([
            sys.executable, 'manage.py', 'runserver', '127.0.0.1:8000'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Aguardar servidor iniciar
        print("  ⏳ Aguardando servidor iniciar...")
        time.sleep(3)

        # Verificar se processo ainda está rodando
        if process.poll() is None:
            print("  ✅ Servidor iniciado com sucesso!")
            print("  🌐 URL: http://127.0.0.1:8000")
            return process
        else:
            print("  ❌ Servidor falhou ao iniciar")
            return None

    except Exception as e:
        print(f"  ❌ Erro ao iniciar servidor: {e}")
        return None

def show_demo_info():
    """Mostra informações da demonstração"""
    print("""
🎯 DEMONSTRAÇÃO INTERATIVA

📱 ACESSE A APLICAÇÃO:
   🌐 Interface Web: http://127.0.0.1:8000
   🔧 Admin Django: http://127.0.0.1:8000/admin
   📡 API REST: http://127.0.0.1:8000/api

👤 CREDENCIAIS DE TESTE:
   • Demo: demo / demo123
   • Admin: admin / admin123

✨ FUNCIONALIDADES IMPLEMENTADAS:
   ✅ Login/Registro com validação
   ✅ CRUD completo de atalhos
   ✅ CRUD de categorias com cores
   ✅ Busca e filtros em tempo real
   ✅ Tema claro/escuro automático
   ✅ Exportar/Importar dados
   ✅ Interface responsiva
   ✅ Notificações toast
   ✅ Modais interativos
   ✅ Cópia automática para clipboard

🎨 PÁGINAS DISPONÍVEIS:
   📝 Dashboard de atalhos
   📂 Gestão de categorias
   ⚙️ Configurações do usuário
   🔐 Autenticação segura

🔧 TECNOLOGIAS:
   • Backend: Django 5.2 + DRF
   • Frontend: HTML5 + Tailwind CSS + JavaScript
   • Banco: SQLite com dados de demo
   • Auth: Token-based authentication
   • API: RESTful endpoints

💡 COMO TESTAR:
   1. Acesse http://127.0.0.1:8000
   2. Faça login com demo/demo123
   3. Explore as funcionalidades
   4. Crie atalhos e categorias
   5. Teste exportar/importar
   6. Alterne o tema claro/escuro

🎉 INTEGRAÇÃO 100% FUNCIONAL!
""")

def open_browser():
    """Abre o navegador automaticamente"""
    try:
        print("\n🌐 Abrindo navegador...")
        webbrowser.open('http://127.0.0.1:8000')
        print("  ✅ Navegador aberto")
    except Exception as e:
        print(f"  ⚠️ Não foi possível abrir automaticamente: {e}")
        print("  📋 Acesse manualmente: http://127.0.0.1:8000")

def main():
    """Função principal"""
    print_banner()

    # Verificar se estamos no diretório correto
    if not Path('manage.py').exists():
        print("❌ Execute este script do diretório symplifika_dango/")
        sys.exit(1)

    # Executar verificações
    if not check_requirements():
        print("\n❌ Requisitos não atendidos. Execute: pip install -r requirements.txt")
        sys.exit(1)

    if not setup_database():
        print("\n❌ Falha na configuração do banco de dados")
        sys.exit(1)

    if not collect_static():
        print("\n❌ Falha na coleta de arquivos estáticos")
        sys.exit(1)

    # Iniciar servidor
    server_process = start_server()
    if not server_process:
        print("\n❌ Falha ao iniciar servidor")
        sys.exit(1)

    # Mostrar informações e abrir navegador
    show_demo_info()
    open_browser()

    try:
        print("\n⌨️ Pressione Ctrl+C para parar o servidor...")
        server_process.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Parando servidor...")
        server_process.terminate()
        server_process.wait()
        print("✅ Servidor parado com sucesso!")
        print("\n🎉 Obrigado por testar o Symplifika!")

if __name__ == "__main__":
    main()
