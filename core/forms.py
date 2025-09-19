from django import forms
from django.contrib.auth.models import User
from users.models import UserProfile


class UserSettingsForm(forms.ModelForm):
    """Form for user settings and preferences"""
    
    # User fields
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-symplifika-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white',
            'placeholder': 'Seu nome'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-symplifika-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white',
            'placeholder': 'Seu sobrenome'
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-symplifika-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white',
            'placeholder': 'seu@email.com'
        })
    )
    
    # AI Model preference choices
    AI_MODEL_CHOICES = [
        ('gpt-3.5-turbo', 'GPT-3.5 Turbo'),
        ('gpt-4', 'GPT-4'),
        ('gpt-4-turbo', 'GPT-4 Turbo'),
        ('claude-3-haiku', 'Claude 3 Haiku'),
        ('claude-3-sonnet', 'Claude 3 Sonnet'),
    ]
    
    ai_model_preference = forms.ChoiceField(
        choices=AI_MODEL_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-symplifika-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'
        })
    )
    
    class Meta:
        model = UserProfile
        fields = ['theme', 'email_notifications', 'ai_enabled']
        widgets = {
            'theme': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-symplifika-primary bg-white dark:bg-gray-700 text-gray-900 dark:text-white'
            }),
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 dark:border-gray-600 text-symplifika-primary focus:ring-symplifika-primary'
            }),
            'ai_enabled': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 dark:border-gray-600 text-symplifika-primary focus:ring-symplifika-primary'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
            # Set initial value for ai_model_preference
            if hasattr(self.user, 'profile'):
                self.fields['ai_model_preference'].initial = self.user.profile.ai_model_preference
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        
        if self.user:
            # Update user fields
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']
            
            # Update ai_model_preference
            profile.ai_model_preference = self.cleaned_data['ai_model_preference']
            
            if commit:
                self.user.save()
                profile.save()
        
        return profile
