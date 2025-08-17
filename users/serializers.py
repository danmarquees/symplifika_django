from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    shortcuts_count = serializers.SerializerMethodField()
    ai_requests_remaining = serializers.SerializerMethodField()
    plan_display = serializers.CharField(source='get_plan_display', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'plan', 'plan_display', 'max_shortcuts', 'ai_enabled',
            'ai_model_preference', 'ai_requests_used', 'max_ai_requests',
            'theme', 'email_notifications', 'total_shortcuts_used',
            'time_saved_minutes', 'shortcuts_count', 'ai_requests_remaining',
            'created_at', 'updated_at', 'last_login'
        ]
        read_only_fields = [
            'ai_requests_used', 'total_shortcuts_used', 'time_saved_minutes',
            'shortcuts_count', 'ai_requests_remaining', 'created_at',
            'updated_at', 'last_login'
        ]

    def get_shortcuts_count(self, obj):
        return obj.user.shortcuts.filter(is_active=True).count()

    def get_ai_requests_remaining(self, obj):
        return max(0, obj.max_ai_requests - obj.ai_requests_used)


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'date_joined', 'password', 'password_confirm', 'profile'
        ]
        read_only_fields = ['id', 'date_joined', 'is_active']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def validate_email(self, value):
        """Valida se o email é único"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email já está em uso.")
        return value

    def validate_username(self, value):
        """Valida se o username é único"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nome de usuário já está em uso.")
        return value

    def validate(self, attrs):
        """Valida se as senhas coincidem"""
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')

        if password != password_confirm:
            raise serializers.ValidationError(
                {"password_confirm": "As senhas não coincidem."}
            )

        # Valida a força da senha
        try:
            validate_password(password)
        except Exception as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return attrs

    def create(self, validated_data):
        """Cria um novo usuário"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualização de dados do usuário"""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def validate_email(self, value):
        """Valida se o email é único (exceto para o usuário atual)"""
        user = self.instance
        if User.objects.filter(email=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("Este email já está em uso.")
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer para mudança de senha"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password_confirm = serializers.CharField(required=True)

    def validate_old_password(self, value):
        """Valida se a senha atual está correta"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Senha atual incorreta.")
        return value

    def validate(self, attrs):
        """Valida se as novas senhas coincidem"""
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')

        if new_password != new_password_confirm:
            raise serializers.ValidationError(
                {"new_password_confirm": "As senhas não coincidem."}
            )

        # Valida a força da nova senha
        try:
            validate_password(new_password)
        except Exception as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})

        return attrs

    def save(self):
        """Salva a nova senha"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer para login"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            # Permite login com email ou username
            if '@' in username:
                try:
                    user = User.objects.get(email=username)
                    username = user.username
                except User.DoesNotExist:
                    raise serializers.ValidationError("Credenciais inválidas.")

            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )

            if not user:
                raise serializers.ValidationError("Credenciais inválidas.")

            if not user.is_active:
                raise serializers.ValidationError("Conta desativada.")

            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError("Username/email e senha são obrigatórios.")


class UserStatsSerializer(serializers.Serializer):
    """Serializer para estatísticas do usuário"""
    total_shortcuts = serializers.IntegerField()
    active_shortcuts = serializers.IntegerField()
    total_uses = serializers.IntegerField()
    ai_requests_used = serializers.IntegerField()
    ai_requests_remaining = serializers.IntegerField()
    time_saved_minutes = serializers.IntegerField()
    time_saved_hours = serializers.FloatField()
    most_used_shortcuts = serializers.ListField()
    usage_by_month = serializers.DictField()
    shortcuts_by_category = serializers.DictField()


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer para solicitação de reset de senha"""
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Valida se o email existe"""
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Email não encontrado.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer para confirmação de reset de senha"""
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        """Valida se as senhas coincidem"""
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')

        if new_password != new_password_confirm:
            raise serializers.ValidationError(
                {"new_password_confirm": "As senhas não coincidem."}
            )

        # Valida a força da nova senha
        try:
            validate_password(new_password)
        except Exception as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})

        return attrs


class AccountDeleteSerializer(serializers.Serializer):
    """Serializer para exclusão de conta"""
    password = serializers.CharField(required=True, write_only=True)
    confirmation = serializers.CharField(required=True)

    def validate_password(self, value):
        """Valida se a senha está correta"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Senha incorreta.")
        return value

    def validate_confirmation(self, value):
        """Valida se a confirmação está correta"""
        expected = "DELETE MY ACCOUNT"
        if value != expected:
            raise serializers.ValidationError(
                f"Digite exatamente: {expected}"
            )
        return value


class PlanUpgradeSerializer(serializers.Serializer):
    """Serializer para upgrade de plano"""
    plan = serializers.ChoiceField(
        choices=UserProfile.PLAN_CHOICES,
        required=True
    )
    payment_method = serializers.CharField(required=False)

    def validate_plan(self, value):
        """Valida se o plano é válido para upgrade"""
        current_plan = self.context['request'].user.profile.plan

        plan_hierarchy = ['free', 'premium', 'enterprise']
        current_index = plan_hierarchy.index(current_plan)
        new_index = plan_hierarchy.index(value)

        if new_index <= current_index:
            raise serializers.ValidationError(
                "Você só pode fazer upgrade para um plano superior."
            )

        return value
