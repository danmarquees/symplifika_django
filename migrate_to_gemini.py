#!/usr/bin/env python
"""
Script de migração automática da OpenAI para Google Gemini
Este script facilita a transição completa do projeto para usar a API do Google Gemini
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header():
    """Imprime o cabeçalho do script"""
    print("=" * 70)
    print("🔄 MIGRAÇÃO AUTOMÁTICA: OpenAI → Google Gemini")
    print("=" * 70)
    print("Este script irá migrar seu projeto para usar a API do Google Gemini")
    print("em vez da OpenAI, mantendo todas as funcionalidades.\n")

def check_requirements():
    """Verifica se os requisitos estão atendidos"""
    print("🔍 Verificando requisitos...")

    # Verificar se estamos no diretório correto
    if not Path("manage.py").exists():
        print("❌ Erro: Execute este script no diretório raiz do projeto Django")
        return False

    # Verificar se o Python está disponível
    try:
        result = subprocess.run([sys.executable, "--version"],
                              capture_output=True, text=True)
        print(f"✅ Python: {result.stdout.strip()}")
    except:
        print("❌ Python não encontrado")
        return False

    # Verificar se pip está disponível
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"],
                      capture_output=True, check=True)
        print("✅ pip disponível")
    except:
        print("❌ pip não encontrado")
        return False

    return True

def backup_files():
    """Cria backup dos arquivos importantes"""
    print("\n📦 Criando backup dos arquivos...")

    backup_dir = Path("backup_openai_migration")
    backup_dir.mkdir(exist_ok=True)

    files_to_backup = [
        "requirements.txt",
        "symplifika/settings.py",
        "shortcuts/services.py",
        "check_environment.py",
        ".env"
    ]

    for file_path in files_to_backup:
        if Path(file_path).exists():
            dest = backup_dir / file_path.replace("/", "_")
            shutil.copy2(file_path, dest)
            print(f"✅ Backup: {file_path} → {dest}")

    print(f"✅ Backup criado em: {backup_dir.absolute()}")

def check_env_file():
    """Verifica e atualiza o arquivo .env"""
    print("\n🔧 Verificando arquivo .env...")

    env_path = Path(".env")

    if not env_path.exists():
        print("⚠️  Arquivo .env não encontrado")
        create_env = input("Deseja criar um arquivo .env básico? (s/n): ").lower().strip()

        if create_env == 's':
            create_basic_env()
        else:
            print("⚠️  Lembre-se de configurar GEMINI_API_KEY manualmente")
        return

    # Ler o arquivo .env atual
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Verificar se já tem GEMINI_API_KEY
    if 'GEMINI_API_KEY' in content:
        print("✅ GEMINI_API_KEY já está no .env")
        return

    # Verificar se tem OPENAI_API_KEY
    if 'OPENAI_API_KEY' in content:
        print("🔄 Convertendo OPENAI_API_KEY para GEMINI_API_KEY...")

        # Comentar a linha antiga e adicionar a nova
        updated_content = content.replace(
            'OPENAI_API_KEY=',
            '# OPENAI_API_KEY= # Migrado para Gemini\nGEMINI_API_KEY='
        )

        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        print("✅ .env atualizado - configure sua GEMINI_API_KEY")
    else:
        # Adicionar GEMINI_API_KEY no final
        with open(env_path, 'a', encoding='utf-8') as f:
            f.write('\n# Google Gemini API\nGEMINI_API_KEY=sua-chave-gemini-aqui\n')

        print("✅ GEMINI_API_KEY adicionada ao .env")

def create_basic_env():
    """Cria um arquivo .env básico"""
    basic_env = """# Django Configuration
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Google Gemini API (obrigatório para funcionalidades de IA)
GEMINI_API_KEY=sua-chave-gemini-aqui

