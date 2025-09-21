from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.conf import settings
import json

from .models import UserProfile
from .forms import UserProfileForm, UserUpdateForm
from shortcuts.models import Shortcut, Category
from core.utils import get_breadcrumbs_context, get_user_context, build_breadcrumbs


@login_required
def profile_view(request, user_id=None):
    """User profile page"""
    if user_id:
        profile_user = get_object_or_404(User, id=user_id)
        # Check if user can view this profile
        if profile_user != request.user and not request.user.is_staff:
            messages.error(request, 'Você não tem permissão para ver este perfil.')
            return redirect('users:profile')
    else:
        profile_user = request.user

    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=profile_user)

    # Get user statistics
    shortcuts_count = Shortcut.objects.filter(user=profile_user).count()
    categories_count = Category.objects.filter(
        shortcuts__user=profile_user
    ).distinct().count()

    # Get recent shortcuts
    recent_shortcuts = Shortcut.objects.filter(
        user=profile_user
    ).order_by('-created_at')[:5]

    # Get favorite shortcuts count
    favorites_count = Shortcut.objects.filter(
        user=profile_user,
        is_favorite=True
    ).count()

    # Breadcrumbs
    breadcrumbs = build_breadcrumbs(
        ('Perfil', None)
    )

    context = {
        'profile_user': profile_user,
        'profile': profile,
        'shortcuts_count': shortcuts_count,
        'categories_count': categories_count,
        'favorites_count': favorites_count,
        'recent_shortcuts': recent_shortcuts,
        'is_own_profile': profile_user == request.user,
        **get_breadcrumbs_context(breadcrumbs),
        **get_user_context(request.user),
    }

    return render(request, 'users/profile.html', context)


@login_required
def settings_view(request):
    """User settings page"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        try:
            # Handle profile form
            profile_form = UserProfileForm(request.POST, instance=profile)
            user_form = UserUpdateForm(request.POST, instance=request.user)

            if profile_form.is_valid() and user_form.is_valid():
                profile_form.save()
                user_form.save()
                messages.success(request, 'Configurações atualizadas com sucesso!')
                return redirect('users:settings')
            else:
                # Collect all form errors
                errors = []
                if profile_form.errors:
                    errors.extend(profile_form.errors.values())
                if user_form.errors:
                    errors.extend(user_form.errors.values())

                for error_list in errors:
                    for error in error_list:
                        messages.error(request, error)

        except Exception as e:
            messages.error(request, f'Erro ao atualizar configurações: {str(e)}')
    else:
        profile_form = UserProfileForm(instance=profile)
        user_form = UserUpdateForm(instance=request.user)

    # Get available themes
    theme_choices = [
        ('light', 'Claro'),
        ('dark', 'Escuro'),
        ('auto', 'Automático'),
    ]

    # Get timezone choices (simplified list)
    timezone_choices = [
        ('America/Sao_Paulo', 'São Paulo (UTC-3)'),
        ('America/New_York', 'New York (UTC-5)'),
        ('Europe/London', 'London (UTC+0)'),
        ('Europe/Paris', 'Paris (UTC+1)'),
        ('Asia/Tokyo', 'Tokyo (UTC+9)'),
    ]

    # Breadcrumbs
    breadcrumbs = build_breadcrumbs(
        ('Configurações', None)
    )

    context = {
        'profile': profile,
        'profile_form': profile_form,
        'user_form': user_form,
        'theme_choices': theme_choices,
        'timezone_choices': timezone_choices,
        'current_theme': getattr(profile, 'theme', 'light'),
        **get_breadcrumbs_context(breadcrumbs),
        **get_user_context(request.user),
    }

    return render(request, 'users/settings.html', context)


@login_required
def edit_profile_view(request):
    """Edit profile page"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        try:
            profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
            user_form = UserUpdateForm(request.POST, instance=request.user)

            if profile_form.is_valid() and user_form.is_valid():
                profile_form.save()
                user_form.save()
                messages.success(request, 'Perfil atualizado com sucesso!')
                return redirect('users:profile')
            else:
                for form in [profile_form, user_form]:
                    for field, errors in form.errors.items():
                        for error in errors:
                            messages.error(request, f'{field}: {error}')

        except Exception as e:
            messages.error(request, f'Erro ao atualizar perfil: {str(e)}')
    else:
        profile_form = UserProfileForm(instance=profile)
        user_form = UserUpdateForm(instance=request.user)

    # Breadcrumbs
    breadcrumbs = build_breadcrumbs(
        ('Perfil', reverse('users:profile')),
        ('Editar', None)
    )

    context = {
        'profile': profile,
        'profile_form': profile_form,
        'user_form': user_form,
        **get_breadcrumbs_context(breadcrumbs),
        **get_user_context(request.user),
    }

    return render(request, 'users/edit_profile.html', context)


