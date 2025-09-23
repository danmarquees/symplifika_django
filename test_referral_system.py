#!/usr/bin/env python
"""
Script de teste para o sistema de indicação do Symplifika

Este script testa todas as funcionalidades do sistema de indicação,
incluindo criação de códigos, registro com indicação, e processamento de bônus.

Uso:
    python test_referral_system.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'symplifika.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import TestCase
from users.models import UserProfile
from users.services import ReferralService
from payments.services import StripeService
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReferralSystemTest:
    """Classe de teste para o sistema de indicação"""

    def __init__(self):
        self.test_users = []
        self.cleanup_users = []

    def setup_test_data(self):
        """Configura dados de teste"""
        logger.info("🔧 Configurando dados de teste...")

        # Limpar usuários de teste existentes primeiro
        self.cleanup_existing_test_users()

        # Criar usuário indicador
        try:
            import time
            timestamp = int(time.time())

            self.referrer = User.objects.create_user(
                username=f'referrer_test_{timestamp}',
                email=f'referrer_{timestamp}@test.com',
                password='test123'
            )
            self.cleanup_users.append(self.referrer)
            logger.info(f"✅ Usuário indicador criado: {self.referrer.username}")

            # Garantir que o perfil existe e tem código
            profile, created = UserProfile.objects.get_or_create(user=self.referrer)
            if not profile.referral_code:
                profile.generate_referral_code()

            self.referral_code = profile.referral_code
            logger.info(f"✅ Código de indicação: {self.referral_code}")

        except Exception as e:
            logger.error(f"❌ Erro ao criar usuário indicador: {e}")
            return False

        return True

    def test_referral_code_generation(self):
        """Testa geração de códigos de indicação"""
        logger.info("🧪 Testando geração de códigos de indicação...")

        try:
            import time
            timestamp = int(time.time())

            # Criar usuário sem código
            user = User.objects.create_user(
                username=f'test_user_code_{timestamp}',
                email=f'testcode_{timestamp}@test.com',
                password='test123'
            )
            self.cleanup_users.append(user)

            profile = user.profile

            # Verificar se código foi gerado automaticamente
            if profile.referral_code:
                logger.info(f"✅ Código gerado automaticamente: {profile.referral_code}")
            else:
                # Gerar manualmente
                code = profile.generate_referral_code()
                logger.info(f"✅ Código gerado manualmente: {code}")

            # Verificar unicidade
            duplicate_count = UserProfile.objects.filter(
                referral_code=profile.referral_code
            ).count()

            if duplicate_count == 1:
                logger.info("✅ Código é único")
                return True
            else:
                logger.error(f"❌ Código duplicado encontrado: {duplicate_count} ocorrências")
                return False

        except Exception as e:
            logger.error(f"❌ Erro no teste de geração de códigos: {e}")
            return False

    def test_referral_creation(self):
        """Testa criação de indicação"""
        logger.info("🧪 Testando criação de indicação...")

        try:
            import time
            timestamp = int(time.time())

            # Criar usuário para ser indicado
            referred_user = User.objects.create_user(
                username=f'referred_test_{timestamp}',
                email=f'referred_{timestamp}@test.com',
                password='test123'
            )
            self.cleanup_users.append(referred_user)

            # Criar indicação
            result = ReferralService.create_referral_by_code(
                referred_user,
                self.referral_code
            )

            if result['success']:
                logger.info(f"✅ Indicação criada: {result['message']}")

                # Verificar se foi salvo corretamente
                referred_user.refresh_from_db()
                if referred_user.profile.referred_by == self.referrer:
                    logger.info("✅ Relação de indicação salva corretamente")

                    # Verificar contador do indicador
                    self.referrer.profile.refresh_from_db()
                    if self.referrer.profile.total_referrals >= 1:
                        logger.info(f"✅ Contador atualizado: {self.referrer.profile.total_referrals} indicações")
                        return True
                    else:
                        logger.error("❌ Contador não foi atualizado")
                        return False
                else:
                    logger.error("❌ Relação não foi salva")
                    return False
            else:
                logger.error(f"❌ Falha na criação: {result['error']}")
                return False

        except Exception as e:
            logger.error(f"❌ Erro no teste de criação de indicação: {e}")
            return False

    def test_referral_bonus_calculation(self):
        """Testa cálculo de bônus de indicação"""
        logger.info("🧪 Testando cálculo de bônus...")

        try:
            # Testar valores de bônus
            premium_bonus = ReferralService.calculate_referral_bonus('premium')
            enterprise_bonus = ReferralService.calculate_referral_bonus('enterprise')
            free_bonus = ReferralService.calculate_referral_bonus('free')

            logger.info(f"✅ Bônus Premium: R$ {premium_bonus:.2f}")
            logger.info(f"✅ Bônus Enterprise: R$ {enterprise_bonus:.2f}")
            logger.info(f"✅ Bônus Gratuito: R$ {free_bonus:.2f}")

            # Verificar valores esperados
            if premium_bonus == 10.00 and enterprise_bonus == 25.00 and free_bonus == 0.00:
                logger.info("✅ Valores de bônus corretos")
                return True
            else:
                logger.error("❌ Valores de bônus incorretos")
                return False

        except Exception as e:
            logger.error(f"❌ Erro no teste de cálculo de bônus: {e}")
            return False

    def test_referral_upgrade_bonus(self):
        """Testa processamento de bônus no upgrade"""
        logger.info("🧪 Testando bônus no upgrade de plano...")

        try:
            import time
            timestamp = int(time.time())

            # Criar usuário indicado
            referred_user = User.objects.create_user(
                username=f'upgrade_test_{timestamp}',
                email=f'upgrade_{timestamp}@test.com',
                password='test123'
            )
            self.cleanup_users.append(referred_user)

            # Criar indicação
            ReferralService.create_referral_by_code(referred_user, self.referral_code)

            # Simular upgrade para premium
            referred_profile = referred_user.profile
            old_bonus = self.referrer.profile.referral_bonus_earned

            # Processar bônus manualmente
            success = self.referrer.profile.process_referral_upgrade(
                referred_user,
                10.00  # Bônus Premium
            )

            if success:
                self.referrer.profile.refresh_from_db()
                new_bonus = self.referrer.profile.referral_bonus_earned

                if new_bonus == old_bonus + 10.00:
                    logger.info(f"✅ Bônus processado: R$ {new_bonus:.2f}")

                    # Verificar contador de upgrades
                    if self.referrer.profile.referral_plan_upgrades >= 1:
                        logger.info(f"✅ Contador de upgrades: {self.referrer.profile.referral_plan_upgrades}")
                        return True
                    else:
                        logger.error("❌ Contador de upgrades não atualizado")
                        return False
                else:
                    logger.error(f"❌ Bônus incorreto: esperado {old_bonus + 10.00}, recebido {new_bonus}")
                    return False
            else:
                logger.error("❌ Falha no processamento do bônus")
                return False

        except Exception as e:
            logger.error(f"❌ Erro no teste de bônus de upgrade: {e}")
            return False

    def test_dashboard_data(self):
        """Testa dados do dashboard"""
        logger.info("🧪 Testando dados do dashboard...")

        try:
            result = ReferralService.get_referral_dashboard_data(self.referrer)

            if result['success']:
                data = result['data']
                logger.info("✅ Dashboard carregado com sucesso")
                logger.info(f"   - Código: {data.get('referral_code')}")
                logger.info(f"   - Total indicações: {data['stats']['total_referrals']}")
                logger.info(f"   - Upgrades: {data['stats']['plan_upgrades']}")
                logger.info(f"   - Bônus ganho: R$ {data['stats']['bonus_earned']:.2f}")
                logger.info(f"   - Taxa conversão: {data['stats']['conversion_rate']:.1f}%")
                logger.info(f"   - Usuários indicados: {len(data['referred_users'])}")
                return True
            else:
                logger.error(f"❌ Erro no dashboard: {result['error']}")
                return False

        except Exception as e:
            logger.error(f"❌ Erro no teste do dashboard: {e}")
            return False

    def test_leaderboard(self):
        """Testa ranking de indicadores"""
        logger.info("🧪 Testando ranking de indicadores...")

        try:
            result = ReferralService.get_referral_leaderboard(limit=5)

            if result['success']:
                leaderboard = result['data']
                logger.info(f"✅ Ranking carregado: {len(leaderboard)} usuários")

                for i, user_data in enumerate(leaderboard[:3], 1):
                    logger.info(f"   {i}. {user_data['user']}: {user_data['total_referrals']} indicações")

                return True
            else:
                logger.error(f"❌ Erro no ranking: {result['error']}")
                return False

        except Exception as e:
            logger.error(f"❌ Erro no teste do ranking: {e}")
            return False

    def test_edge_cases(self):
        """Testa casos extremos"""
        logger.info("🧪 Testando casos extremos...")

        try:
            import time
            timestamp = int(time.time())

            # Testar código inválido
            invalid_user = User.objects.create_user(
                username=f'invalid_test_{timestamp}',
                email=f'invalid_{timestamp}@test.com',
                password='test123'
            )
            self.cleanup_users.append(invalid_user)

            result = ReferralService.create_referral_by_code(invalid_user, "INVALID_CODE")

            if not result['success']:
                logger.info("✅ Código inválido rejeitado corretamente")
            else:
                logger.error("❌ Código inválido foi aceito")
                return False

            # Testar auto-indicação
            result = ReferralService.create_referral_by_code(
                self.referrer,
                self.referral_code
            )

            if not result['success'] and 'próprio código' in result['error']:
                logger.info("✅ Auto-indicação rejeitada corretamente")
            else:
                logger.error("❌ Auto-indicação foi aceita")
                return False

            # Testar indicação dupla
            double_user = User.objects.create_user(
                username=f'double_test_{timestamp}',
                email=f'double_{timestamp}@test.com',
                password='test123'
            )
            self.cleanup_users.append(double_user)

            # Primeira indicação
            ReferralService.create_referral_by_code(double_user, self.referral_code)

            # Segunda indicação (deve falhar)
            result = ReferralService.create_referral_by_code(double_user, self.referral_code)

            if not result['success'] and 'já foi indicado' in result['error']:
                logger.info("✅ Indicação dupla rejeitada corretamente")
                return True
            else:
                logger.error("❌ Indicação dupla foi aceita")
                return False

        except Exception as e:
            logger.error(f"❌ Erro nos testes de casos extremos: {e}")
            return False

    def cleanup_existing_test_users(self):
        """Limpa usuários de teste existentes"""
        try:
            test_users = User.objects.filter(username__contains='_test')
            count = test_users.count()
            if count > 0:
                test_users.delete()
                logger.info(f"🧹 Removidos {count} usuários de teste existentes")
        except Exception as e:
            logger.warning(f"⚠️ Erro na limpeza prévia: {e}")

    def cleanup(self):
        """Limpa dados de teste"""
        logger.info("🧹 Limpando dados de teste...")

        try:
            for user in self.cleanup_users:
                try:
                    user.delete()
                    logger.info(f"✅ Usuário removido: {user.username}")
                except Exception as e:
                    logger.warning(f"⚠️  Erro ao remover {user.username}: {e}")

            logger.info("✅ Limpeza concluída")

        except Exception as e:
            logger.error(f"❌ Erro na limpeza: {e}")

    def run_all_tests(self):
        """Executa todos os testes"""
        logger.info("🚀 Iniciando testes do sistema de indicação...")
        logger.info("=" * 60)

        tests = [
            ("Setup de dados", self.setup_test_data),
            ("Geração de códigos", self.test_referral_code_generation),
            ("Criação de indicação", self.test_referral_creation),
            ("Cálculo de bônus", self.test_referral_bonus_calculation),
            ("Bônus no upgrade", self.test_referral_upgrade_bonus),
            ("Dados do dashboard", self.test_dashboard_data),
            ("Ranking", self.test_leaderboard),
            ("Casos extremos", self.test_edge_cases),
        ]

        passed = 0
        failed = 0

        for test_name, test_func in tests:
            logger.info(f"\n📋 {test_name}...")
            try:
                if test_func():
                    logger.info(f"✅ {test_name}: PASSOU")
                    passed += 1
                else:
                    logger.error(f"❌ {test_name}: FALHOU")
                    failed += 1
            except Exception as e:
                logger.error(f"💥 {test_name}: ERRO - {e}")
                failed += 1

        # Relatório final
        logger.info("\n" + "=" * 60)
        logger.info("📊 RELATÓRIO FINAL")
        logger.info("=" * 60)
        logger.info(f"✅ Testes aprovados: {passed}")
        logger.info(f"❌ Testes falharam: {failed}")
        logger.info(f"📈 Taxa de sucesso: {(passed / (passed + failed)) * 100:.1f}%")

        if failed == 0:
            logger.info("🎉 TODOS OS TESTES PASSARAM!")
        else:
            logger.warning(f"⚠️  {failed} TESTE(S) FALHARAM")

        # Limpeza
        self.cleanup()

        return failed == 0

def main():
    """Função principal"""
    print("🔥 Sistema de Indicação - Symplifika")
    print("🧪 Bateria de Testes Completa")
    print("=" * 60)

    # Verificar se estamos em ambiente de desenvolvimento
    from django.conf import settings
    if not settings.DEBUG:
        print("⚠️  AVISO: Este script deve ser executado apenas em ambiente de desenvolvimento!")
        response = input("Continuar mesmo assim? (s/N): ")
        if response.lower() != 's':
            print("❌ Execução cancelada")
            return

    # Executar testes
    test_runner = ReferralSystemTest()
    success = test_runner.run_all_tests()

    # Status de saída
    if success:
        print("\n🎊 Sistema de indicação funcionando perfeitamente!")
        sys.exit(0)
    else:
        print("\n💥 Problemas encontrados no sistema de indicação!")
        sys.exit(1)

if __name__ == "__main__":
    main()
