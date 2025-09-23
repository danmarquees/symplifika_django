from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q, Sum
from django.db import models
from users.models import UserProfile
from users.services import ReferralService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Processa bônus de indicação pendentes e verifica upgrades de plano'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa em modo de teste sem fazer alterações'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Número de dias para verificar upgrades recentes'
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='Processar apenas um usuário específico'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        days = options['days']
        user_id = options.get('user_id')

        if dry_run:
            self.stdout.write(
                self.style.WARNING('Executando em modo DRY RUN - Nenhuma alteração será feita')
            )

        # Data limite para verificar upgrades
        cutoff_date = timezone.now() - timezone.timedelta(days=days)

        # Filtrar usuários
        if user_id:
            users_query = User.objects.filter(id=user_id)
        else:
            # Buscar usuários que fizeram upgrade recentemente e foram indicados
            users_query = User.objects.filter(
                profile__referred_by__isnull=False,
                profile__plan__in=['premium', 'enterprise']
            ).exclude(
                profile__plan='free'
            )

        self.stdout.write(f'Verificando {users_query.count()} usuários...')

        processed = 0
        bonuses_awarded = 0
        total_bonus_amount = 0

        for user in users_query:
            try:
                profile = user.profile

                # Verificar se o usuário foi indicado
                if not profile.referred_by:
                    continue

                # Obter perfil do indicador
                referrer_profile = profile.referred_by.profile

                # Calcular bônus baseado no plano atual
                bonus_amount = ReferralService.calculate_referral_bonus(profile.plan)

                if bonus_amount <= 0:
                    continue

                # Verificar se este bônus já foi processado
                # (Idealmente você criaria uma tabela de log de bônus processados)
                # Por enquanto, vamos assumir que se o usuário tem plano pago
                # e o indicador não tem o bônus correspondente, precisa processar

                self.stdout.write(
                    f'Processando usuário {user.username} (indicado por {referrer_profile.user.username})'
                )
                self.stdout.write(f'  - Plano atual: {profile.plan}')
                self.stdout.write(f'  - Bônus calculado: R$ {bonus_amount:.2f}')

                if not dry_run:
                    # Processar o bônus
                    success = referrer_profile.process_referral_upgrade(user, bonus_amount)

                    if success:
                        bonuses_awarded += 1
                        total_bonus_amount += bonus_amount

                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  ✓ Bônus de R$ {bonus_amount:.2f} processado para {referrer_profile.user.username}'
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f'  ✗ Erro ao processar bônus')
                        )
                else:
                    self.stdout.write(
                        f'  [DRY RUN] Bônus de R$ {bonus_amount:.2f} seria processado'
                    )
                    bonuses_awarded += 1
                    total_bonus_amount += bonus_amount

                processed += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Erro ao processar usuário {user.username}: {e}')
                )
                logger.error(f'Erro ao processar bônus para usuário {user.username}: {e}')

        # Relatório final
        self.stdout.write('\n' + '='*50)
        self.stdout.write('RELATÓRIO FINAL')
        self.stdout.write('='*50)
        self.stdout.write(f'Usuários processados: {processed}')
        self.stdout.write(f'Bônus concedidos: {bonuses_awarded}')
        self.stdout.write(f'Valor total em bônus: R$ {total_bonus_amount:.2f}')

        if dry_run:
            self.stdout.write(
                self.style.WARNING('\nEste foi um DRY RUN - Nenhuma alteração foi feita')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\n✓ Processamento concluído com sucesso!')
            )

        # Estatísticas gerais do sistema
        self.show_referral_stats()

    def show_referral_stats(self):
        """Mostra estatísticas gerais do sistema de indicação"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('ESTATÍSTICAS DO SISTEMA')
        self.stdout.write('='*50)

        # Total de usuários com indicações
        users_with_referrals = UserProfile.objects.filter(total_referrals__gt=0).count()

        # Total de indicações
        total_referrals = UserProfile.objects.aggregate(
            total=Sum('total_referrals')
        )['total'] or 0

        # Total de upgrades
        total_upgrades = UserProfile.objects.aggregate(
            total=Sum('referral_plan_upgrades')
        )['total'] or 0

        # Total de bônus distribuído
        total_bonuses = UserProfile.objects.aggregate(
            total=Sum('referral_bonus_earned')
        )['total'] or 0

        # Taxa de conversão global
        conversion_rate = (total_upgrades / total_referrals * 100) if total_referrals > 0 else 0

        self.stdout.write(f'Usuários indicadores: {users_with_referrals}')
        self.stdout.write(f'Total de indicações: {total_referrals}')
        self.stdout.write(f'Total de upgrades: {total_upgrades}')
        self.stdout.write(f'Taxa de conversão: {conversion_rate:.1f}%')
        self.stdout.write(f'Total de bônus distribuído: R$ {total_bonuses:.2f}')

        # Top indicadores
        top_referrers = UserProfile.objects.filter(
            total_referrals__gt=0
        ).order_by('-total_referrals')[:5]

        if top_referrers:
            self.stdout.write('\nTOP 5 INDICADORES:')
            for i, profile in enumerate(top_referrers, 1):
                self.stdout.write(
                    f'{i}. {profile.user.username}: {profile.total_referrals} indicações, '
                    f'{profile.referral_plan_upgrades} upgrades, '
                    f'R$ {profile.referral_bonus_earned:.2f} em bônus'
                )