@login_required
def change_avatar_view(request):
    """Change user avatar"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        try:
            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']
                profile.save()
                messages.success(request, 'Avatar atualizado com sucesso!')
            else:
                messages.error(request, 'Nenhum arquivo de imagem foi enviado.')

            return redirect('users:profile')

        except Exception as e:
            messages.error(request, f'Erro ao atualizar avatar: {str(e)}')

    # Breadcrumbs
    breadcrumbs = build_breadcrumbs(
        ('Perfil', reverse('users:profile')),
        ('Alterar Avatar', None)
    )

    context = {
        'profile': profile,
        **get_breadcrumbs_context(breadcrumbs),
        **get_user_context(request.user),
    }

    return render(request, 'users/change_avatar.html', context)


@login_required
@require_http_methods(["POST"])
def delete_avatar_view(request):
    """Delete user avatar"""
    try:
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        if profile.avatar:
            profile.avatar.delete()
            profile.save()
            messages.success(request, 'Avatar removido com sucesso!')
        else:
            messages.info(request, 'Nenhum avatar para remover.')

    except Exception as e:
        messages.error(request, f'Erro ao remover avatar: {str(e)}')

    return redirect('users:profile')


# ================================
# API VIEWS FOR COMPONENTS
# ================================

@login_required
@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
def api_update_profile(request):
    """API endpoint to update user profile"""
    try:
        data = json.loads(request.body)
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        # Update profile fields
        updatable_fields = ['theme', 'email_notifications', 'ai_enabled']
        updated_fields = []

        for field in updatable_fields:
            if field in data:
                setattr(profile, field, data[field])
                updated_fields.append(field)

        if updated_fields:
            profile.save()

        # Update user fields
        user_updated_fields = []
        user_updatable_fields = ['first_name', 'last_name', 'email']

        for field in user_updatable_fields:
            if field in data:
                setattr(request.user, field, data[field])
                user_updated_fields.append(field)

        if user_updated_fields:
            request.user.save()

        return JsonResponse({
            'success': True,
            'message': 'Perfil atualizado com sucesso!',
            'updated_fields': updated_fields + user_updated_fields
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def api_user_stats(request):
    """API endpoint for user statistics"""
    try:
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        # Get user statistics
        shortcuts_count = Shortcut.objects.filter(user=request.user).count()
        categories_count = Category.objects.filter(
            shortcuts__user=request.user
        ).distinct().count()
        favorites_count = Shortcut.objects.filter(
            user=request.user,
            is_favorite=True
        ).count()

        # Get recent activity count (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_shortcuts = Shortcut.objects.filter(
            user=request.user,
            created_at__gte=thirty_days_ago
        ).count()

        stats = {
            'shortcuts_count': shortcuts_count,
            'categories_count': categories_count,
            'favorites_count': favorites_count,
            'recent_shortcuts': recent_shortcuts,
            'plan': profile.plan.name if hasattr(profile, 'plan') and profile.plan else 'Free',
            'theme': getattr(profile, 'theme', 'light'),
        }

        return JsonResponse({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def api_user_menu_data(request):
    """API endpoint for user menu data"""
    try:
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        data = {
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'full_name': request.user.get_full_name() or request.user.username,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
            },
            'profile': {
                'avatar': profile.avatar.url if hasattr(profile, 'avatar') and profile.avatar else None,
                'plan': profile.plan.name if hasattr(profile, 'plan') and profile.plan else 'Free',
                'theme': getattr(profile, 'theme', 'light'),
                'email_notifications': getattr(profile, 'email_notifications', True),
            },
            'stats': {
                'shortcuts_count': Shortcut.objects.filter(user=request.user).count(),
                'favorites_count': Shortcut.objects.filter(
                    user=request.user,
                    is_favorite=True
                ).count(),
            },
            'urls': {
                'profile': reverse('users:profile'),
                'settings': reverse('users:settings'),
                'shortcuts': reverse('shortcuts:list'),
                'favorites': reverse('shortcuts:favorites'),
                'help': reverse('core:help'),
                'feedback': reverse('core:feedback'),
                'logout': reverse('users:logout'),
            }
        }

        return JsonResponse(data)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_toggle_theme(request):
    """API endpoint to toggle user theme"""
    try:
        data = json.loads(request.body)
        theme = data.get('theme', 'light')

        if theme not in ['light', 'dark', 'auto']:
            return JsonResponse({
                'success': False,
                'error': 'Invalid theme option'
            }, status=400)

        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.theme = theme
        profile.save()

        return JsonResponse({
            'success': True,
            'theme': theme,
            'message': f'Tema alterado para {theme}'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ================================
# AUTHENTICATION VIEWS
# ================================

def login_view(request):
    """Login template view"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        from django.contrib.auth.forms import AuthenticationForm
        from django.contrib.auth import login

        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Bem-vindo de volta, {user.get_full_name() or user.username}!')

            # Redirect to next page or dashboard
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('core:dashboard')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    else:
        from django.contrib.auth.forms import AuthenticationForm
        form = AuthenticationForm()

    breadcrumbs = build_breadcrumbs(
        ('Login', None)
    )

    context = {
        'form': form,
        'next': request.GET.get('next', ''),
        **get_breadcrumbs_context(breadcrumbs),
    }

    return render(request, 'auth/login.html', context)


