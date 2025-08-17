from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from shortcuts.models import Category, Shortcut
from users.models import UserProfile
from core.models import AppSettings, ActivityLog
import random


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de exemplo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=5,
            help='Número de usuários para criar'
        )
        parser.add_argument(
            '--shortcuts',
            type=int,
            default=20,
            help='Número de atalhos para criar'
        )

    def handle(self, *args, **options):
        self.stdout.write('Iniciando população do banco de dados...')

        # Criar configurações básicas
        self.create_app_settings()

        # Criar usuários de exemplo
        users = self.create_sample_users(options['users'])

        # Criar categorias e atalhos
        self.create_sample_shortcuts(users, options['shortcuts'])

        # Criar logs de atividade
        self.create_sample_activity_logs(users)

        self.stdout.write(
            self.style.SUCCESS('Dados de exemplo criados com sucesso!')
        )

    def create_app_settings(self):
        """Cria configurações básicas da aplicação"""
        settings = [
            {
                'key': 'app_name',
                'value': 'Symplifika',
                'description': 'Nome da aplicação'
            },
            {
                'key': 'app_version',
                'value': '1.0.0',
                'description': 'Versão da aplicação'
            },
            {
                'key': 'max_shortcuts_free',
                'value': '50',
                'description': 'Máximo de atalhos para usuários gratuitos'
            },
            {
                'key': 'max_shortcuts_premium',
                'value': '500',
                'description': 'Máximo de atalhos para usuários premium'
            },
            {
                'key': 'max_ai_requests_free',
                'value': '100',
                'description': 'Máximo de requisições IA para usuários gratuitos'
            },
            {
                'key': 'max_ai_requests_premium',
                'value': '1000',
                'description': 'Máximo de requisições IA para usuários premium'
            },
            {
                'key': 'maintenance_mode',
                'value': 'false',
                'description': 'Modo de manutenção ativo'
            }
        ]

        for setting in settings:
            AppSettings.set_setting(
                setting['key'],
                setting['value'],
                setting['description']
            )

        self.stdout.write('Configurações básicas criadas.')

    def create_sample_users(self, count):
        """Cria usuários de exemplo"""
        users = []

        # Criar superusuário admin se não existir
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@symplifika.com',
                password='admin123',
                first_name='Admin',
                last_name='System'
            )
            admin_user.profile.plan = 'enterprise'
            admin_user.profile.max_shortcuts = -1
            admin_user.profile.max_ai_requests = -1
            admin_user.profile.save()
            users.append(admin_user)
            self.stdout.write(f'Superusuário admin criado.')

        # Criar usuários de exemplo
        sample_users = [
            {
                'username': 'joao_silva',
                'email': 'joao@exemplo.com',
                'first_name': 'João',
                'last_name': 'Silva',
                'plan': 'premium'
            },
            {
                'username': 'maria_santos',
                'email': 'maria@exemplo.com',
                'first_name': 'Maria',
                'last_name': 'Santos',
                'plan': 'free'
            },
            {
                'username': 'pedro_oliveira',
                'email': 'pedro@exemplo.com',
                'first_name': 'Pedro',
                'last_name': 'Oliveira',
                'plan': 'enterprise'
            },
            {
                'username': 'ana_costa',
                'email': 'ana@exemplo.com',
                'first_name': 'Ana',
                'last_name': 'Costa',
                'plan': 'free'
            },
            {
                'username': 'carlos_ferreira',
                'email': 'carlos@exemplo.com',
                'first_name': 'Carlos',
                'last_name': 'Ferreira',
                'plan': 'premium'
            }
        ]

        for i, user_data in enumerate(sample_users[:count]):
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password='password123',
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name']
                )

                # Configurar perfil
                profile = user.profile
                profile.plan = user_data['plan']

                if profile.plan == 'premium':
                    profile.max_shortcuts = 500
                    profile.max_ai_requests = 1000
                elif profile.plan == 'enterprise':
                    profile.max_shortcuts = -1
                    profile.max_ai_requests = -1

                profile.save()
                users.append(user)

        self.stdout.write(f'{len(users)} usuários criados.')
        return users

    def create_sample_shortcuts(self, users, shortcut_count):
        """Cria categorias e atalhos de exemplo"""
        categories_data = [
            {'name': 'Email', 'description': 'Templates de email', 'color': '#007bff'},
            {'name': 'Atendimento', 'description': 'Respostas para atendimento', 'color': '#28a745'},
            {'name': 'Vendas', 'description': 'Textos para vendas', 'color': '#ffc107'},
            {'name': 'Programação', 'description': 'Snippets de código', 'color': '#6f42c1'},
            {'name': 'Reuniões', 'description': 'Templates para reuniões', 'color': '#fd7e14'},
        ]

        shortcuts_data = [
            {
                'trigger': '//email-boas-vindas',
                'title': 'Email de Boas-vindas',
                'content': 'Olá {nome},\n\nSeja bem-vindo(a) à nossa empresa! Estamos muito felizes em tê-lo(a) conosco.\n\nQualquer dúvida, estamos à disposição.\n\nAtenciosamente,\n{assinatura}',
                'category': 'Email',
                'expansion_type': 'static'
            },
            {
                'trigger': '//email-agradecimento',
                'title': 'Email de Agradecimento',
                'content': 'Olá {nome},\n\nGostaria de agradecer por {motivo}. Sua colaboração foi fundamental.\n\nMuito obrigado!\n\n{assinatura}',
                'category': 'Email',
                'expansion_type': 'static'
            },
            {
                'trigger': '//resp-suporte',
                'title': 'Resposta Padrão Suporte',
                'content': 'Olá! Obrigado por entrar em contato. Recebi sua mensagem e vou analisá-la. Retorno em até 24h com uma solução.',
                'category': 'Atendimento',
                'expansion_type': 'ai_enhanced',
                'ai_prompt': 'Torne esta resposta mais profissional e empática'
            },
            {
                'trigger': '//prop-comercial',
                'title': 'Proposta Comercial',
                'content': 'Prezado(a) {cliente},\n\nSegue nossa proposta para {produto/serviço}:\n\n- Valor: R$ {valor}\n- Prazo: {prazo}\n- Condições: {condições}\n\nAguardo retorno.',
                'category': 'Vendas',
                'expansion_type': 'dynamic',
                'variables': {'cliente': '', 'produto/serviço': '', 'valor': '', 'prazo': '', 'condições': ''}
            },
            {
                'trigger': '//func-python',
                'title': 'Função Python Básica',
                'content': 'def {nome_funcao}({parametros}):\n    """\n    {descricao}\n    """\n    # Implementação aqui\n    return resultado',
                'category': 'Programação',
                'expansion_type': 'dynamic',
                'variables': {'nome_funcao': 'minha_funcao', 'parametros': 'param1, param2', 'descricao': 'Descrição da função'}
            },
            {
                'trigger': '//ata-reuniao',
                'title': 'Ata de Reunião',
                'content': 'ATA DE REUNIÃO\n\nData: {data}\nParticipantes: {participantes}\n\nPautas discutidas:\n1. {pauta1}\n2. {pauta2}\n\nDecisões tomadas:\n- {decisao1}\n- {decisao2}\n\nPróximos passos:\n- {acao1}\n- {acao2}',
                'category': 'Reuniões',
                'expansion_type': 'dynamic',
                'variables': {'data': '', 'participantes': '', 'pauta1': '', 'pauta2': '', 'decisao1': '', 'decisao2': '', 'acao1': '', 'acao2': ''}
            },
            {
                'trigger': '//follow-up',
                'title': 'Follow-up Cliente',
                'content': 'Olá {nome},\n\nEspero que esteja bem. Gostaria de fazer um acompanhamento sobre nossa última conversa.\n\nTem alguma novidade sobre {assunto}?\n\nFico à disposição para esclarecer qualquer dúvida.',
                'category': 'Vendas',
                'expansion_type': 'ai_enhanced',
                'ai_prompt': 'Torne este follow-up mais persuasivo e personalizado'
            },
            {
                'trigger': '//desculpas-atraso',
                'title': 'Pedido de Desculpas por Atraso',
                'content': 'Prezado(a) {nome},\n\nPeço desculpas pelo atraso em {motivo}. Houve um imprevisto que causou este contratempo.\n\nJá estamos trabalhando para resolver e em breve terá uma solução.\n\nMais uma vez, minhas sinceras desculpas.',
                'category': 'Atendimento',
                'expansion_type': 'static'
            },
            {
                'trigger': '//query-sql',
                'title': 'Query SQL Básica',
                'content': 'SELECT {campos}\nFROM {tabela}\nWHERE {condicao}\nORDER BY {ordenacao};',
                'category': 'Programação',
                'expansion_type': 'dynamic',
                'variables': {'campos': '*', 'tabela': 'usuarios', 'condicao': 'ativo = 1', 'ordenacao': 'id DESC'}
            },
            {
                'trigger': '//convite-reuniao',
                'title': 'Convite para Reunião',
                'content': 'Olá {nome},\n\nGostaria de convidá-lo(a) para uma reunião sobre {assunto}.\n\nData: {data}\nHorário: {horario}\nLocal: {local}\n\nPor favor, confirme sua presença.\n\nObrigado!',
                'category': 'Reuniões',
                'expansion_type': 'dynamic',
                'variables': {'nome': '', 'assunto': '', 'data': '', 'horario': '', 'local': ''}
            }
        ]

        total_created = 0

        for user in users:
            # Criar categorias para o usuário
            user_categories = {}
            for cat_data in categories_data:
                category, created = Category.objects.get_or_create(
                    name=cat_data['name'],
                    user=user,
                    defaults={
                        'description': cat_data['description'],
                        'color': cat_data['color']
                    }
                )
                user_categories[cat_data['name']] = category

            # Criar atalhos para o usuário
            shortcuts_per_user = min(shortcut_count // len(users), len(shortcuts_data))
            selected_shortcuts = random.sample(shortcuts_data, shortcuts_per_user)

            for shortcut_data in selected_shortcuts:
                category = user_categories.get(shortcut_data['category'])

                shortcut, created = Shortcut.objects.get_or_create(
                    trigger=shortcut_data['trigger'],
                    user=user,
                    defaults={
                        'title': shortcut_data['title'],
                        'content': shortcut_data['content'],
                        'category': category,
                        'expansion_type': shortcut_data['expansion_type'],
                        'ai_prompt': shortcut_data.get('ai_prompt', ''),
                        'variables': shortcut_data.get('variables', {}),
                        'use_count': random.randint(0, 50),
                        'last_used': timezone.now() - timezone.timedelta(days=random.randint(1, 30))
                    }
                )

                if created:
                    total_created += 1

        self.stdout.write(f'{total_created} atalhos criados.')

    def create_sample_activity_logs(self, users):
        """Cria logs de atividade de exemplo"""
        actions = ['login', 'shortcut_created', 'shortcut_used', 'ai_enhancement', 'profile_updated']

        total_logs = 0
        for user in users:
            # Criar alguns logs para cada usuário
            for _ in range(random.randint(5, 15)):
                action = random.choice(actions)

                ActivityLog.log_activity(
                    user=user,
                    action=action,
                    description=f'Ação {action} executada pelo usuário',
                    metadata={'sample': True}
                )
                total_logs += 1

        self.stdout.write(f'{total_logs} logs de atividade criados.')
