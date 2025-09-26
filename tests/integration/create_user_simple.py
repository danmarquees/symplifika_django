import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'symplifika.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile
from shortcuts.models import Category, Shortcut

# Criar usuário
try:
    user = User.objects.get(username='test')
    print("Usuário 'test' já existe")
except User.DoesNotExist:
    user = User.objects.create_user(
        username='test',
        email='test@test.com',
        password='test123',
        first_name='Test',
        last_name='User'
    )
    print("Usuário 'test' criado")

# Criar perfil
profile, created = UserProfile.objects.get_or_create(user=user)
if created:
    print("Perfil criado")

# Criar categoria
category, created = Category.objects.get_or_create(
    name='Teste',
    user=user,
    defaults={'description': 'Categoria de teste', 'color': '#10b981'}
)

# Criar atalhos
shortcuts_data = [
    {'trigger': '!oi', 'title': 'Saudação', 'content': 'Olá! Como posso ajudá-lo?'},
    {'trigger': '!email', 'title': 'Email', 'content': 'Prezado(a),\n\nEspero que esteja bem.\n\nAtenciosamente,\n{{user.name}}'},
    {'trigger': '!ass', 'title': 'Assinatura', 'content': 'Atenciosamente,\n{{user.name}}\n{{user.email}}'}
]

for data in shortcuts_data:
    shortcut, created = Shortcut.objects.get_or_create(
        trigger=data['trigger'],
        user=user,
        defaults={
            'title': data['title'],
            'content': data['content'],
            'category': category,
            'is_active': True
        }
    )
    if created:
        print(f"Atalho {data['trigger']} criado")

print(f"\nUsuário: test")
print(f"Senha: test123")
print(f"Atalhos: {Shortcut.objects.filter(user=user).count()}")
