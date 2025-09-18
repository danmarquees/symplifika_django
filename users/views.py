from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from datetime import timedelta
import calendar
from django.contrib.auth.decorators import login_required

from .models import UserProfile
from .serializers import (
    UserSerializer, UserUpdateSerializer, UserProfileSerializer,
    PasswordChangeSerializer, LoginSerializer, UserStatsSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    AccountDeleteSerializer, PlanUpgradeSerializer
)
from .forms import (
    UserProfileForm, UserUpdateForm, CustomUserCreationForm,
    CustomPasswordChangeForm, PlanUpgradeForm, AccountDeleteForm
)
from .models import PlanUpgradeRequest
import logging
from django.core.cache import cache
from django.conf import settings


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar usuários"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Retorna dados do usuário logado"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Atualiza dados do usuário logado"""
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Muda a senha do usuário"""
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Senha alterada com sucesso'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Retorna estatísticas do usuário"""
        user = request.user

        # Estatísticas básicas
        shortcuts = user.shortcuts.all()
        total_shortcuts = shortcuts.count()
        active_shortcuts = shortcuts.filter(is_active=True).count()
        total_uses = shortcuts.aggregate(total=Sum('use_count'))['total'] or 0

        # Estatísticas de IA
        ai_requests_used = user.profile.ai_requests_used
        ai_requests_remaining = max(0, user.profile.max_ai_requests - ai_requests_used)

        # Tempo economizado
        time_saved_minutes = user.profile.time_saved_minutes
        time_saved_hours = round(time_saved_minutes / 60, 2)

        # Atalhos mais usados (top 5)
        most_used_shortcuts = list(
            shortcuts.filter(use_count__gt=0)
            .order_by('-use_count')[:5]
            .values('trigger', 'title', 'use_count')
        )

        # Uso por mês (últimos 6 meses)
        usage_by_month = self.get_usage_by_month(user)

        # Atalhos por categoria
        shortcuts_by_category = dict(
            shortcuts.values('category__name')
            .annotate(count=Count('id'))
            .values_list('category__name', 'count')
        )

        stats_data = {
            'total_shortcuts': total_shortcuts,
            'active_shortcuts': active_shortcuts,
            'total_uses': total_uses,
            'ai_requests_used': ai_requests_used,
            'ai_requests_remaining': ai_requests_remaining,
            'time_saved_minutes': time_saved_minutes,
            'time_saved_hours': time_saved_hours,
            'most_used_shortcuts': most_used_shortcuts,
            'usage_by_month': usage_by_month,
            'shortcuts_by_category': shortcuts_by_category
        }

        serializer = UserStatsSerializer(stats_data)
        return Response(serializer.data)

    def get_usage_by_month(self, user):
        """Calcula uso por mês dos últimos 6 meses"""
        now = timezone.now()
        usage_by_month = {}

        for i in range(6):
            # Calcula o mês
            month_date = now - timedelta(days=30 * i)
            month_key = month_date.strftime('%Y-%m')
            month_name = calendar.month_name[month_date.month]

            # Conta usos no mês
            month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if i == 0:
                month_end = now
            else:
                next_month = month_start.replace(month=month_start.month + 1) if month_start.month < 12 else month_start.replace(year=month_start.year + 1, month=1)
                month_end = next_month - timedelta(seconds=1)

            usage_count = user.shortcuts.filter(
                usage_history__used_at__range=[month_start, month_end]
            ).aggregate(total=Count('usage_history'))['total'] or 0

            usage_by_month[month_key] = {
                'month': month_name,
                'count': usage_count
            }

        return usage_by_month

    @action(detail=False, methods=['post'])
    def delete_account(self, request):
        """Exclui a conta do usuário"""
        serializer = AccountDeleteSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            user = request.user
            user.delete()
            return Response({'message': 'Conta excluída com sucesso'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar perfil do usuário"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    def get_object(self):
        """Retorna o perfil do usuário logado"""
        return self.request.user.profile

    @action(detail=False, methods=['post'])
    def upgrade_plan(self, request):
        """Faz upgrade do plano do usuário"""
        from .services import PaymentService

        payment_service = PaymentService()

        try:
            target_plan = request.data.get('plan')
            payment_method = request.data.get('payment_method', 'credit_card')
            billing_cycle = request.data.get('billing_cycle', 'monthly')

            if not target_plan:
                return Response(
                    {'error': 'Plano é obrigatório'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Criar solicitação de upgrade
            upgrade_request = payment_service.create_upgrade_request(
                user=request.user,
                target_plan=target_plan,
                payment_method=payment_method,
                billing_cycle=billing_cycle
            )

            # Para desenvolvimento, aprovar automaticamente
            # Em produção, isso seria feito após confirmação do pagamento
            if request.data.get('auto_approve', False):
                payment_service.process_payment(upgrade_request)

                return Response({
                    'message': f'Plano atualizado para {target_plan} com sucesso!',
                    'upgrade_request_id': upgrade_request.id,
                    'new_plan': target_plan,
                    'status': 'completed'
                })
            else:
                return Response({
                    'message': 'Solicitação de upgrade criada com sucesso!',
                    'upgrade_request_id': upgrade_request.id,
                    'amount': upgrade_request.amount,
                    'payment_method': payment_method,
                    'status': 'pending'
                })

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Erro interno do servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def plan_pricing(self, request):
        """Retorna preços dos planos"""
        from .services import PaymentService

        payment_service = PaymentService()
        plans = payment_service.get_plan_comparison(request.user)

        return Response(plans)

    @action(detail=False, methods=['get'])
    def subscription_info(self, request):
        """Retorna informações da assinatura do usuário"""
        from .services import PaymentService

        payment_service = PaymentService()
        subscription_info = payment_service.get_user_subscription_info(request.user)

        return Response(subscription_info)

    @action(detail=False, methods=['get'])
    def payment_methods(self, request):
        """Retorna métodos de pagamento disponíveis"""
        from .services import PaymentService

        payment_service = PaymentService()
        payment_methods = payment_service.get_available_payment_methods()

        return Response(payment_methods)

    @action(detail=False, methods=['get'])
    def payment_history(self, request):
        """Retorna histórico de pagamentos do usuário"""
        from .services import PaymentService

        payment_service = PaymentService()
        payments = payment_service.get_user_payment_history(request.user)

        from .serializers import PaymentSerializer
        serializer = PaymentSerializer(payments, many=True)

        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def cancel_subscription(self, request):
        """Cancela a assinatura do usuário"""
        from .services import PaymentService

        try:
            payment_service = PaymentService()
            payment_service.cancel_subscription(request.user)

            return Response({
                'message': 'Assinatura cancelada com sucesso',
                'new_plan': 'free'
            })

        except Exception as e:
            return Response(
                {'error': 'Erro ao cancelar assinatura'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def process_payment(self, request):
        """Processa pagamento de upgrade"""
        from .services import PaymentService
        from .models import PlanUpgradeRequest

        try:
            upgrade_request_id = request.data.get('upgrade_request_id')
            payment_data = request.data.get('payment_data', {})

            if not upgrade_request_id:
                return Response(
                    {'error': 'ID da solicitação de upgrade é obrigatório'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            upgrade_request = PlanUpgradeRequest.objects.get(
                id=upgrade_request_id,
                user=request.user,
                status='pending'
            )

            payment_service = PaymentService()
            payment = payment_service.process_payment(upgrade_request, payment_data)

            return Response({
                'message': 'Pagamento processado com sucesso!',
                'payment_id': payment.id,
                'transaction_id': payment.transaction_id,
                'new_plan': upgrade_request.requested_plan
            })

        except PlanUpgradeRequest.DoesNotExist:
            return Response(
                {'error': 'Solicitação de upgrade não encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': 'Erro ao processar pagamento'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def reset_monthly_counters(self, request):
        """Reseta contadores mensais (uso interno/admin)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Acesso negado'},
                status=status.HTTP_403_FORBIDDEN
            )

        profile = request.user.profile
        profile.reset_monthly_counters()

        return Response({'message': 'Contadores mensais resetados'})


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Registra um novo usuário"""
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        # Cria token de autenticação
        token, created = Token.objects.get_or_create(user=user)

        # Faz login automático
        login(request, user)

        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Usuário criado com sucesso'
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Faz login do usuário com rate limiting e proteção contra brute force"""
    logger = logging.getLogger('security')
    ip = request.META.get('REMOTE_ADDR', 'unknown')
    username = request.data.get('username') or request.data.get('email')

    # Proteção contra brute force: bloqueia após 5 tentativas falhas por IP/username por 10 minutos
    brute_force_key = f"login_fail_{ip}_{username}"
    fail_count = cache.get(brute_force_key, 0)
    if fail_count >= 5:
        logger.warning(f"Bloqueio temporário de login para {username} do IP {ip}")
        if hasattr(settings, 'notify_slack'):
            settings.notify_slack(f"Bloqueio temporário de login para {username} do IP {ip}")
        return Response({
            "error": "Muitas tentativas de login. Tente novamente em alguns minutos.",
            "code": "too_many_attempts"
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)

    serializer = LoginSerializer(
        data=request.data,
        context={'request': request}
    )
    if serializer.is_valid():
        user = serializer.validated_data['user']

        # Cria ou pega token
        token, created = Token.objects.get_or_create(user=user)

        # Faz login
        login(request, user)

        # Atualiza último login no perfil
        user.profile.last_login = timezone.now()
        user.profile.save(update_fields=['last_login'])

        # Resetar contador de falhas após sucesso
        cache.delete(brute_force_key)

        logger.info(f"Login realizado para {username} do IP {ip}")
        if hasattr(settings, 'notify_slack') and created:
            settings.notify_slack(f"Novo login realizado para {username} do IP {ip}")

        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Login realizado com sucesso'
        })

    # Falha de login: incrementa contador e monitora atividade suspeita
    cache.set(brute_force_key, fail_count + 1, timeout=600)
    logger.warning(f"Tentativa de login falha para {username} do IP {ip} (falha {fail_count + 1})")
    if hasattr(settings, 'notify_slack') and fail_count + 1 >= 3:
        settings.notify_slack(f"Tentativas suspeitas de login para {username} do IP {ip} (falha {fail_count + 1})")

    return Response({
        "error": "Usuário ou senha inválidos",
        "code": "invalid_credentials"
    }, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Faz logout do usuário"""
    try:
        # Remove token
        token = Token.objects.get(user=request.user)
        token.delete()
    except Token.DoesNotExist:
        pass

    # Faz logout
    logout(request)

    return Response({'message': 'Logout realizado com sucesso'})


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    """Solicita reset de senha"""
    serializer = PasswordResetRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)

        # Aqui você implementaria o envio de email
        # Por enquanto, apenas retorna sucesso

        return Response({
            'message': 'Instruções de recuperação enviadas para seu email'
        })

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """Confirma reset de senha"""
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        # Aqui você implementaria a validação do token
        # e a atualização da senha

        return Response({
            'message': 'Senha alterada com sucesso'
        })

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_data(request):
    """Retorna dados para o dashboard do usuário"""
    user = request.user

    # Estatísticas rápidas
    shortcuts_count = user.shortcuts.filter(is_active=True).count()
    total_uses = user.shortcuts.aggregate(total=Sum('use_count'))['total'] or 0

    # Atalhos recentes (últimos 5 criados)
    recent_shortcuts = user.shortcuts.order_by('-created_at')[:5]

    # Atalhos mais usados (top 3)
    top_shortcuts = user.shortcuts.filter(use_count__gt=0).order_by('-use_count')[:3]

    # Atividade recente (últimos 7 dias)
    week_ago = timezone.now() - timedelta(days=7)
    recent_activity = user.shortcuts.filter(
        usage_history__used_at__gte=week_ago
    ).distinct().count()

    from shortcuts.serializers import ShortcutSerializer

    return Response({
        'shortcuts_count': shortcuts_count,
        'total_uses': total_uses,
        'recent_activity': recent_activity,
        'ai_requests_remaining': max(0, user.profile.max_ai_requests - user.profile.ai_requests_used),
        'recent_shortcuts': ShortcutSerializer(recent_shortcuts, many=True).data,
        'top_shortcuts': ShortcutSerializer(top_shortcuts, many=True).data,
        'plan': user.profile.get_plan_display(),
        'theme': user.profile.theme
    })


# ============================================================================
# HTML Template Views
# ============================================================================

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy


def login_template_view(request):
    """Renderiza o template de login"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, f'Bem-vindo, {user.get_full_name() or user.username}!')
                next_url = request.POST.get('next') or request.GET.get('next') or 'core:dashboard'
                return redirect(next_url)
            else:
                messages.error(request, 'Credenciais inválidas. Tente novamente.')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = AuthenticationForm()

    return render(request, 'auth/login.html', {
        'form': form,
        'redirect_field_name': 'next',
        'redirect_field_value': request.GET.get('next', ''),
    })


def register_template_view(request):
    """Renderiza o template de registro"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    from django.contrib.auth.forms import UserCreationForm

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Criar perfil do usuário
            UserProfile.objects.get_or_create(user=user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada para {username}!')
            return redirect('users:login')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = UserCreationForm()

    return render(request, 'auth/register.html', {'form': form})


def logout_template_view(request):
    """Faz logout do usuário"""
    username = request.user.username if request.user.is_authenticated else None
    logout(request)
    if username:
        messages.success(request, f'Logout realizado com sucesso. Até logo, {username}!')
    return redirect('core:index')

def profile_template_view(request):
    """Renderiza o template de perfil"""
    if not request.user.is_authenticated:
        return redirect('users:login')

    user = request.user
    profile = user.userprofile

    return render(request, 'auth/profile.html', {'user': user, 'profile': profile})

def profile_update_view(request):
    """Atualiza o perfil do usuário"""
    if not request.user.is_authenticated:
        return redirect('users:login')

    user = request.user
    profile = user.profile

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'auth/profile_update.html', {'form': form})

def profile_delete_view(request):
    """Exclui o perfil do usuário"""
    if not request.user.is_authenticated:
        return redirect('users:login')

    user = request.user
    profile = user.profile

    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Perfil excluído com sucesso!')
        return redirect('core:index')
    else:
        return render(request, 'auth/profile_delete.html', {'user': user})

def profile_delete_confirm_view(request):
    """Confirmação de exclusão do perfil"""
    if not request.user.is_authenticated:
        return redirect('users:login')

    user = request.user
    profile = user.profile

    if request.method == 'POST':
        user.delete()
        logout(request)
        messages.success(request, 'Conta excluída com sucesso.')
        return redirect('core:index')
    else:
        return render(request, 'auth/profile_delete_confirm.html', {'user': user})


def plan_upgrade_view(request):
    """View para upgrade de plano"""
    if not request.user.is_authenticated:
        return redirect('users:login')

    from .services import PaymentService

    payment_service = PaymentService()

    if request.method == 'POST':
        form = PlanUpgradeForm(request.user, request.POST)
        if form.is_valid():
            try:
                target_plan = form.cleaned_data['plan']
                payment_method = form.cleaned_data['payment_method']

                upgrade_request = payment_service.create_upgrade_request(
                    user=request.user,
                    target_plan=target_plan,
                    payment_method=payment_method
                )

                messages.success(request, 'Solicitação de upgrade criada com sucesso!')
                return redirect('users:plan_upgrade_payment', upgrade_id=upgrade_request.id)

            except ValueError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = PlanUpgradeForm(request.user)

    # Dados para o template
    plans = payment_service.get_plan_comparison(request.user)
    payment_methods = payment_service.get_available_payment_methods()
    subscription_info = payment_service.get_user_subscription_info(request.user)

    context = {
        'form': form,
        'plans': plans,
        'payment_methods': payment_methods,
        'subscription_info': subscription_info,
        'current_plan': request.user.profile.plan
    }

    return render(request, 'users/plan_upgrade.html', context)


def plan_upgrade_payment_view(request, upgrade_id):
    """View para pagamento do upgrade"""
    if not request.user.is_authenticated:
        return redirect('users:login')

    try:
        upgrade_request = PlanUpgradeRequest.objects.get(
            id=upgrade_id,
            user=request.user,
            status='pending'
        )
    except PlanUpgradeRequest.DoesNotExist:
        messages.error(request, 'Solicitação de upgrade não encontrada.')
        return redirect('users:plan_upgrade')

    if request.method == 'POST':
        # Simular processamento de pagamento
        from .services import PaymentService

        try:
            payment_service = PaymentService()
            payment = payment_service.process_payment(upgrade_request)

            messages.success(request, f'Pagamento processado com sucesso! Seu plano foi atualizado para {upgrade_request.requested_plan}.')
            return redirect('users:profile')

        except Exception as e:
            messages.error(request, 'Erro ao processar pagamento. Tente novamente.')

    context = {
        'upgrade_request': upgrade_request,
        'payment_methods': PaymentService().get_available_payment_methods()
    }

    return render(request, 'users/plan_upgrade_payment.html', context)


def subscription_management_view(request):
    """View para gerenciamento de assinatura"""
    if not request.user.is_authenticated:
        return redirect('users:login')

    from .services import PaymentService

    payment_service = PaymentService()
    subscription_info = payment_service.get_user_subscription_info(request.user)
    payment_history = payment_service.get_user_payment_history(request.user)[:10]  # Últimos 10

    if request.method == 'POST' and 'cancel_subscription' in request.POST:
        try:
            payment_service.cancel_subscription(request.user)
            messages.success(request, 'Assinatura cancelada com sucesso.')
            return redirect('users:subscription_management')
        except Exception as e:
            messages.error(request, 'Erro ao cancelar assinatura.')

    context = {
        'subscription_info': subscription_info,
        'payment_history': payment_history,
        'current_plan': request.user.profile.plan
    }

    return render(request, 'users/subscription_management.html', context)

def settings_view(request):
    """View para configurações do usuário"""
    if not request.user.is_authenticated:
        return redirect('users:login')

    context = {
        'user': request.user,
        'profile': request.user.profile
    }

    return render(request, 'users/settings.html', context)


@login_required
def subscription_success_view(request):
    """View para sucesso da assinatura"""
    session_id = request.GET.get('session_id')
    
    if session_id:
        # Aqui você pode verificar o status da sessão no Stripe se necessário
        # Por enquanto, apenas mostramos uma mensagem de sucesso
        messages.success(request, 'Pagamento realizado com sucesso! Sua assinatura foi ativada.')
    
    context = {
        'session_id': session_id,
        'user': request.user
    }
    
    return render(request, 'users/subscription_success.html', context)
