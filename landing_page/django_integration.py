"""
Django Integration for Symplifika Landing Page
==============================================

Este arquivo demonstra como integrar a landing page com o backend Django,
incluindo views, models e APIs para captura de leads da lista de espera.

Para usar este código:
1. Copie as classes necessárias para seu projeto Django
2. Configure as URLs correspondentes
3. Execute as migrações
4. Configure as variáveis de ambiente necessárias
"""

from django.db import models
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.views.generic import TemplateView
from django.conf import settings
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import re

# Configure logging
logger = logging.getLogger(__name__)

# =============================================================================
# MODELS
# =============================================================================


class WaitlistSubscriber(models.Model):
    """Model para armazenar assinantes da lista de espera"""

    ROLE_CHOICES = [
        ("marketing", "Marketing"),
        ("vendas", "Vendas"),
        ("atendimento", "Atendimento ao Cliente"),
        ("rh", "Recursos Humanos"),
        ("desenvolvedor", "Desenvolvimento"),
        ("design", "Design"),
        ("gestao", "Gestão/Liderança"),
        ("freelancer", "Freelancer"),
        ("estudante", "Estudante"),
        ("outro", "Outro"),
    ]

    # Campos principais
    name = models.CharField(max_length=100, verbose_name="Nome completo")
    email = models.EmailField(unique=True, verbose_name="Email")
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, verbose_name="Área de atuação"
    )

    # Dados de tracking
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    utm_source = models.CharField(max_length=100, blank=True)
    utm_medium = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=100, blank=True)

    # Localização (opcional)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    timezone = models.CharField(max_length=50, blank=True)

    # Status e controle
    is_active = models.BooleanField(default=True)
    is_early_access_sent = models.BooleanField(default=False)
    is_beta_invited = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    early_access_sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "waitlist_subscribers"
        verbose_name = "Assinante da Lista de Espera"
        verbose_name_plural = "Assinantes da Lista de Espera"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["role"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.email})"

    def clean(self):
        """Validação customizada"""
        super().clean()

        # Validar email
        try:
            EmailValidator()(self.email)
        except ValidationError:
            raise ValidationError({"email": "Email deve ter um formato válido"})

        # Validar nome
        if len(self.name.strip()) < 2:
            raise ValidationError({"name": "Nome deve ter pelo menos 2 caracteres"})

    def save(self, *args, **kwargs):
        """Override do save para limpeza de dados"""
        self.name = self.name.strip()
        self.email = self.email.lower().strip()
        super().save(*args, **kwargs)

    @property
    def is_recent(self):
        """Verifica se o cadastro foi feito nas últimas 24h"""
        return self.created_at > timezone.now() - timedelta(days=1)

    @property
    def role_display(self):
        """Retorna o display name da área de atuação"""
        return dict(self.ROLE_CHOICES).get(self.role, self.role)


