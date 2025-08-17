from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from shortcuts.models import Category, Shortcut
from users.models import UserProfile


class Command(BaseCommand):
    help = 'Setup inicial do projeto Symplifika'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-superuser',
            action='store_true',
            help='Criar superusuário automaticamente',
        )
        parser.add_argument(
            '--admin-username',
            type=str,
            default='admin',
            help='Username do superusuário (padrão: admin)',
        )
        parser.add_argument(
            '--admin-email',
            type=str,
            default='admin@symplifika.com',
            help='Email do superusuário',
        )
        parser.add_argument(
            '--admin-password',
            type=str,
            default='admin123',
            help='Senha do superusuário (padrão: admin123)',
        )
        parser.add_argument(
            '--create-demo-data',
            action='store_true',
            help='Criar dados de demonstração',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando setup do projeto Symplifika...')
        )

        # Criar superusuário se solicitado
        if options['create_superuser']:
            self.create_superuser(options)

        # Criar dados de demonstração se solicitado
        if options['create_demo_data']:
            self.create_demo_data()

        self.stdout.write(
            self.style.SUCCESS('✅ Setup concluído com sucesso!')
        )
        self.stdout.write(
            self.style.WARNING('📝 Lembre-se de configurar as variáveis de ambiente no arquivo .env')
        )
        self.stdout.write(
            self.style.WARNING('🔑 Especialmente a OPENAI_API_KEY para funcionalidades de IA')
        )

    def create_superuser(self, options):
        username = options['admin_username']
        email = options['admin_email']
        password = options['admin_password']

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'Superusuário "{username}" já existe')
            )
            return

        try:
            superuser = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name='Admin',
                last_name='Symplifika'
            )

            # Atualizar perfil para plano Enterprise
            profile = superuser.profile
            profile.plan = 'enterprise'
            profile.max_shortcuts = -1  # Ilimitado
            profile.max_ai_requests = 10000
            profile.save()

            self.stdout.write(
                self.style.SUCCESS(f'✅ Superusuário criado: {username}')
            )
            self.stdout.write(f'   Email: {email}')
            self.stdout.write(f'   Senha: {password}')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao criar superusuário: {e}')
            )

    def create_demo_data(self):
        self.stdout.write('📊 Criando dados de demonstração...')

        try:
            # Criar usuário de demonstração
            demo_user, created = User.objects.get_or_create(
                username='demo',
                defaults={
                    'email': 'demo@symplifika.com',
                    'first_name': 'Usuário',
                    'last_name': 'Demo',
                    'is_active': True
                }
            )

            if created:
                demo_user.set_password('demo123')
                demo_user.save()
                self.stdout.write('   ✅ Usuário demo criado')

            # Criar categorias de exemplo
            categories_data = [
                {
                    'name': 'Emails',
                    'description': 'Templates de email profissionais',
                    'color': '#007bff'
                },
                {
                    'name': 'Respostas Rápidas',
                    'description': 'Respostas comuns para chat e suporte',
                    'color': '#28a745'
                },
                {
                    'name': 'Código',
                    'description': 'Snippets de código frequentemente usados',
                    'color': '#6f42c1'
                },
                {
                    'name': 'Assinaturas',
                    'description': 'Assinaturas para diferentes contextos',
                    'color': '#fd7e14'
                }
            ]

            created_categories = {}
            for cat_data in categories_data:
                category, created = Category.objects.get_or_create(
                    name=cat_data['name'],
                    user=demo_user,
                    defaults=cat_data
                )
                created_categories[cat_data['name']] = category
                if created:
                    self.stdout.write(f'   ✅ Categoria "{cat_data["name"]}" criada')

            # Criar atalhos de exemplo
            shortcuts_data = [
                {
                    'trigger': '//email-boasvindas',
                    'title': 'Email de Boas-vindas',
                    'content': 'Olá {nome},\n\nSeja muito bem-vindo(a) à nossa empresa!\n\nEstamos felizes em tê-lo(a) conosco.\n\nAtenciosamente,\nEquipe {empresa}',
                    'category': 'Emails',
                    'expansion_type': 'dynamic',
                    'variables': {'nome': 'João', 'empresa': 'Symplifika'}
                },
                {
                    'trigger': '//resposta-suporte',
                    'title': 'Resposta Padrão Suporte',
                    'content': 'Obrigado por entrar em contato conosco!\n\nRecebemos sua mensagem e nossa equipe irá analisá-la. Você receberá uma resposta em até 24 horas.\n\nSe for urgente, entre em contato pelo telefone (11) 99999-9999.',
                    'category': 'Respostas Rápidas',
                    'expansion_type': 'static'
                },
                {
                    'trigger': '//func-python',
                    'title': 'Função Python Básica',
                    'content': 'def {nome_funcao}():\n    """\n    Descrição da função\n    """\n    # Implementação aqui\n    pass',
                    'category': 'Código',
                    'expansion_type': 'dynamic',
                    'variables': {'nome_funcao': 'minha_funcao'}
                },
                {
                    'trigger': '//assinatura-formal',
                    'title': 'Assinatura Formal',
                    'content': 'Atenciosamente,\n\n{nome}\n{cargo}\n{empresa}\n{telefone}\n{email}',
                    'category': 'Assinaturas',
                    'expansion_type': 'dynamic',
                    'variables': {
                        'nome': 'Seu Nome',
                        'cargo': 'Seu Cargo',
                        'empresa': 'Sua Empresa',
                        'telefone': '(11) 99999-9999',
                        'email': 'seu@email.com'
                    }
                },
                {
                    'trigger': '//agradecimento',
                    'title': 'Agradecimento Profissional',
                    'content': 'Gostaria de expressar minha sincera gratidão pelo excelente trabalho realizado.',
                    'category': 'Respostas Rápidas',
                    'expansion_type': 'ai_enhanced',
                    'ai_prompt': 'Expanda este agradecimento de forma mais elaborada e profissional, mantendo um tom cordial e sincero.'
                },
                {
                    'trigger': '//reuniao-followup',
                    'title': 'Follow-up de Reunião',
                    'content': 'Obrigado pela reunião produtiva de hoje.',
                    'category': 'Emails',
                    'expansion_type': 'ai_enhanced',
                    'ai_prompt': 'Transforme em um email completo de follow-up de reunião, incluindo próximos passos e agradecimentos.'
                }
            ]

            for shortcut_data in shortcuts_data:
                category = created_categories.get(shortcut_data.pop('category'))
                shortcut_data['category'] = category
                shortcut_data['user'] = demo_user

                shortcut, created = Shortcut.objects.get_or_create(
                    trigger=shortcut_data['trigger'],
                    user=demo_user,
                    defaults=shortcut_data
                )

                if created:
                    self.stdout.write(f'   ✅ Atalho "{shortcut_data["trigger"]}" criado')

            self.stdout.write(
                self.style.SUCCESS('✅ Dados de demonstração criados com sucesso!')
            )
            self.stdout.write('📝 Usuário demo criado:')
            self.stdout.write('   Username: demo')
            self.stdout.write('   Senha: demo123')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao criar dados de demonstração: {e}')
            )
