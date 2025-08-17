from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile


class Command(BaseCommand):
    help = 'Cria um usuário administrador para o sistema Symplifika'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Username do administrador (padrão: admin)',
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@symplifika.com',
            help='Email do administrador',
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Senha do administrador (padrão: admin123)',
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        self.stdout.write(
            self.style.SUCCESS('🚀 Criando usuário administrador...')
        )

        # Verifica se já existe
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'❌ Usuário "{username}" já existe!')
            )
            return

        try:
            # Cria o superusuário
            admin_user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name='Admin',
                last_name='Symplifika'
            )

            # Atualiza o perfil para plano Enterprise
            profile = admin_user.profile
            profile.plan = 'enterprise'
            profile.max_shortcuts = -1  # Ilimitado
            profile.max_ai_requests = -1  # Ilimitado
            profile.ai_enabled = True
            profile.save()

            self.stdout.write(
                self.style.SUCCESS('✅ Administrador criado com sucesso!')
            )
            self.stdout.write(f'   👤 Username: {username}')
            self.stdout.write(f'   📧 Email: {email}')
            self.stdout.write(f'   🔑 Senha: {password}')
            self.stdout.write(f'   🎯 Plano: Enterprise (ilimitado)')
            self.stdout.write('')
            self.stdout.write(
                self.style.WARNING('⚠️  IMPORTANTE: Altere a senha após o primeiro login!')
            )
            self.stdout.write(
                self.style.SUCCESS('🌐 Acesse o admin em: http://localhost:8000/admin/')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao criar administrador: {e}')
            )
