#!/usr/bin/env python3
"""
Symplifika Server Status Checker
Checks if the Django development server is running and provides helpful information.
"""

import sys
import os
import socket
import subprocess
import requests
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_colored(text, color=Colors.WHITE):
    """Print colored text to terminal"""
    print(f"{color}{text}{Colors.END}")

def print_header():
    """Print application header"""
    print_colored("\n" + "="*60, Colors.CYAN)
    print_colored("🚀 SYMPLIFIKA DJANGO SERVER STATUS CHECKER", Colors.BOLD + Colors.CYAN)
    print_colored("="*60, Colors.CYAN)

def check_port(host, port):
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def check_django_process():
    """Check if Django runserver process is running"""
    try:
        # Check for Django runserver process
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True,
            timeout=5
        )

        lines = result.stdout.split('\n')
        django_processes = [line for line in lines if 'manage.py runserver' in line and 'grep' not in line]

        return len(django_processes) > 0, django_processes
    except Exception:
        return False, []

def check_api_endpoint():
    """Check if the API endpoints are responding"""
    try:
        response = requests.get('http://127.0.0.1:8000/shortcuts/api/', timeout=5)
        return response.status_code == 200, response.status_code
    except requests.exceptions.ConnectionError:
        return False, "Connection Refused"
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)

def check_static_files():
    """Check if static files are being served correctly"""
    static_files = [
        '/static/js/app.js',
        '/static/js/base.js',
        '/static/css/style.css'
    ]

    results = {}
    for file_path in static_files:
        try:
            response = requests.get(f'http://127.0.0.1:8000{file_path}', timeout=3)
            results[file_path] = response.status_code == 200
        except Exception:
            results[file_path] = False

    return results

def check_database():
    """Check if database is accessible"""
    try:
        # Check if db.sqlite3 exists and is readable
        db_path = Path('db.sqlite3')
        if db_path.exists():
            # Try to read the file
            with open(db_path, 'rb') as f:
                f.read(1024)  # Read first 1KB
            return True, "SQLite database accessible"
        else:
            return False, "Database file not found"
    except Exception as e:
        return False, f"Database error: {str(e)}"

def get_django_version():
    """Get Django version"""
    try:
        import django
        return django.get_version()
    except ImportError:
        return "Not installed"

def main():
    """Main function"""
    print_header()

    # Check current directory
    if not Path('manage.py').exists():
        print_colored("❌ Error: manage.py not found in current directory", Colors.RED)
        print_colored("Please run this script from the Django project root directory.", Colors.YELLOW)
        sys.exit(1)

    # 1. Check Django installation
    print_colored("\n📋 SYSTEM CHECK", Colors.BOLD + Colors.BLUE)
    print_colored("-" * 30, Colors.BLUE)

    django_version = get_django_version()
    if django_version == "Not installed":
        print_colored(f"❌ Django: {django_version}", Colors.RED)
    else:
        print_colored(f"✅ Django: {django_version}", Colors.GREEN)

    # 2. Check database
    db_ok, db_msg = check_database()
    if db_ok:
        print_colored(f"✅ Database: {db_msg}", Colors.GREEN)
    else:
        print_colored(f"❌ Database: {db_msg}", Colors.RED)

    # 3. Check if port 8000 is open
    print_colored("\n🌐 SERVER STATUS", Colors.BOLD + Colors.BLUE)
    print_colored("-" * 30, Colors.BLUE)

    port_open = check_port('127.0.0.1', 8000)
    if port_open:
        print_colored("✅ Port 8000: Open", Colors.GREEN)
    else:
        print_colored("❌ Port 8000: Closed", Colors.RED)

    # 4. Check Django process
    process_running, processes = check_django_process()
    if process_running:
        print_colored("✅ Django Process: Running", Colors.GREEN)
        print_colored("   Active processes:", Colors.CYAN)
        for proc in processes:
            # Clean up the process line for better display
            clean_proc = ' '.join(proc.split()[10:])  # Skip PID, CPU, etc.
            print_colored(f"   → {clean_proc}", Colors.WHITE)
    else:
        print_colored("❌ Django Process: Not running", Colors.RED)

    # 5. Check API endpoints
    print_colored("\n🔌 API ENDPOINTS", Colors.BOLD + Colors.BLUE)
    print_colored("-" * 30, Colors.BLUE)

    api_ok, api_status = check_api_endpoint()
    if api_ok:
        print_colored(f"✅ API Endpoint: Responding (HTTP {api_status})", Colors.GREEN)
    else:
        print_colored(f"❌ API Endpoint: {api_status}", Colors.RED)

    # 6. Check static files (only if server is running)
    if port_open:
        print_colored("\n📁 STATIC FILES", Colors.BOLD + Colors.BLUE)
        print_colored("-" * 30, Colors.BLUE)

        static_results = check_static_files()
        for file_path, is_ok in static_results.items():
            status = "✅" if is_ok else "❌"
            color = Colors.GREEN if is_ok else Colors.RED
            print_colored(f"{status} {file_path}", color)

    # 7. Provide recommendations
    print_colored("\n💡 RECOMMENDATIONS", Colors.BOLD + Colors.YELLOW)
    print_colored("-" * 30, Colors.YELLOW)

    if not port_open and not process_running:
        print_colored("🚀 Start the Django server:", Colors.CYAN)
        print_colored("   python manage.py runserver 127.0.0.1:8000", Colors.WHITE)
        print_colored("   OR use the startup script:", Colors.WHITE)
        print_colored("   ./start_server.sh", Colors.WHITE)
    elif port_open and not api_ok:
        print_colored("🔧 Server is running but API is not responding:", Colors.CYAN)
        print_colored("   Check Django logs for errors", Colors.WHITE)
        print_colored("   Verify URL configuration in urls.py", Colors.WHITE)
    elif not db_ok:
        print_colored("🗄️  Database issues detected:", Colors.CYAN)
        print_colored("   Run migrations: python manage.py migrate", Colors.WHITE)
        print_colored("   Create superuser: python manage.py createsuperuser", Colors.WHITE)
    else:
        print_colored("🎉 Everything looks good!", Colors.GREEN)
        print_colored("   Server should be accessible at: http://127.0.0.1:8000", Colors.WHITE)

    # 8. Quick commands reference
    print_colored("\n📚 QUICK COMMANDS", Colors.BOLD + Colors.CYAN)
    print_colored("-" * 30, Colors.CYAN)
    print_colored("Start server:     python manage.py runserver 127.0.0.1:8000", Colors.WHITE)
    print_colored("Stop server:      Ctrl+C (in server terminal)", Colors.WHITE)
    print_colored("Run migrations:   python manage.py migrate", Colors.WHITE)
    print_colored("Collect static:   python manage.py collectstatic", Colors.WHITE)
    print_colored("Django shell:     python manage.py shell", Colors.WHITE)
    print_colored("View logs:        tail -f server.log", Colors.WHITE)

    print_colored("\n" + "="*60 + "\n", Colors.CYAN)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n\n👋 Goodbye!", Colors.YELLOW)
        sys.exit(0)
    except Exception as e:
        print_colored(f"\n❌ Unexpected error: {str(e)}", Colors.RED)
        sys.exit(1)
