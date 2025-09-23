from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Shortcut, ShortcutUsage, AIEnhancementLog
import logging

logger = logging.getLogger(__name__)


class CategorySerializer(serializers.ModelSerializer):
    shortcuts_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'color', 'shortcuts_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_shortcuts_count(self, obj):
        if hasattr(obj, 'shortcuts_count'):
            return obj.shortcuts_count
        return obj.shortcuts.filter(is_active=True).count()

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate_name(self, value):
        """Valida se o nome da categoria não existe para o usuário"""
        if not value or not value.strip():
            raise serializers.ValidationError("O nome da categoria é obrigatório.")

        value = value.strip()

        if len(value) < 2:
            raise serializers.ValidationError("O nome da categoria deve ter pelo menos 2 caracteres.")

        if len(value) > 100:
            raise serializers.ValidationError("O nome da categoria deve ter no máximo 100 caracteres.")

        user = self.context['request'].user

        # Para criação, verifica se já existe categoria com este nome
        if not self.instance and Category.objects.filter(user=user, name=value).exists():
            raise serializers.ValidationError("Já existe uma categoria com este nome.")

        # Para atualização, verifica se existe outra categoria com este nome
        if self.instance:
            existing = Category.objects.filter(user=user, name=value).exclude(id=self.instance.id)
            if existing.exists():
                raise serializers.ValidationError("Já existe uma categoria com este nome.")

        return value

    def validate_color(self, value):
        """Valida se a cor está em formato hexadecimal válido"""
        if not value:
            return "#007bff"  # Cor padrão

        if not value.startswith('#') or len(value) != 7:
            raise serializers.ValidationError("A cor deve estar no formato hexadecimal (#RRGGBB).")

        try:
            int(value[1:], 16)  # Verifica se é um valor hexadecimal válido
        except ValueError:
            raise serializers.ValidationError("A cor deve estar no formato hexadecimal válido (#RRGGBB).")

        return value


class ShortcutSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    usage_stats = serializers.SerializerMethodField()

    class Meta:
        model = Shortcut
        fields = [
            'id', 'trigger', 'title', 'content', 'expanded_content',
            'expansion_type', 'category', 'category_name', 'is_active',
            'use_count', 'last_used', 'ai_prompt', 'variables', 'url_context',
            'usage_stats', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'use_count', 'last_used', 'created_at', 'updated_at']

    def get_usage_stats(self, obj):
        return {
            'total_uses': obj.use_count,
            'last_used': obj.last_used,
            'avg_uses_per_week': self.calculate_avg_uses_per_week(obj)
        }

    def calculate_avg_uses_per_week(self, obj):
        from django.utils import timezone
        from datetime import timedelta

        if not obj.created_at:
            return 0

        days_since_creation = (timezone.now() - obj.created_at).days
        weeks_since_creation = max(days_since_creation / 7, 1)

        return round(obj.use_count / weeks_since_creation, 2)

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate_trigger(self, value):
        """Valida se o gatilho tem o formato correto"""
        if not value.startswith('//'):
            raise serializers.ValidationError("O gatilho deve começar com '//'")

        if len(value) < 4:
            raise serializers.ValidationError("O gatilho deve ter pelo menos 4 caracteres")

        # Verifica se não há caracteres especiais
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_//')
        if not set(value).issubset(allowed_chars):
            raise serializers.ValidationError("O gatilho contém caracteres inválidos")

        return value.lower()

    def validate_category(self, value):
        """Valida se a categoria pertence ao usuário"""
        if value and value.user != self.context['request'].user:
            raise serializers.ValidationError("Categoria não encontrada")
        return value

    def validate_url_context(self, value):
        """Valida o formato da URL de contexto"""
        if not value:
            return value

        # Remove protocolo se presente para validação mais flexível
        if value.startswith(('http://', 'https://')):
            # URL completa está OK
            return value
        elif '.' in value and not value.startswith(('/', '\\')):
            # Adiciona https:// se parece ser um domínio
            return f"https://{value}"
        else:
            raise serializers.ValidationError(
                "URL deve ser um domínio válido (ex: gmail.com) ou URL completa"
            )

        return value


