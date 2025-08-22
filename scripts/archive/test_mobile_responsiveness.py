#!/usr/bin/env python3
"""
Script de Teste de Responsividade Mobile - Symplifika
Testa se todas as páginas principais atendem aos critérios de responsividade.
"""

import requests
import json
import time
from urllib.parse import urljoin
from dataclasses import dataclass
from typing import List, Dict, Optional
import sys

@dataclass
class ResponsivenessTest:
    url: str
    name: str
    mobile_width: int = 375
    mobile_height: int = 667
    tablet_width: int = 768
    tablet_height: int = 1024
    desktop_width: int = 1920
    desktop_height: int = 1080

@dataclass
class TestResult:
    url: str
    name: str
    passed: bool
    issues: List[str]
    score: int  # 0-100
    device: str

class MobileResponsivenessChecker:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results: List[TestResult] = []

        # Headers para simular diferentes dispositivos
        self.mobile_headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
        }

        self.tablet_headers = {
            'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
        }

        self.desktop_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_test_pages(self) -> List[ResponsivenessTest]:
        """Define as páginas que serão testadas"""
        return [
            ResponsivenessTest("/", "Página Inicial"),
            ResponsivenessTest("/login/", "Login"),
            ResponsivenessTest("/register/", "Registro"),
            ResponsivenessTest("/dashboard/", "Dashboard"),
            ResponsivenessTest("/pricing/", "Preços"),
            ResponsivenessTest("/about/", "Sobre"),
            ResponsivenessTest("/help/", "Ajuda"),
            ResponsivenessTest("/contact/", "Contato"),
            ResponsivenessTest("/faq/", "FAQ"),
            ResponsivenessTest("/privacy/", "Privacidade"),
            ResponsivenessTest("/terms/", "Termos de Uso"),
        ]

    def check_viewport_meta(self, html_content: str) -> tuple[bool, List[str]]:
        """Verifica se a meta tag viewport está correta"""
        issues = []

        if 'name="viewport"' not in html_content:
            issues.append("Meta tag viewport não encontrada")
            return False, issues

        if 'width=device-width' not in html_content:
            issues.append("Viewport não está configurado com width=device-width")

        if 'initial-scale=1' not in html_content:
            issues.append("Viewport não está configurado com initial-scale=1")

        return len(issues) == 0, issues

    def check_responsive_classes(self, html_content: str) -> tuple[bool, List[str]]:
        """Verifica se as classes responsivas do Tailwind estão sendo usadas"""
        issues = []
        responsive_patterns = [
            'sm:', 'md:', 'lg:', 'xl:', '2xl:',
            'max-w-', 'min-w-',
            'flex-col', 'flex-row',
            'grid-cols-1', 'grid-cols-2', 'grid-cols-3',
            'hidden', 'block',
        ]

        found_responsive = False
        for pattern in responsive_patterns:
            if pattern in html_content:
                found_responsive = True
                break

        if not found_responsive:
            issues.append("Não foram encontradas classes responsivas")

        # Verificar se há classes mobile-first
        mobile_first_patterns = ['mobile-', 'touch-', 'safe-area-']
        mobile_optimizations = any(pattern in html_content for pattern in mobile_first_patterns)

        if not mobile_optimizations and not found_responsive:
            issues.append("Não foram encontradas otimizações mobile")

        return len(issues) == 0, issues

    def check_touch_targets(self, html_content: str) -> tuple[bool, List[str]]:
        """Verifica se os alvos de toque têm tamanho adequado"""
        issues = []

        # Procurar por elementos com min-height e min-width adequados
        touch_target_patterns = [
            'min-h-[44px]', 'min-h-[48px]',
            'min-w-[44px]', 'min-w-[48px]',
            'min-height: 44px', 'min-height: 48px',
            'min-width: 44px', 'min-width: 48px',
            'touch-target'
        ]

        has_touch_targets = any(pattern in html_content for pattern in touch_target_patterns)

        if not has_touch_targets:
            issues.append("Não foram encontrados touch targets adequados (44px mínimo)")

        return has_touch_targets, issues

    def check_mobile_navigation(self, html_content: str) -> tuple[bool, List[str]]:
        """Verifica se há navegação mobile adequada"""
        issues = []

        # Verificar menu hamburger
        hamburger_patterns = [
            'mobile-menu', 'hamburger', 'menu-toggle',
            'data-sidebar-toggle', 'mobile-menu-button'
        ]

        has_mobile_nav = any(pattern in html_content for pattern in hamburger_patterns)

        if not has_mobile_nav:
            issues.append("Não foi encontrada navegação mobile (menu hamburger)")

        # Verificar se há breakpoints para esconder/mostrar elementos
        responsive_nav_patterns = ['md:hidden', 'lg:hidden', 'hidden md:block']
        has_responsive_nav = any(pattern in html_content for pattern in responsive_nav_patterns)

        if not has_responsive_nav:
            issues.append("Navegação não parece ser responsiva")

        return has_mobile_nav and has_responsive_nav, issues

    def check_images_responsive(self, html_content: str) -> tuple[bool, List[str]]:
        """Verifica se as imagens são responsivas"""
        issues = []

        # Contar tags img
        img_count = html_content.count('<img')
        if img_count > 0:
            # Verificar se há classes responsivas nas imagens
            responsive_img_patterns = [
                'max-w-full', 'w-full', 'h-auto',
                'object-cover', 'object-contain',
                'responsive'
            ]

            responsive_imgs = sum(1 for pattern in responsive_img_patterns if pattern in html_content)

            if responsive_imgs == 0:
                issues.append(f"Encontradas {img_count} imagens, mas nenhuma parece ser responsiva")

        return len(issues) == 0, issues

    def check_forms_mobile_friendly(self, html_content: str) -> tuple[bool, List[str]]:
        """Verifica se os formulários são mobile-friendly"""
        issues = []

        # Verificar se há formulários
        has_forms = '<form' in html_content

        if has_forms:
            # Verificar inputs com classes adequadas
            form_patterns = [
                'form-input', 'min-h-[48px]', 'text-base',
                'w-full', 'mobile-', 'touch-'
            ]

            mobile_form_optimizations = any(pattern in html_content for pattern in form_patterns)

            if not mobile_form_optimizations:
                issues.append("Formulários não parecem ter otimizações mobile")

        return len(issues) == 0 or not has_forms, issues

    def check_accessibility(self, html_content: str) -> tuple[bool, List[str]]:
        """Verifica recursos de acessibilidade"""
        issues = []

        accessibility_patterns = [
            'aria-label', 'aria-expanded', 'role=', 'sr-only',
            'focus:ring', 'focus:outline', 'tabindex'
        ]

        accessibility_features = sum(1 for pattern in accessibility_patterns if pattern in html_content)

        if accessibility_features < 3:
            issues.append("Poucos recursos de acessibilidade encontrados")

        return accessibility_features >= 3, issues

    def test_page(self, test: ResponsivenessTest, device: str, headers: dict) -> TestResult:
        """Testa uma página específica em um dispositivo"""
        url = urljoin(self.base_url, test.url)
        issues = []
        score = 100

        try:
            response = self.session.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                issues.append(f"Página retornou status {response.status_code}")
                score -= 20
                return TestResult(url, test.name, False, issues, score, device)

            html_content = response.text

            # Executar todos os testes
            tests = [
                ("Viewport Meta Tag", self.check_viewport_meta),
                ("Classes Responsivas", self.check_responsive_classes),
                ("Touch Targets", self.check_touch_targets),
                ("Navegação Mobile", self.check_mobile_navigation),
                ("Imagens Responsivas", self.check_images_responsive),
                ("Formulários Mobile", self.check_forms_mobile_friendly),
                ("Acessibilidade", self.check_accessibility),
            ]

            total_tests = len(tests)
            passed_tests = 0

            for test_name, test_func in tests:
                try:
                    passed, test_issues = test_func(html_content)
                    if passed:
                        passed_tests += 1
                    else:
                        issues.extend([f"{test_name}: {issue}" for issue in test_issues])
                except Exception as e:
                    issues.append(f"{test_name}: Erro no teste - {str(e)}")

            # Calcular pontuação baseada nos testes que passaram
            score = int((passed_tests / total_tests) * 100)

            return TestResult(url, test.name, len(issues) == 0, issues, score, device)

        except requests.RequestException as e:
            issues.append(f"Erro de conexão: {str(e)}")
            return TestResult(url, test.name, False, issues, 0, device)

    def run_tests(self) -> Dict[str, List[TestResult]]:
        """Executa todos os testes de responsividade"""
        print("🧪 Iniciando testes de responsividade mobile...")
        print("=" * 60)

        test_pages = self.get_test_pages()
        results = {"mobile": [], "tablet": [], "desktop": []}

        devices = [
            ("mobile", self.mobile_headers),
            ("tablet", self.tablet_headers),
            ("desktop", self.desktop_headers)
        ]

        for device_name, headers in devices:
            print(f"\n📱 Testando dispositivo: {device_name.upper()}")
            print("-" * 40)

            for test_page in test_pages:
                print(f"  Testando: {test_page.name}... ", end="")

                result = self.test_page(test_page, device_name, headers)
                results[device_name].append(result)

                if result.passed:
                    print(f"✅ PASSOU (Score: {result.score}/100)")
                else:
                    print(f"❌ FALHOU (Score: {result.score}/100)")
                    for issue in result.issues:
                        print(f"    - {issue}")

                time.sleep(0.1)  # Pequena pausa entre requests

        return results

    def generate_report(self, results: Dict[str, List[TestResult]]) -> None:
        """Gera relatório completo dos testes"""
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO FINAL DE RESPONSIVIDADE")
        print("=" * 60)

        total_tests = 0
        total_passed = 0
        device_scores = {}

        for device, device_results in results.items():
            device_total = len(device_results)
            device_passed = sum(1 for r in device_results if r.passed)
            device_avg_score = sum(r.score for r in device_results) / len(device_results) if device_results else 0

            total_tests += device_total
            total_passed += device_passed
            device_scores[device] = device_avg_score

            print(f"\n📱 {device.upper()}")
            print(f"   Páginas testadas: {device_total}")
            print(f"   Páginas aprovadas: {device_passed}")
            print(f"   Taxa de aprovação: {(device_passed/device_total*100):.1f}%")
            print(f"   Pontuação média: {device_avg_score:.1f}/100")

            # Listar páginas com problemas
            failed_pages = [r for r in device_results if not r.passed]
            if failed_pages:
                print(f"   ⚠️  Páginas com problemas:")
                for page in failed_pages:
                    print(f"     - {page.name} (Score: {page.score}/100)")

        # Resumo geral
        overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        overall_avg_score = sum(device_scores.values()) / len(device_scores) if device_scores else 0

        print(f"\n🎯 RESUMO GERAL")
        print(f"   Total de testes: {total_tests}")
        print(f"   Testes aprovados: {total_passed}")
        print(f"   Taxa geral de aprovação: {overall_pass_rate:.1f}%")
        print(f"   Pontuação média geral: {overall_avg_score:.1f}/100")

        # Classificação
        if overall_avg_score >= 90:
            classification = "🌟 EXCELENTE"
        elif overall_avg_score >= 80:
            classification = "✅ BOM"
        elif overall_avg_score >= 70:
            classification = "⚠️ REGULAR"
        else:
            classification = "❌ PRECISA MELHORAR"

        print(f"   Classificação: {classification}")

        # Recomendações
        print(f"\n💡 RECOMENDAÇÕES")
        if overall_avg_score < 90:
            print("   - Revisar páginas com pontuação baixa")
            print("   - Implementar melhorias de acessibilidade")
            print("   - Verificar touch targets em elementos interativos")
            print("   - Otimizar imagens para dispositivos móveis")
        else:
            print("   - Parabéns! O site está bem otimizado para mobile")
            print("   - Continue monitorando regularmente")

        return overall_avg_score >= 80