def register_view(request):
    """Registration template view"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        from django.contrib.auth.models import User
        from django.contrib.auth import login

        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')

            # Basic validation
            if not all([username, email, password1, password2]):
                messages.error(request, 'Preencha todos os campos obrigatórios.')
                return render(request, 'auth/register.html')

            if password1 != password2:
                messages.error(request, 'As senhas não coincidem.')
                return render(request, 'auth/register.html')

            if len(password1) < 8:
                messages.error(request, 'A senha deve ter pelo menos 8 caracteres.')
                return render(request, 'auth/register.html')

            # Check if user exists
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Este nome de usuário já está em uso.')
                return render(request, 'auth/register.html')

            if User.objects.filter(email=email).exists():
                messages.error(request, 'Este email já está cadastrado.')
                return render(request, 'auth/register.html')

            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )

            # Create profile
            UserProfile.objects.create(user=user)

            # Login user
            login(request, user)
            messages.success(request, f'Conta criada com sucesso! Bem-vindo, {user.get_full_name() or user.username}!')

            return redirect('core:dashboard')

        except Exception as e:
            messages.error(request, f'Erro ao criar conta: {str(e)}')

    breadcrumbs = build_breadcrumbs(
        ('Cadastro', None)
    )

    context = {
        **get_breadcrumbs_context(breadcrumbs),
    }

    return render(request, 'auth/register.html', context)


def logout_view(request):
    """Logout view"""
    from django.contrib.auth import logout

    if request.user.is_authenticated:
        username = request.user.get_full_name() or request.user.username
        logout(request)
        messages.success(request, f'Logout realizado com sucesso. Até logo, {username}!')

    return redirect('core:index')
