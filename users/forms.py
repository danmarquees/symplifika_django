from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    """Formulário para edição do perfil do usuário"""

    class Meta:
        model = UserProfile
        fields = [
            'theme', 'email_notifications', 'ai_enabled',
            'ai_model_preference'
        ]
        widgets = {
            'theme': forms.Select(attrs={
                'class': 'form-control'
            }),
            'ai_model_preference': forms.Select(attrs={
                'class': 'form-control'
            }),
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'ai_enabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'theme': 'Tema da Interface',
            'email_notifications': 'Receber notificações por email',
            'ai_enabled': 'Habilitar funcionalidades de IA',
            'ai_model_preference': 'Modelo de IA preferido',
        }
        help_texts = {
            'theme': 'Escolha o tema visual da aplicação',
            'ai_model_preference': 'Modelo de IA usado para expansão de texto',
        }


class UserUpdateForm(forms.ModelForm):
    """Formulário para atualização dos dados básicos do usuário"""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sobrenome'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemplo.com'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este email já está em uso.")
        return email


class CustomUserCreationForm(UserCreationForm):
    """Formulário customizado para registro de usuário"""

    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Sobrenome'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'email@exemplo.com'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome de usuário'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Senha'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirme a senha'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este email já está em uso.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class CustomPasswordChangeForm(PasswordChangeForm):
    """Formulário customizado para mudança de senha"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Senha atual'
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nova senha'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirme a nova senha'
        })


class PlanUpgradeForm(forms.Form):
    """Formulário para upgrade de plano"""

    PLAN_CHOICES = [
        ('premium', 'Premium - R$ 19,90/mês'),
        ('enterprise', 'Enterprise - R$ 49,90/mês'),
    ]

    plan = forms.ChoiceField(
        choices=PLAN_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label='Escolha seu plano'
    )

    payment_method = forms.ChoiceField(
        choices=[
            ('credit_card', 'Cartão de Crédito'),
            ('pix', 'PIX'),
            ('boleto', 'Boleto Bancário'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Método de pagamento',
        required=False
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        # Remove opções de plano baseado no plano atual
        current_plan = user.profile.plan
        if current_plan == 'premium':
            # Se já é premium, só pode fazer upgrade para enterprise
            self.fields['plan'].choices = [('enterprise', 'Enterprise - R$ 49,90/mês')]

    def clean_plan(self):
        plan = self.cleaned_data.get('plan')
        current_plan = self.user.profile.plan

        plan_hierarchy = ['free', 'premium', 'enterprise']
        current_index = plan_hierarchy.index(current_plan)
        new_index = plan_hierarchy.index(plan)

        if new_index <= current_index:
            raise forms.ValidationError(
                "Você só pode fazer upgrade para um plano superior."
            )

        return plan


class AccountDeleteForm(forms.Form):
    """Formulário para exclusão de conta"""

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua senha para confirmar'
        }),
        label='Senha atual'
    )

    confirmation = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'DELETE MY ACCOUNT'
        }),
        label='Confirmação',
        help_text='Digite exatamente: DELETE MY ACCOUNT'
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.user.check_password(password):
            raise forms.ValidationError("Senha incorreta.")
        return password

    def clean_confirmation(self):
        confirmation = self.cleaned_data.get('confirmation')
        expected = "DELETE MY ACCOUNT"
        if confirmation != expected:
            raise forms.ValidationError(f"Digite exatamente: {expected}")
        return confirmation