class LandingPageAnalytics(models.Model):
    """Model para tracking de eventos da landing page"""

    EVENT_TYPES = [
        ("page_view", "Page View"),
        ("form_start", "Form Start"),
        ("form_submit", "Form Submit"),
        ("form_success", "Form Success"),
        ("form_error", "Form Error"),
        ("cta_click", "CTA Click"),
        ("scroll_depth", "Scroll Depth"),
        ("faq_open", "FAQ Open"),
        ("time_on_page", "Time on Page"),
        ("social_share", "Social Share"),
    ]

    # Dados do evento
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    event_data = models.JSONField(default=dict, blank=True)

    # Dados da sessão
    session_id = models.CharField(max_length=100, blank=True)
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    referrer = models.URLField(blank=True)

    # Dados de página
    page_url = models.URLField()
    page_title = models.CharField(max_length=200, blank=True)

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "landing_page_analytics"
        verbose_name = "Analytics Event"
        verbose_name_plural = "Analytics Events"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event_type", "created_at"]),
            models.Index(fields=["session_id"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


# =============================================================================
# UTILITIES
# =============================================================================


def get_client_ip(request):
    """Extrai o IP real do cliente"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def extract_utm_params(request):
    """Extrai parâmetros UTM da query string"""
    return {
        "utm_source": request.GET.get("utm_source", ""),
        "utm_medium": request.GET.get("utm_medium", ""),
        "utm_campaign": request.GET.get("utm_campaign", ""),
    }


def validate_request_data(data: Dict[str, Any]) -> Dict[str, str]:
    """Valida dados do request e retorna erros se houver"""
    errors = {}

    # Validar nome
    name = data.get("name", "").strip()
    if not name:
        errors["name"] = "Nome é obrigatório"
    elif len(name) < 2:
        errors["name"] = "Nome deve ter pelo menos 2 caracteres"
    elif len(name) > 100:
        errors["name"] = "Nome deve ter no máximo 100 caracteres"

    # Validar email
    email = data.get("email", "").strip().lower()
    if not email:
        errors["email"] = "Email é obrigatório"
    else:
        email_pattern = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
        if not email_pattern.match(email):
            errors["email"] = "Email deve ter um formato válido"

    # Validar role
    role = data.get("role", "")
    valid_roles = [choice[0] for choice in WaitlistSubscriber.ROLE_CHOICES]
    if not role:
        errors["role"] = "Área de atuação é obrigatória"
    elif role not in valid_roles:
        errors["role"] = "Área de atuação inválida"

    return errors


# =============================================================================
# VIEWS
# =============================================================================


class LandingPageView(TemplateView):
    """View principal da landing page"""

    template_name = "landing_page/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Adicionar dados para a página
        context.update(
            {
                "waitlist_count": WaitlistSubscriber.objects.filter(
                    is_active=True
                ).count(),
                "page_title": "Symplifika - Automações Fáceis e Rápidas | Em Breve",
                "meta_description": "Descubra o Symplifika - a plataforma de automação de texto com IA que vai revolucionar sua produtividade.",
            }
        )

        # Track page view
        try:
            LandingPageAnalytics.objects.create(
                event_type="page_view",
                page_url=self.request.build_absolute_uri(),
                page_title=context["page_title"],
                user_agent=self.request.META.get("HTTP_USER_AGENT", ""),
                ip_address=get_client_ip(self.request),
                referrer=self.request.META.get("HTTP_REFERER", ""),
                session_id=self.request.session.session_key or "",
                event_data=extract_utm_params(self.request),
            )
        except Exception as e:
            logger.error(f"Error tracking page view: {e}")

        return context


@csrf_exempt
@require_http_methods(["POST"])
def waitlist_submit_api(request):
    """API endpoint para submissão do formulário de lista de espera"""

    try:
        # Parse JSON data
        data = json.loads(request.body.decode("utf-8"))

        # Validar dados
        errors = validate_request_data(data)
        if errors:
            return JsonResponse({"success": False, "errors": errors}, status=400)

        # Extrair dados limpos
        name = data["name"].strip()
        email = data["email"].strip().lower()
        role = data["role"]

        # Verificar se email já existe
        if WaitlistSubscriber.objects.filter(email=email).exists():
            return JsonResponse(
                {
                    "success": False,
                    "message": "Este email já está cadastrado na nossa lista de espera!",
                },
                status=400,
            )

        # Extrair dados adicionais
        location_data = data.get("location", {})

        # Criar subscriber
        subscriber = WaitlistSubscriber.objects.create(
            name=name,
            email=email,
            role=role,
            ip_address=get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            referrer=data.get("referrer", ""),
            country=location_data.get("country", ""),
            city=location_data.get("city", ""),
            timezone=location_data.get("timezone", ""),
            **extract_utm_params(request),
        )

        # Track successful submission
        LandingPageAnalytics.objects.create(
            event_type="form_success",
            page_url=request.META.get("HTTP_REFERER", ""),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            ip_address=get_client_ip(request),
            referrer=request.META.get("HTTP_REFERER", ""),
            session_id=request.session.session_key or "",
            event_data={
                "subscriber_id": subscriber.id,
                "role": role,
                "referrer": data.get("referrer", ""),
                **extract_utm_params(request),
            },
        )

        # Enviar email de boas-vindas (opcional)
        # send_welcome_email.delay(subscriber.id)

        # Resposta de sucesso
        return JsonResponse(
            {
                "success": True,
                "message": "Obrigado! Você foi adicionado à nossa lista de espera.",
                "subscriber_id": subscriber.id,
                "waitlist_count": WaitlistSubscriber.objects.filter(
                    is_active=True
                ).count(),
            }
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "message": "Dados inválidos"}, status=400
        )

    except Exception as e:
        logger.error(f"Error in waitlist submission: {e}")

        # Track error
        try:
            LandingPageAnalytics.objects.create(
                event_type="form_error",
                page_url=request.META.get("HTTP_REFERER", ""),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                ip_address=get_client_ip(request),
                session_id=request.session.session_key or "",
                event_data={"error": str(e)},
            )
        except:
            pass

        return JsonResponse(
            {"success": False, "message": "Erro interno do servidor. Tente novamente."},
            status=500,
        )


@csrf_exempt
@require_http_methods(["POST"])
def analytics_track_api(request):
    """API endpoint para tracking de eventos analytics"""

    try:
        data = json.loads(request.body.decode("utf-8"))

        event_type = data.get("event_type")
        if not event_type:
            return JsonResponse(
                {"success": False, "message": "event_type é obrigatório"}, status=400
            )

        # Criar evento analytics
        LandingPageAnalytics.objects.create(
            event_type=event_type,
            event_data=data.get("event_data", {}),
            page_url=data.get("page_url", ""),
            page_title=data.get("page_title", ""),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            ip_address=get_client_ip(request),
            referrer=request.META.get("HTTP_REFERER", ""),
            session_id=request.session.session_key or "",
        )

        return JsonResponse({"success": True})

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "message": "Dados inválidos"}, status=400
        )

    except Exception as e:
        logger.error(f"Error in analytics tracking: {e}")
        return JsonResponse(
            {"success": False, "message": "Erro interno do servidor"}, status=500
        )


def waitlist_stats_api(request):
    """API endpoint para estatísticas da lista de espera"""

    try:
        from django.db.models import Count
        from django.utils import timezone
        from datetime import datetime, timedelta

        # Dados básicos
        total_count = WaitlistSubscriber.objects.filter(is_active=True).count()
        today_count = WaitlistSubscriber.objects.filter(
            created_at__date=timezone.now().date(), is_active=True
        ).count()

        # Distribuição por área
        role_distribution = (
            WaitlistSubscriber.objects.filter(is_active=True)
            .values("role")
            .annotate(count=Count("role"))
            .order_by("-count")
        )

        # Crescimento nos últimos 7 dias
        last_7_days = []
        for i in range(7):
            date = timezone.now().date() - timedelta(days=i)
            count = WaitlistSubscriber.objects.filter(
                created_at__date=date, is_active=True
            ).count()
            last_7_days.append({"date": date.isoformat(), "count": count})

        return JsonResponse(
            {
                "success": True,
                "data": {
                    "total_count": total_count,
                    "today_count": today_count,
                    "role_distribution": list(role_distribution),
                    "last_7_days": last_7_days,
                    "generated_at": timezone.now().isoformat(),
                },
            }
        )

    except Exception as e:
        logger.error(f"Error in waitlist stats: {e}")
        return JsonResponse(
            {"success": False, "message": "Erro ao buscar estatísticas"}, status=500
        )


# =============================================================================
# URL CONFIGURATION
# =============================================================================

"""
# Adicione estas URLs ao seu urls.py:

from django.urls import path
from . import django_integration as landing

urlpatterns = [
    # Landing page principal
    path('', landing.LandingPageView.as_view(), name='landing_page'),

    # APIs
    path('api/waitlist/submit/', landing.waitlist_submit_api, name='waitlist_submit'),
    path('api/analytics/track/', landing.analytics_track_api, name='analytics_track'),
    path('api/waitlist/stats/', landing.waitlist_stats_api, name='waitlist_stats'),
]
"""

# =============================================================================
# ADMIN CONFIGURATION
# =============================================================================

"""
# Adicione ao seu admin.py:

from django.contrib import admin
from .models import WaitlistSubscriber, LandingPageAnalytics

@admin.register(WaitlistSubscriber)
class WaitlistSubscriberAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'role', 'country', 'created_at', 'is_active')
    list_filter = ('role', 'is_active', 'created_at', 'country', 'is_early_access_sent')
    search_fields = ('name', 'email', 'city', 'country')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 50
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'email', 'role')
        }),
        ('Tracking', {
            'fields': ('ip_address', 'user_agent', 'referrer', 'utm_source', 'utm_medium', 'utm_campaign')
        }),
        ('Localização', {
            'fields': ('country', 'city', 'timezone')
        }),
        ('Status', {
            'fields': ('is_active', 'is_early_access_sent', 'is_beta_invited')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'early_access_sent_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(LandingPageAnalytics)
class LandingPageAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'page_url', 'ip_address', 'created_at')
    list_filter = ('event_type', 'created_at')
    search_fields = ('page_url', 'session_id')
    readonly_fields = ('created_at',)
    list_per_page = 100
    date_hierarchy = 'created_at'
"""

# =============================================================================
# CELERY TASKS (OPCIONAL)
# =============================================================================

"""
# Para envio assíncrono de emails:

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_welcome_email(subscriber_id):
    try:
        subscriber = WaitlistSubscriber.objects.get(id=subscriber_id)

        subject = 'Bem-vindo à lista de espera do Symplifika!'
        message = f'''
        Olá {subscriber.name}!

        Obrigado por se inscrever na nossa lista de espera!

        Em breve você receberá acesso antecipado ao Symplifika,
        a plataforma de automação de texto com IA.

        Atenciosamente,
        Equipe Symplifika
        '''

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[subscriber.email],
            fail_silently=False,
        )

        logger.info(f"Welcome email sent to {subscriber.email}")

    except Exception as e:
        logger.error(f"Error sending welcome email: {e}")
"""