def main():
    """Função principal"""
    import argparse

    parser = argparse.ArgumentParser(description='Testa responsividade mobile do Symplifika')
    parser.add_argument('--url', default='http://localhost:8000', help='URL base do site')
    parser.add_argument('--json', action='store_true', help='Salvar resultados em JSON')

    args = parser.parse_args()

    checker = MobileResponsivenessChecker(args.url)

    try:
        # Testar se o servidor está rodando
        response = requests.get(args.url, timeout=5)
        if response.status_code not in [200, 302, 404]:  # 404 é ok, significa que o servidor está rodando
            print(f"❌ Erro: Servidor não está respondendo em {args.url}")
            sys.exit(1)
    except requests.RequestException:
        print(f"❌ Erro: Não foi possível conectar ao servidor em {args.url}")
        print("   Certifique-se de que o servidor Django está rodando")
        sys.exit(1)

    # Executar testes
    results = checker.run_tests()
    success = checker.generate_report(results)

    # Salvar em JSON se solicitado
    if args.json:
        json_results = {}
        for device, device_results in results.items():
            json_results[device] = [
                {
                    'url': r.url,
                    'name': r.name,
                    'passed': r.passed,
                    'issues': r.issues,
                    'score': r.score,
                    'device': r.device
                }
                for r in device_results
            ]

        with open('mobile_responsiveness_report.json', 'w', encoding='utf-8') as f:
            json.dump(json_results, f, indent=2, ensure_ascii=False)

        print(f"\n📄 Relatório salvo em: mobile_responsiveness_report.json")

    # Exit code baseado no resultado
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
