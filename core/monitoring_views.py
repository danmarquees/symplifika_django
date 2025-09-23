from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
import json

from .monitoring_models import (
    AIRequestLog,
    UserActivityLog,
    PaymentMonitoring,
    SubscriptionUsageTracking,
    DashboardMetrics
)
from users.models import UserProfile, Subscription, Payment
from payments.models import StripeSubscription, StripePaymentIntent
from shortcuts.models import Shortcut


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def monitoring_dashboard_overview(request):
    """
    API endpoint que retorna overview geral do dashboard com métricas principais
    """
    user = request.user
    
    # Período para análise (último mês)
    now = timezone.now()
    last_month = now - timedelta(days=30)
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    try:
        # Estatísticas básicas do usuário
        profile = UserProfile.objects.get(user=user)
        
        # AI Requests
        ai_stats = AIRequestLog.get_user_stats(user, 'month')
        ai_today = AIRequestLog.objects.filter(
            user=user,
            created_at__date=now.date()
        ).count()
        
        # Atividades
        activity_summary = UserActivityLog.get_user_activity_summary(user, 30)
        
        # Pagamentos
        payment_stats = PaymentMonitoring.get_user_payment_stats(user, 'month')
        
        # Atalhos
        shortcuts_count = Shortcut.objects.filter(user=user, is_active=True).count()
        shortcuts_used_today = UserActivityLog.objects.filter(
            user=user,
            activity