class ShortcutCreateSerializer(ShortcutSerializer):
    """Serializer específico para criação de atalhos"""

    class Meta(ShortcutSerializer.Meta):
        fields = [
            'trigger', 'title', 'content', 'expansion_type',
            'category', 'ai_prompt', 'variables', 'url_context'
        ]

    def validate(self, attrs):
        user = self.context['request'].user

        # Verifica se o usuário pode criar mais atalhos
        if not user.profile.can_create_shortcut():
            raise serializers.ValidationError(
                f"Limite de {user.profile.max_shortcuts} atalhos atingido"
            )

        # Verifica se o gatilho já existe para este usuário
        trigger = attrs.get('trigger')
        if trigger and Shortcut.objects.filter(user=user, trigger=trigger).exists():
            raise serializers.ValidationError({"trigger": "Este gatilho já existe"})

        return attrs


class ShortcutUpdateSerializer(ShortcutSerializer):
    """Serializer específico para atualização de atalhos"""

    class Meta(ShortcutSerializer.Meta):
        fields = [
            'title', 'content', 'expansion_type', 'category',
            'is_active', 'ai_prompt', 'variables', 'url_context'
        ]


class ShortcutUsageSerializer(serializers.ModelSerializer):
    shortcut_trigger = serializers.CharField(source='shortcut.trigger', read_only=True)
    shortcut_title = serializers.CharField(source='shortcut.title', read_only=True)

    class Meta:
        model = ShortcutUsage
        fields = ['id', 'shortcut_trigger', 'shortcut_title', 'used_at', 'context']
        read_only_fields = ['id', 'used_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AIEnhancementLogSerializer(serializers.ModelSerializer):
    shortcut_trigger = serializers.CharField(source='shortcut.trigger', read_only=True)

    class Meta:
        model = AIEnhancementLog
        fields = [
            'id', 'shortcut_trigger', 'original_content', 'enhanced_content',
            'ai_model_used', 'processing_time', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ShortcutSearchSerializer(serializers.Serializer):
    """Serializer para busca de atalhos"""
    query = serializers.CharField(max_length=200, required=False)
    category = serializers.IntegerField(required=False)
    expansion_type = serializers.ChoiceField(
        choices=Shortcut.EXPANSION_TYPES,
        required=False
    )
    is_active = serializers.BooleanField(required=False, default=True)
    order_by = serializers.ChoiceField(
        choices=[
            'trigger', '-trigger',
            'title', '-title',
            'use_count', '-use_count',
            'last_used', '-last_used',
            'created_at', '-created_at'
        ],
        required=False,
        default='-last_used'
    )


class ShortcutStatsSerializer(serializers.Serializer):
    """Serializer para estatísticas dos atalhos"""
    total_shortcuts = serializers.IntegerField()
    active_shortcuts = serializers.IntegerField()
    total_uses = serializers.IntegerField()
    most_used_shortcut = ShortcutSerializer(read_only=True)
    recent_shortcuts = ShortcutSerializer(many=True, read_only=True)
    shortcuts_by_category = serializers.DictField()
    shortcuts_by_type = serializers.DictField()


class BulkShortcutActionSerializer(serializers.Serializer):
    """Serializer para ações em lote nos atalhos"""
    shortcut_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    action = serializers.ChoiceField(choices=[
        'activate', 'deactivate', 'delete', 'change_category'
    ])
    category_id = serializers.IntegerField(required=False)

    def validate(self, attrs):
        if attrs['action'] == 'change_category' and not attrs.get('category_id'):
            raise serializers.ValidationError(
                "category_id é obrigatório para a ação 'change_category'"
            )
        return attrs
