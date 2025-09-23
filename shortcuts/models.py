from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    """Categoria para organizar os atalhos"""
    name = models.CharField(max_length=100, verbose_name="Nome")
    description = models.TextField(blank=True, verbose_name="Descrição")
    color = models.CharField(max_length=7, default="#007bff", verbose_name="Cor")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['name']
        unique_together = ['user', 'name']

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class Shortcut(models.Model):
    """Modelo principal para os atalhos de texto"""

    EXPANSION_TYPES = [
        ('static', 'Texto Estático'),
        ('ai_enhanced', 'Expandido com IA'),
        ('dynamic', 'Dinâmico com Variáveis'),
    ]

    trigger = models.CharField(
        max_length=50,
        verbose_name="Gatilho",
        help_text="Ex: //email-boasvindas"
    )
    title = models.CharField(max_length=200, verbose_name="Título")
    content = models.TextField(verbose_name="Conteúdo")
    expanded_content = models.TextField(
        blank=True,
        verbose_name="Conteúdo Expandido",
        help_text="Conteúdo processado pela IA"
    )

    expansion_type = models.CharField(
        max_length=20,
        choices=EXPANSION_TYPES,
        default='static',
        verbose_name="Tipo de Expansão"
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shortcuts",
        verbose_name="Categoria"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shortcuts",
        verbose_name="Usuário"
    )

    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    use_count = models.PositiveIntegerField(default=0, verbose_name="Contador de Uso")
    last_used = models.DateTimeField(null=True, blank=True, verbose_name="Último Uso")

    # AI Enhancement settings
    ai_prompt = models.TextField(
        blank=True,
        verbose_name="Prompt para IA",
        help_text="Instruções específicas para a IA expandir este conteúdo"
    )

    # Variables for dynamic content
    variables = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Variáveis",
        help_text="Variáveis dinâmicas no formato JSON"
    )

    # URL context for better trigger suggestions
    url_context = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="URL de Contexto",
        help_text="URL do site/serviço onde este atalho é mais útil (ex: gmail.com, linkedin.com)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Atalho"
        verbose_name_plural = "Atalhos"
        ordering = ['-last_used', '-use_count', 'trigger']
        unique_together = ['user', 'trigger']

    def __str__(self):
        return f"{self.trigger} - {self.title}"

    def increment_usage(self):
        """Incrementa o contador de uso e atualiza último uso"""
        self.use_count += 1
        self.last_used = timezone.now()
        self.save(update_fields=['use_count', 'last_used'])

    def get_processed_content(self):
        """Retorna o conteúdo processado baseado no tipo de expansão"""
        if self.expansion_type == 'ai_enhanced' and self.expanded_content:
            return self.expanded_content
        elif self.expansion_type == 'dynamic':
            # Aqui seria implementada a lógica de substituição de variáveis
            return self.process_dynamic_content()
        else:
            return self.content

    def process_dynamic_content(self):
        """Processa conteúdo dinâmico substituindo variáveis"""
        content = self.content
        for key, value in self.variables.items():
            placeholder = f"{{{key}}}"
            content = content.replace(placeholder, str(value))
        return content


class ShortcutUsage(models.Model):
    """Modelo para rastrear o histórico de uso dos atalhos"""
    shortcut = models.ForeignKey(
        Shortcut,
        on_delete=models.CASCADE,
        related_name="usage_history"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)
    context = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Contexto",
        help_text="Onde o atalho foi usado (app, página, etc.)"
    )

    class Meta:
        verbose_name = "Uso de Atalho"
        verbose_name_plural = "Usos de Atalhos"
        ordering = ['-used_at']

    def __str__(self):
        return f"{self.shortcut.trigger} usado em {self.used_at}"


class AIEnhancementLog(models.Model):
    """Log das expansões feitas pela IA"""
    shortcut = models.ForeignKey(
        Shortcut,
        on_delete=models.CASCADE,
        related_name="ai_logs"
    )
    original_content = models.TextField(verbose_name="Conteúdo Original")
    enhanced_content = models.TextField(verbose_name="Conteúdo Expandido")
    ai_model_used = models.CharField(max_length=100, verbose_name="Modelo IA Usado")
    processing_time = models.FloatField(verbose_name="Tempo de Processamento (s)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Log de Expansão IA"
        verbose_name_plural = "Logs de Expansões IA"
        ordering = ['-created_at']

    def __str__(self):
        return f"IA Log para {self.shortcut.trigger} em {self.created_at}"