# Security
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
"""

    with open('.env', 'w', encoding='utf-8') as f:
        f.write(basic_env)

    print("✅ Arquivo .env básico criado")

def install_dependencies():
    """Instala as novas dependências"""
    print("\n📦 Instalando dependências do Google Gemini...")

    try:
        # Desinstalar openai
        print("🗑️  Removendo pacote openai...")
        subprocess.run([
            sys.executable, "-m", "pip", "uninstall", "openai", "-y"
        ], check=True, capture_output=True)
        print("✅ Pacote openai removido")

    except subprocess.CalledProcessError:
        print("⚠️  Pacote openai não estava instalado")

    try:
        # Instalar google-generativeai
        print("📥 Instalando google-generativeai...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "google-generativeai==0.3.2"
        ], check=True)
        print("✅ google-generativeai instalado")

        # Reinstalar outras dependências do requirements.txt
        if Path("requirements.txt").exists():
            print("📥 Reinstalando dependências do projeto...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], check=True)
            print("✅ Dependências instaladas")

    except subprocess.CalledProcessError as e:
        print(f"❌ Erro na instalação: {e}")
        return False

    return True

def run_tests():
    """Executa testes de verificação"""
    print("\n🧪 Executando testes de verificação...")

    # Verificar se o arquivo de teste existe
    test_file = Path("test_gemini_integration.py")
    if not test_file.exists():
        print("⚠️  Arquivo de teste não encontrado - pulando testes")
        return

    try:
        result = subprocess.run([
            sys.executable, "test_gemini_integration.py"
        ], capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            print("✅ Todos os testes passaram!")
        else:
            print("⚠️  Alguns testes falharam - verifique a configuração")
            print("Saída do teste:")
            print(result.stdout)
            if result.stderr:
                print("Erros:")
                print(result.stderr)

    except subprocess.TimeoutExpired:
        print("⚠️  Testes excederam tempo limite - verifique manualmente")
    except Exception as e:
        print(f"⚠️  Erro ao executar testes: {e}")

def show_next_steps():
    """Mostra os próximos passos após a migração"""
    print("\n" + "=" * 70)
    print("🎉 MIGRAÇÃO CONCLUÍDA!")
    print("=" * 70)
    print("\n📋 PRÓXIMOS PASSOS:")
    print("\n1. 🔑 CONFIGURAR API KEY:")
    print("   • Acesse: https://makersuite.google.com/app/apikey")
    print("   • Crie uma nova API Key do Google Gemini")
    print("   • Edite o arquivo .env e substitua 'sua-chave-gemini-aqui' pela sua chave real")

    print("\n2. ✅ VERIFICAR FUNCIONAMENTO:")
    print("   • Execute: python test_gemini_integration.py")
    print("   • Ou teste no Django shell:")
    print("     python manage.py shell")
    print("     from shortcuts.services import AIService")
    print("     service = AIService()")
    print("     print(service.check_api_status())")

    print("\n3. 🚀 TESTAR A APLICAÇÃO:")
    print("   • Inicie o servidor: python manage.py runserver")
    print("   • Teste as funcionalidades de IA na interface")

    print("\n4. 📚 DOCUMENTAÇÃO:")
    print("   • Leia o arquivo GEMINI_MIGRATION.md para mais detalhes")
    print("   • Consulte https://ai.google.dev/docs para documentação da API")

    print("\n5. 🔄 DEPLOY EM PRODUÇÃO:")
    print("   • Configure GEMINI_API_KEY no seu ambiente de produção")
    print("   • Atualize requirements.txt no servidor")
    print("   • Faça o deploy das alterações")

    print(f"\n💾 BACKUP: Arquivos originais salvos em 'backup_openai_migration/'")
    print("\n✨ Sua aplicação agora usa Google Gemini! 🚀")

def main():
    """Função principal do script de migração"""
    print_header()

    # Verificar confirmação do usuário
    confirm = input("Deseja continuar com a migração? (s/n): ").lower().strip()
    if confirm != 's':
        print("Migração cancelada.")
        return

    # Executar etapas da migração
    steps = [
        ("Verificando requisitos", check_requirements),
        ("Criando backup", backup_files),
        ("Configurando .env", check_env_file),
        ("Instalando dependências", install_dependencies),
        ("Executando testes", run_tests)
    ]

    for step_name, step_function in steps:
        print(f"\n{'▶️ ' + step_name + '...'}")
        try:
            if step_function and not step_function():
                print(f"❌ Falha em: {step_name}")
                if step_name == "Verificando requisitos" or step_name == "Instalando dependências":
                    print("Migração interrompida devido a erro crítico.")
                    return
        except KeyboardInterrupt:
            print("\n⚠️  Migração interrompida pelo usuário")
            return
        except Exception as e:
            print(f"❌ Erro em {step_name}: {e}")
            if step_name == "Verificando requisitos" or step_name == "Instalando dependências":
                print("Migração interrompida devido a erro crítico.")
                return

    show_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Migração interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)
