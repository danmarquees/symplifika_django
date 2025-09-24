from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.cache import cache_page
from shortcuts.models import Shortcut, Category
from users.models import UserProfile
import json

from django.conf import settings as django_settings
import os

# Importações DRF para o endpoint de estatísticas
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import SystemStats
from .serializers import SystemStatsSerializer


def frontend_app(request):
    """Serve the main frontend application"""
    return render(request, 'frontend.html')


def api_status(request):
    """API status endpoint"""
    return JsonResponse({
        'status': 'ok',
        'message': 'Symplifika API is running',
        'version': '1.0.0'
    })


@csrf_exempt
@require_http_methods(["GET", "POST", "OPTIONS"])
def health_check(request):
    """Health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat()
    })


def index(request):
    """Home page view"""
    return render(request, 'index.html')


@login_required
def dashboard(request):
    """Dashboard view"""
    return render(request, 'dashboard.html')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """API endpoint for dashboard statistics"""
    user = request.user

    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=user)

    # Get shortcuts statistics
    shortcuts = Shortcut.objects.filter(user=user)
    total_shortcuts = shortcuts.count()
    active_shortcuts = shortcuts.filter(is_active=True).count()

    # Get categories count
    categories_count = Category.objects.filter(
        shortcuts__user=user
    ).distinct().count()

    # Calculate monthly usage (last 30 days)
    from datetime import timedelta
    thirty_days_ago = timezone.now() - timedelta(days=30)
    monthly_usage = shortcuts.filter(
        last_used__gte=thirty_days_ago
    ).count()

    # Calculate time saved (estimate: 30 seconds per shortcut use)
    total_uses = sum(shortcut.use_count for shortcut in shortcuts)
    time_saved_minutes = total_uses * 0.5  # 30 seconds = 0.5 minutes
    time_saved_hours = round(time_saved_minutes / 60, 1)

    # Calculate today's usage for the usage counter
    today = timezone.now().date()
    usages_today = shortcuts.filter(
        last_used__date=today
    ).count()

    # Weekly usage for chart
    weekly_usage = []
    for i in range(7):
        day = today - timedelta(days=i)
        day_usage = shortcuts.filter(last_used__date=day).count()
        weekly_usage.append({
            'day': day.strftime('%a'),
            'count': day_usage
        })
    weekly_usage.reverse()

    return Response({
        'total_shortcuts': total_shortcuts,
        'active_shortcuts': active_shortcuts,
        'total_categories': categories_count,
        'categories_count': categories_count,
        'monthly_usage': monthly_usage,
        'usages_today': usages_today,
        'total_usages': total_uses,
        'time_saved': f"{time_saved_hours}h",
        'time_saved_minutes': time_saved_minutes,
        'ai_requests_used': profile.ai_requests_used,
        'ai_requests_remaining': max(0, profile.max_ai_requests - profile.ai_requests_used),
        'max_ai_requests': profile.max_ai_requests,
        'max_ai_requests_free': profile.max_ai_requests_free if hasattr(profile, 'max_ai_requests_free') else 50,
        'plan': profile.plan,
        'plan_display': profile.get_plan_display(),
        'max_shortcuts': profile.max_shortcuts,
        'weekly_usage': weekly_usage,
        'user_full_name': user.get_full_name() or user.username,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def plan_status(request):
    """API endpoint for quick plan status check"""
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    return Response({
        'plan': profile.plan,
        'plan_display': profile.get_plan_display(),
        'ai_requests_used': profile.ai_requests_used,
        'max_ai_requests': profile.max_ai_requests,
        'max_ai_requests_free': profile.max_ai_requests_free if hasattr(profile, 'max_ai_requests_free') else 50,
        'max_shortcuts': profile.max_shortcuts,
        'last_updated': timezone.now().isoformat(),
    })


@login_required
def shortcuts(request):
    """Shortcuts management page"""
    return render(request, 'dashboard.html')


# Authentication views moved to users app - no redirects needed


@login_required
def profile_view(request, user_id=None):
    """Profile view - shows user profile with stats and activity"""
    from django.shortcuts import get_object_or_404
    from django.contrib.auth.models import User
    from django.db.models import Sum, Count
    from users.models import UserProfile

    # If user_id is provided, show that user's profile, otherwise show current user's profile
    if user_id:
        profile_user = get_object_or_404(User, id=user_id)
    else:
        profile_user = request.user

    # Get or create profile
    profile, created = UserProfile.objects.get_or_create(user=profile_user)

    # Calculate statistics
    shortcuts_count = profile_user.shortcuts.filter(is_active=True).count()
    total_usage = profile_user.shortcuts.aggregate(total=Sum('use_count'))['total'] or 0
    time_saved = profile.time_saved_minutes / 60 if profile.time_saved_minutes else 0

    context = {
        'profile_user': profile_user,
        'shortcuts_count': shortcuts_count,
        'total_usage': total_usage,
        'time_saved': round(time_saved, 1)
    }

    return render(request, 'core/profile/profile.html', context)


@login_required
def edit_profile(request):
    """Edit profile view"""
    if request.method == 'POST':
        # Process profile edit form data
        messages.success(request, 'Profile updated successfully!')
        return redirect('core:profile')
    return render(request, 'edit_profile.html')


@login_required
def change_password(request):
    """Change password view"""
    if request.method == 'POST':
        # Process password change form data
        messages.success(request, 'Password changed successfully!')
        return redirect('core:profile')
    return render(request, 'change_password.html')


@login_required
def change_avatar(request):
    """Change avatar view"""
    if request.method == 'POST':
        # Process avatar change form data
        messages.success(request, 'Avatar updated successfully!')
        return redirect('core:profile')
    return render(request, 'change_avatar.html')


@login_required
def delete_avatar(request):
    """Delete avatar view"""
    if request.method == 'POST':
        # Process avatar deletion
        messages.success(request, 'Avatar deleted successfully!')
        return redirect('core:profile')
    return render(request, 'delete_avatar.html')


@login_required
@require_http_methods(["POST"])
def upload_avatar(request):
    """Upload avatar endpoint"""
    if request.FILES.get('avatar'):
        # Process avatar upload
        messages.success(request, 'Avatar uploaded successfully!')
    else:
        messages.error(request, 'No avatar file provided!')
    return redirect('core:profile')


@login_required
@require_http_methods(["POST"])
def delete_uploaded_avatar(request, avatar_id=None):
    """Delete uploaded avatar endpoint"""
    # Process avatar deletion
    messages.success(request, 'Avatar deleted successfully!')
    return redirect('core:profile')


@login_required
def support(request):
    """Support view"""
    return render(request, 'support.html')


@login_required
def feedback(request):
    """Feedback view"""
    if request.method == 'POST':
        # Process feedback form data
        messages.success(request, 'Obrigado pelo seu feedback!')
        return redirect('core:feedback')
    return render(request, 'feedback.html')


@login_required
def settings(request):
    """Settings view - user preferences and account settings"""
    from .forms import UserSettingsForm

    if request.method == 'POST':
        # Process settings form data
        form = UserSettingsForm(request.POST, instance=request.user.profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configurações atualizadas com sucesso!')
            return redirect('core:settings')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = UserSettingsForm(instance=request.user.profile, user=request.user)

    context = {
        'form': form,
        'user': request.user
    }

    return render(request, 'core/settings.html', context)


@login_required
def about(request):
    """About view"""
    return render(request, 'about.html')


@login_required
def contact(request):
    """Contact view"""
    if request.method == 'POST':
        # Process contact form data
        messages.success(request, 'Your message has been sent!')
        return redirect('core:contact')
    return render(request, 'contact.html')


def privacy(request):
    """Privacy policy view"""
    return render(request, 'privacy.html')


def terms(request):
    """Terms of service view"""
    return render(request, 'terms.html')


@login_required
def faq(request):
    """FAQ view"""
    return render(request, 'faq.html')


def help(request):
    """Help view - comprehensive help and FAQ"""
    return render(request, 'help.html')


def pricing(request):
    """Pricing view"""
    return render(request, 'pricing.html')


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def statistics_view(request):
    """
    Endpoint para retornar as estatísticas mais recentes do sistema.
    """
    stats = SystemStats.objects.order_by('-date').first()
    if not stats:
        # Gera estatísticas se não houver registro
        stats = SystemStats.update_daily_stats()
    serializer = SystemStatsSerializer(stats)
    return Response(serializer.data)


def favicon_view(request):
    """Serve favicon.ico"""
    # Try different favicon formats
    favicon_paths = [
        ('favicon.ico', 'image/x-icon'),
        ('favicon.svg', 'image/svg+xml'),
        ('favicon.png', 'image/png'),
    ]

    # Check static directories
    static_dirs = []
    if django_settings.STATIC_ROOT:
        static_dirs.append(django_settings.STATIC_ROOT)
    if django_settings.STATICFILES_DIRS:
        static_dirs.extend(django_settings.STATICFILES_DIRS)

    for static_dir in static_dirs:
        for filename, content_type in favicon_paths:
            favicon_path = os.path.join(static_dir, 'images', filename)
            if os.path.exists(favicon_path):
                with open(favicon_path, 'rb') as f:
                    return HttpResponse(f.read(), content_type=content_type)

    # Generate a minimal SVG favicon if none found
    svg_favicon = '''<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
  <rect width="32" height="32" rx="6" fill="#007bff"/>
  <text x="16" y="22" font-family="Arial,sans-serif" font-size="18" font-weight="bold" text-anchor="middle" fill="white">S</text>
</svg>'''
    return HttpResponse(svg_favicon, content_type="image/svg+xml")


# API Views for templates
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_activity_api(request, user_id):
    """API endpoint for user activity timeline"""
    from django.contrib.auth.models import User
    from django.shortcuts import get_object_or_404

    user = get_object_or_404(User, id=user_id)

    # Check if user can view this profile
    if user != request.user and not user.userprofile.public_profile:
        return Response({'error': 'Profile is private'}, status=status.HTTP_403_FORBIDDEN)

    # Mock activity data - replace with actual activity tracking
    activities = [
        {
            'description': 'Criou um novo atalho "Abrir Gmail"',
            'timestamp': timezone.now() - timezone.timedelta(hours=2)
        },
        {
            'description': 'Atualizou o perfil',
            'timestamp': timezone.now() - timezone.timedelta(days=1)
        },
        {
            'description': 'Fez upgrade para Premium',
            'timestamp': timezone.now() - timezone.timedelta(days=3)
        }
    ]

    return Response(activities)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_categories_api(request, user_id):
    """API endpoint for user favorite categories"""
    from django.contrib.auth.models import User
    from django.shortcuts import get_object_or_404
    from django.db.models import Count

    user = get_object_or_404(User, id=user_id)

    # Check if user can view this profile
    if user != request.user and not user.userprofile.public_profile:
        return Response({'error': 'Profile is private'}, status=status.HTTP_403_FORBIDDEN)

    # Get categories with shortcut counts
    categories = user.shortcuts.values('category').annotate(
        count=Count('id')
    ).order_by('-count')[:5]

    # Format response
    formatted_categories = []
    for cat in categories:
        formatted_categories.append({
            'name': cat['category'] or 'Sem categoria',
            'count': cat['count']
        })

    return Response(formatted_categories)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def usage_stats_api(request):
    """API endpoint for user usage statistics"""
    user = request.user

    # Calculate AI requests used this month
    ai_requests_used = getattr(user.userprofile, 'ai_requests_used', 0)

    # Calculate time saved (mock calculation)
    shortcuts_count = user.shortcuts.count()
    time_saved = shortcuts_count * 5  # 5 minutes per shortcut average

    stats = {
        'ai_requests_used': ai_requests_used,
        'time_saved': time_saved
    }

    return Response(stats)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def billing_history_api(request):
    """API endpoint for billing history"""
    # Mock billing history - integrate with actual payment system
    history = [
        {
            'date': timezone.now() - timezone.timedelta(days=30),
            'description': 'Assinatura Premium - Mensal',
            'amount': 29.90,
            'status': 'paid'
        },
        {
            'date': timezone.now() - timezone.timedelta(days=60),
            'description': 'Assinatura Premium - Mensal',
            'amount': 29.90,
            'status': 'paid'
        }
    ]

    return Response(history)


@csrf_exempt
@login_required
def api_profile_update(request):
    """API endpoint to update user profile"""
    if request.method != 'PUT':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

    try:
        import json
        from .forms import UserSettingsForm
        from users.models import UserProfile

        # Parse JSON data
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        # Ensure user has a profile
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        # Create form with data
        form = UserSettingsForm(data, instance=profile, user=request.user)

        if form.is_valid():
            saved_profile = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Perfil atualizado com sucesso!',
                'data': {
                    'theme': saved_profile.theme,
                    'email_notifications': saved_profile.email_notifications,
                    'ai_enabled': saved_profile.ai_enabled,
                    'ai_model_preference': saved_profile.ai_model_preference
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': dict(form.errors),
                'message': 'Dados inválidos'
            }, status=400)

    except Exception as e:
        import traceback
        error_info = {
            'success': False,
            'error': str(e),
            'type': type(e).__name__,
            'traceback': traceback.format_exc()
        }
        print(f"API Profile Error: {error_info}")  # Log to console
        return JsonResponse(error_info, status=500)


@csrf_exempt
@login_required
@require_http_methods(["PUT"])
def api_account_update(request):
    """API endpoint to update account settings"""
    import json

    try:
        data = json.loads(request.body)
        user = request.user

        # Update user fields
        if 'email' in data:
            user.email = data['email']
        if 'timezone' in data:
            # Store timezone in user profile or session
            request.session['timezone'] = data['timezone']

        user.save()
        return JsonResponse({'success': True, 'message': 'Configurações da conta atualizadas!'})
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def api_change_password(request):
    """API endpoint to change user password"""
    import json
    from django.contrib.auth import authenticate

    try:
        data = json.loads(request.body)
        user = request.user

        # Verify current password
        if not authenticate(username=user.username, password=data.get('current_password')):
            return JsonResponse({'success': False, 'error': 'Senha atual incorreta'}, status=400)

        # Set new password
        user.set_password(data.get('new_password'))
        user.save()

        return JsonResponse({'success': True, 'message': 'Senha alterada com sucesso!'})
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["PUT"])
def api_notifications_preferences(request):
    """API endpoint to update notification preferences"""
    import json

    try:
        data = json.loads(request.body)

        # Ensure user has a profile
        if not hasattr(request.user, 'profile'):
            from users.models import UserProfile
            UserProfile.objects.create(user=request.user)

        profile = request.user.profile

        # Update notification preferences
        if 'email_notifications' in data:
            profile.email_notifications = data['email_notifications']

        profile.save()
        return JsonResponse({'success': True, 'message': 'Preferências de notificação atualizadas!'})
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


def privacy_policy_view(request):
    """Renderiza a página de política de privacidade"""
    context = {
        'last_updated': 'Janeiro 2025'
    }
    return render(request, 'legal/privacy_policy.html', context)

# ================================
# SEARCH VIEWS
# ================================

def search_view(request):
    """Main search page with advanced search capabilities"""
    query = request.GET.get('q', '').strip()
    filter_type = request.GET.get('filter', 'all')
    page = request.GET.get('page', 1)

    # Initialize empty results
    results = []
    total_count = 0

    if query:
        # Build base queryset
        if request.user.is_authenticated:
            shortcuts_qs = Shortcut.objects.filter(user=request.user)
        else:
            shortcuts_qs = Shortcut.objects.filter(is_public=True)

        categories_qs = Category.objects.all()

        # Apply search filters
        if filter_type == 'shortcuts' or filter_type == 'all':
            shortcuts_results = shortcuts_qs.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(command__icontains=query) |
                Q(tags__icontains=query)
            ).distinct()

            if filter_type == 'shortcuts':
                results = shortcuts_results
            else:
                results.extend(shortcuts_results)

        if filter_type == 'categories' or filter_type == 'all':
            categories_results = categories_qs.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            ).distinct()

            if filter_type == 'categories':
                results = categories_results
            else:
                results.extend(categories_results)

        total_count = len(results) if isinstance(results, list) else results.count()

    # Pagination
    paginator = Paginator(results, 20)  # 20 items per page
    page_obj = paginator.get_page(page)

    # Breadcrumbs
    breadcrumbs = [
        {'title': 'Pesquisar', 'url': None}
    ]

    context = {
        'query': query,
        'filter_type': filter_type,
        'results': page_obj.object_list,
        'page_obj': page_obj,
        'total_count': total_count,
        'breadcrumbs': breadcrumbs,
        'show_search_filters': True,
    }

    return render(request, 'search/search_results.html', context)


@require_GET
def search_suggestions_api(request):
    """API endpoint for search suggestions"""
    query = request.GET.get('q', '').strip()
    filter_type = request.GET.get('filter', 'all')
    limit = min(int(request.GET.get('limit', 10)), 20)  # Max 20 suggestions

    if not query or len(query) < 2:
        return JsonResponse({'suggestions': []})

    suggestions = []

    try:
        # Get shortcuts suggestions
        if filter_type in ['all', 'shortcuts']:
            if request.user.is_authenticated:
                shortcuts = Shortcut.objects.filter(user=request.user, is_active=True)
            else:
                # Para usuários não autenticados, não mostrar atalhos (são privados)
                shortcuts = Shortcut.objects.none()

            shortcuts = shortcuts.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(trigger__icontains=query)
            ).select_related('category')[:limit//2 if filter_type == 'all' else limit]

            for shortcut in shortcuts:
                # Criar preview do conteúdo (primeiros 100 caracteres)
                content_preview = shortcut.content[:100] + '...' if len(shortcut.content) > 100 else shortcut.content
                
                suggestions.append({
                    'text': shortcut.title,
                    'type': 'shortcut',
                    'description': content_preview,
                    'trigger': shortcut.trigger,
                    'category': shortcut.category.name if shortcut.category else None,
                    'url': f'/shortcuts/{shortcut.id}/' if shortcut.id else None
                })

        # Get categories suggestions
        if filter_type in ['all', 'categories']:
            if request.user.is_authenticated:
                categories = Category.objects.filter(user=request.user)
            else:
                # Para usuários não autenticados, não mostrar categorias (são privadas)
                categories = Category.objects.none()

            categories = categories.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )[:limit//2 if filter_type == 'all' else limit]

            for category in categories:
                # Criar preview da descrição
                desc_preview = category.description[:100] + '...' if len(category.description) > 100 else category.description
                
                suggestions.append({
                    'text': category.name,
                    'type': 'category',
                    'description': desc_preview if category.description else f'Categoria: {category.name}',
                    'color': category.color,
                    'url': f'/shortcuts/category/{category.id}/' if category.id else None
                })

        # Sort by relevance (exact matches first, then starts with, then contains)
        def sort_key(item):
            text = item['text'].lower()
            query_lower = query.lower()
            if text == query_lower:
                return (0, text)
            elif text.startswith(query_lower):
                return (1, text)
            else:
                return (2, text)

        suggestions.sort(key=sort_key)
        suggestions = suggestions[:limit]

    except Exception as e:
        # Log error but don't crash
        print(f"Search suggestions error: {e}")
        suggestions = []

    return JsonResponse({'suggestions': suggestions})


# ================================
# USER PROFILE & SETTINGS VIEWS
# ================================

@login_required
def profile_view(request, user_id=None):
    """User profile page"""
    if user_id:
        profile_user = get_object_or_404(User, id=user_id)
        # Check if user can view this profile (privacy settings)
        if profile_user != request.user:
            # Add privacy checks here if needed
            pass
    else:
        profile_user = request.user

    # Get user profile or create one
    profile, created = UserProfile.objects.get_or_create(user=profile_user)

    # Get real statistics
    try:
        from shortcuts.models import Shortcut, Category

        shortcuts_count = Shortcut.objects.filter(user=profile_user).count()
        categories_count = Category.objects.filter(user=profile_user).count()
        favorites_count = 0  # Placeholder - implementar sistema de favoritos

        # Get recent shortcuts
        recent_shortcuts = Shortcut.objects.filter(
            user=profile_user
        ).order_by('-created_at')[:5]

    except ImportError:
        # Fallback if shortcuts app not available
        shortcuts_count = 0
        categories_count = 0
        favorites_count = 0
        recent_shortcuts = []

    context = {
        'profile_user': profile_user,
        'profile': profile,
        'shortcuts_count': shortcuts_count,
        'categories_count': categories_count,
        'favorites_count': favorites_count,
        'recent_shortcuts': recent_shortcuts,
        'breadcrumbs': [{'title': 'Perfil', 'url': None}],
        'is_own_profile': profile_user == request.user,
    }

    return render(request, 'users/profile.html', context)


@login_required
def settings_view(request):
    """User settings page"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Handle form submission
        try:
            # Update profile settings
            profile.theme = request.POST.get('theme', 'light')
            profile.email_notifications = request.POST.get('email_notifications') == 'on'
            profile.save()

            # Update user settings
            user = request.user
            if 'email' in request.POST:
                user.email = request.POST['email']
            if 'first_name' in request.POST:
                user.first_name = request.POST['first_name']
            if 'last_name' in request.POST:
                user.last_name = request.POST['last_name']
            user.save()

            messages.success(request, 'Configurações atualizadas com sucesso!')
            return redirect('core:settings')

        except Exception as e:
            messages.error(request, f'Erro ao atualizar configurações: {str(e)}')

    # Breadcrumbs
    breadcrumbs = [
        {'title': 'Configurações', 'url': None}
    ]

    context = {
        'profile': profile,
        'breadcrumbs': breadcrumbs,
    }

    return render(request, 'core/settings.html', context)


# ================================
# SHORTCUTS VIEWS
# ================================

@login_required
def shortcuts_list_view(request):
    """List all user shortcuts with pagination and filtering"""
    # Get user shortcuts
    shortcuts = Shortcut.objects.filter(user=request.user)

    # Apply filters
    search = request.GET.get('search', '').strip()
    category_id = request.GET.get('category')
    sort_by = request.GET.get('sort', '-created_at')

    if search:
        shortcuts = shortcuts.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(command__icontains=search)
        )

    if category_id:
        shortcuts = shortcuts.filter(category_id=category_id)

    # Sorting
    if sort_by in ['title', '-title', 'created_at', '-created_at', 'usage_count', '-usage_count']:
        shortcuts = shortcuts.order_by(sort_by)

    # Pagination
    paginator = Paginator(shortcuts, 20)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)

    # Get categories for filter
    categories = Category.objects.all()

    # Breadcrumbs
    breadcrumbs = [
        {'title': 'Meus Atalhos', 'url': None}
    ]

    context = {
        'shortcuts': page_obj.object_list,
        'page_obj': page_obj,
        'categories': categories,
        'current_search': search,
        'current_category': int(category_id) if category_id else None,
        'current_sort': sort_by,
        'breadcrumbs': breadcrumbs,
    }

    return render(request, 'shortcuts/list.html', context)


@login_required
def shortcuts_favorites_view(request):
    #"""List users favorite shortcuts"""
    # Get favorites (assuming there's a favorites relationship or field)
    favorites = Shortcut.objects.filter(
        user=request.user,
        is_favorite=True  # Assuming this field exists
    ).order_by('-created_at')

    # Pagination
    paginator = Paginator(favorites, 20)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)

    # Breadcrumbs
    breadcrumbs = [
        {'title': 'Meus Atalhos', 'url': reverse('shortcuts:list')},
        {'title': 'Favoritos', 'url': None}
    ]

    context = {
        'shortcuts': page_obj.object_list,
        'page_obj': page_obj,
        'breadcrumbs': breadcrumbs,
        'is_favorites': True,
    }

    return render(request, 'shortcuts/favorites.html', context)


def shortcuts_category_view(request, category_id):
    """View shortcuts by category"""
    category = get_object_or_404(Category, id=category_id)

    # Get shortcuts in this category
    if request.user.is_authenticated:
        shortcuts = Shortcut.objects.filter(
            category=category,
            user=request.user
        )
    else:
        shortcuts = Shortcut.objects.filter(
            category=category,
            is_public=True
        )

    # Pagination
    paginator = Paginator(shortcuts, 20)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)

    # Breadcrumbs
    breadcrumbs = [
        {'title': 'Categorias', 'url': reverse('shortcuts:categories')},
        {'title': category.name, 'url': None}
    ]

    context = {
        'category': category,
        'shortcuts': page_obj.object_list,
        'page_obj': page_obj,
        'breadcrumbs': breadcrumbs,
    }

    return render(request, 'shortcuts/category.html', context)


# ================================
# HELP & SUPPORT VIEWS
# ================================

def help_view(request):
    """Help and documentation page"""
    breadcrumbs = [
        {'title': 'Ajuda', 'url': None}
    ]

    context = {
        'breadcrumbs': breadcrumbs,
    }

    return render(request, 'core/help.html', context)


def faq_view(request):
    """FAQ page"""
    # Mock FAQ data - replace with database model if needed
    faqs = [
        {
            'question': 'Como criar um novo atalho?',
            'answer': 'Vá para a página "Meus Atalhos" e clique em "Novo Atalho". Preencha o título, comando e descrição.'
        },
        {
            'question': 'Como organizar atalhos em categorias?',
            'answer': 'Você pode criar categorias personalizadas e atribuir atalhos a elas durante a criação ou edição.'
        },
        {
            'question': 'Como usar a pesquisa avançada?',
            'answer': 'Use a barra de pesquisa no topo da página. Você pode filtrar por tipo (atalhos, categorias) e usar palavras-chave.'
        },
    ]

    breadcrumbs = [
        {'title': 'Ajuda', 'url': reverse('core:help')},
        {'title': 'FAQ', 'url': None}
    ]

    context = {
        'faqs': faqs,
        'breadcrumbs': breadcrumbs,
    }

    return render(request, 'core/faq.html', context)


def feedback_view(request):
    """Feedback and contact form"""
    if request.method == 'POST':
        try:
            name = request.POST.get('name', '')
            email = request.POST.get('email', '')
            message = request.POST.get('message', '')
            feedback_type = request.POST.get('type', 'general')

            if name and email and message:
                # Here you would typically save to database or send email
                # For now, just show success message
                messages.success(request, 'Obrigado pelo seu feedback! Entraremos em contato em breve.')
                return redirect('core:feedback')
            else:
                messages.error(request, 'Por favor, preencha todos os campos obrigatórios.')

        except Exception as e:
            messages.error(request, f'Erro ao enviar feedback: {str(e)}')

    breadcrumbs = [
        {'title': 'Feedback', 'url': None}
    ]

    context = {
        'breadcrumbs': breadcrumbs,
    }

    return render(request, 'core/feedback.html', context)


# ================================
# UTILITY FUNCTIONS
# ================================

def get_context_data(request, extra_context=None):
    """Get common context data for templates"""
    context = {
        'user': request.user,
        'is_authenticated': request.user.is_authenticated,
        'current_path': request.path,
        'current_url_name': request.resolver_match.url_name if request.resolver_match else None,
    }

    if request.user.is_authenticated:
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        context['user_profile'] = profile

    if extra_context:
        context.update(extra_context)

    return context


# ================================
# API ENDPOINTS FOR COMPONENTS
# ================================

@require_GET
def notifications_api(request):
    """API endpoint for toast notifications data"""
    # This would typically fetch from a notifications model
    notifications = []

    if request.user.is_authenticated:
        # Mock notifications - replace with actual model queries
        notifications = [
            {
                'type': 'info',
                'title': 'Bem-vindo!',
                'message': 'Explore os recursos do Symplifika',
                'timestamp': timezone.now().isoformat(),
            }
        ]

    return JsonResponse({'notifications': notifications})


@login_required
@require_POST
@csrf_exempt
def mark_notification_read_api(request):
    """API endpoint to mark notification as read"""
    try:
        data = json.loads(request.body)
        notification_id = data.get('id')

        # Mark notification as read (implement based on your notification model)
        # Notification.objects.filter(id=notification_id, user=request.user).update(is_read=True)

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_GET
@cache_page(60 * 15)  # Cache for 15 minutes
def user_menu_data_api(request):
    """API endpoint for user menu data"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Get user statistics
    shortcuts_count = Shortcut.objects.filter(user=request.user).count() if hasattr(request.user, 'shortcuts') else 0

    data = {
        'user': {
            'username': request.user.username,
            'email': request.user.email,
            'full_name': request.user.get_full_name() or request.user.username,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        },
        'profile': {
            'avatar': profile.avatar.url if profile.avatar else None,
            'plan': profile.plan.name if hasattr(profile, 'plan') and profile.plan else 'Gratuito',
            'theme': getattr(profile, 'theme', 'light'),
        },
        'stats': {
            'shortcuts_count': shortcuts_count,
        },
        'urls': {
            'profile': reverse('users:profile'),
            'settings': reverse('core:settings'),
            'help': reverse('core:help'),
            'feedback': reverse('core:feedback'),
            'logout': reverse('users:logout'),
        }
    }

    return JsonResponse(data)


# ================================
# ERROR HANDLERS
# ================================

def handler404(request, exception):
    """Custom 404 error handler"""
    breadcrumbs = [
        {'title': 'Página não encontrada', 'url': None}
    ]

    context = get_context_data(request, {
        'breadcrumbs': breadcrumbs,
        'error_code': 404,
        'error_message': 'A página que você está procurando não foi encontrada.'
    })

    return render(request, '404.html', context, status=404)


def handler500(request):
    """Custom 500 error handler"""
    breadcrumbs = [
        {'title': 'Erro interno', 'url': None}
    ]

    context = get_context_data(request, {
        'breadcrumbs': breadcrumbs,
        'error_code': 500,
        'error_message': 'Ocorreu um erro interno. Tente novamente mais tarde.'
    })

    return render(request, '500.html', context, status=500)


# ================================
# SETTINGS API ENDPOINTS
# ================================

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def api_profile(request):
    """API endpoint for user profile management"""
    try:
        from users.models import UserProfile
        from django.contrib.auth.models import User

        profile, created = UserProfile.objects.get_or_create(user=request.user)

        if request.method == 'GET':
            return Response({
                'success': True,
                'data': {
                    'user': {
                        'id': request.user.id,
                        'username': request.user.username,
                        'email': request.user.email,
                        'first_name': request.user.first_name,
                        'last_name': request.user.last_name,
                        'date_joined': request.user.date_joined.isoformat(),
                        'last_login': request.user.last_login.isoformat() if request.user.last_login else None,
                    },
                    'profile': {
                        'theme': profile.theme,
                        'email_notifications': profile.email_notifications,
                        'ai_enabled': profile.ai_enabled,
                        'ai_model_preference': profile.ai_model_preference,
                        'plan': profile.plan,
                        'max_shortcuts': profile.max_shortcuts,
                        'max_ai_requests': profile.max_ai_requests,
                        'ai_requests_used': profile.ai_requests_used,
                        'total_shortcuts_used': profile.total_shortcuts_used,
                        'time_saved_minutes': profile.time_saved_minutes,
                    }
                }
            })

        elif request.method in ['PUT', 'PATCH']:
            data = request.data
            updated_fields = []

            # Update user fields
            user_fields = ['first_name', 'last_name', 'email']
            for field in user_fields:
                if field in data:
                    setattr(request.user, field, data[field])
                    updated_fields.append(field)

            if updated_fields:
                request.user.save()

            # Update profile fields
            profile_fields = ['theme', 'email_notifications', 'ai_enabled', 'ai_model_preference']
            profile_updated = []
            for field in profile_fields:
                if field in data:
                    setattr(profile, field, data[field])
                    profile_updated.append(field)

            if profile_updated:
                profile.save()

            return Response({
                'success': True,
                'message': 'Perfil atualizado com sucesso!',
                'updated_fields': updated_fields + profile_updated
            })

    except Exception as e:
        import traceback
        return Response({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def api_account(request):
    """API endpoint for account settings"""
    try:
        from users.models import UserProfile

        profile, created = UserProfile.objects.get_or_create(user=request.user)

        if request.method == 'GET':
            return Response({
                'success': True,
                'data': {
                    'email': request.user.email,
                    'username': request.user.username,
                    'plan': profile.plan,
                    'date_joined': request.user.date_joined.isoformat(),
                    'last_login': request.user.last_login.isoformat() if request.user.last_login else None,
                    'is_active': request.user.is_active,
                    'email_notifications': profile.email_notifications,
                    'theme': profile.theme,
                }
            })

        elif request.method in ['PUT', 'PATCH']:
            data = request.data
            updated_fields = []

            # Update email if provided
            if 'email' in data:
                from django.contrib.auth.models import User
                new_email = data['email']

                # Check if email is already in use
                if User.objects.filter(email=new_email).exclude(id=request.user.id).exists():
                    return Response({
                        'success': False,
                        'error': 'Este email já está em uso por outro usuário.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                request.user.email = new_email
                request.user.save()
                updated_fields.append('email')

            # Update profile settings
            profile_fields = ['email_notifications', 'theme']
            for field in profile_fields:
                if field in data:
                    setattr(profile, field, data[field])
                    updated_fields.append(field)

            if any(field in profile_fields for field in updated_fields):
                profile.save()

            return Response({
                'success': True,
                'message': 'Configurações da conta atualizadas com sucesso!',
                'updated_fields': updated_fields
            })

    except Exception as e:
        import traceback
        return Response({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_change_password(request):
    """API endpoint for changing password"""
    try:
        data = request.data
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if not all([current_password, new_password, confirm_password]):
            return Response({
                'success': False,
                'error': 'Todos os campos são obrigatórios.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check current password
        if not request.user.check_password(current_password):
            return Response({
                'success': False,
                'error': 'Senha atual incorreta.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if new passwords match
        if new_password != confirm_password:
            return Response({
                'success': False,
                'error': 'As novas senhas não coincidem.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate password strength
        if len(new_password) < 8:
            return Response({
                'success': False,
                'error': 'A nova senha deve ter pelo menos 8 caracteres.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Change password
        request.user.set_password(new_password)
        request.user.save()

        return Response({
            'success': True,
            'message': 'Senha alterada com sucesso!'
        })

    except Exception as e:
        import traceback
        return Response({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def api_notifications_preferences(request):
    """API endpoint for notification preferences"""
    try:
        from users.models import UserProfile

        profile, created = UserProfile.objects.get_or_create(user=request.user)

        if request.method == 'GET':
            return Response({
                'success': True,
                'data': {
                    'email_notifications': profile.email_notifications,
                    'push_notifications': getattr(profile, 'push_notifications', True),
                    'marketing_emails': getattr(profile, 'marketing_emails', False),
                    'security_alerts': getattr(profile, 'security_alerts', True),
                    'product_updates': getattr(profile, 'product_updates', True),
                }
            })

        elif request.method in ['PUT', 'PATCH']:
            data = request.data
            updated_fields = []

            # Update notification preferences
            notification_fields = [
                'email_notifications', 'push_notifications',
                'marketing_emails', 'security_alerts', 'product_updates'
            ]

            for field in notification_fields:
                if field in data:
                    setattr(profile, field, data[field])
                    updated_fields.append(field)

            if updated_fields:
                profile.save()

            return Response({
                'success': True,
                'message': 'Preferências de notificação atualizadas com sucesso!',
                'updated_fields': updated_fields
            })

    except Exception as e:
        import traceback
        return Response({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_settings_config(request):
    """API endpoint for settings configuration data"""
    try:
        from users.models import UserProfile

        profile, created = UserProfile.objects.get_or_create(user=request.user)

        # Get environment info
        environment_info = {
            'is_production': not django_settings.DEBUG,
            'api_base_url': request.build_absolute_uri('/api/'),
            'frontend_url': request.build_absolute_uri('/'),
            'stripe': {
                'configured': bool(getattr(django_settings, 'STRIPE_PUBLISHABLE_KEY', None))
            }
        }

        # API endpoints configuration
        api_endpoints = {
            'auth': {
                'login': '/api/auth/login/',
                'register': '/api/auth/register/',
                'logout': '/api/auth/logout/',
            },
            'shortcuts': {
                'list': '/shortcuts/api/shortcuts/',
                'create': '/shortcuts/api/shortcuts/',
                'categories': '/shortcuts/api/categories/',
            },
            'payments': {
                'create_checkout': '/payments/create-checkout-session/',
                'plans': '/api/profile/plan-pricing/',
            },
            'settings': {
                'profile': '/api/profile/',
                'account': '/api/account/',
                'change_password': '/api/change-password/',
                'notifications': '/api/notifications-preferences/',
            }
        }

        return Response({
            'success': True,
            'data': {
                'environment': environment_info,
                'endpoints': api_endpoints,
                'user': {
                    'plan': profile.plan,
                    'theme': profile.theme,
                    'email_notifications': profile.email_notifications,
                    'ai_enabled': profile.ai_enabled,
                }
            }
        })

    except Exception as e:
        import traceback
        return Response({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# PROFILE MANAGEMENT APIs - Sistema completo de gerenciamento de perfil
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_upload_avatar(request):
    """API endpoint for avatar upload with image processing"""
    try:
        if 'avatar' not in request.FILES:
            return Response({
                'success': False,
                'error': 'Nenhum arquivo de avatar fornecido'
            }, status=status.HTTP_400_BAD_REQUEST)

        avatar_file = request.FILES['avatar']

        # Validações do arquivo
        max_size = 5 * 1024 * 1024  # 5MB
        if avatar_file.size > max_size:
            return Response({
                'success': False,
                'error': 'Arquivo muito grande. Máximo permitido: 5MB'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validar tipo de arquivo
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
        if avatar_file.content_type not in allowed_types:
            return Response({
                'success': False,
                'error': 'Tipo de arquivo não permitido. Use: JPEG, PNG, GIF ou WebP'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get or create profile
        from users.models import UserProfile
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        # Remove avatar anterior se existir
        if profile.avatar:
            profile.delete_avatar()

        # Salva o novo avatar
        profile.avatar = avatar_file
        profile.save()

        return Response({
            'success': True,
            'message': 'Avatar atualizado com sucesso!',
            'avatar_url': profile.get_avatar_url(),
            'data': {
                'avatar_url': profile.get_avatar_url(),
                'has_avatar': bool(profile.avatar)
            }
        })

    except Exception as e:
        import traceback
        return Response({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def api_delete_avatar(request):
    """API endpoint for avatar deletion"""
    try:
        from users.models import UserProfile
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        if not profile.avatar:
            return Response({
                'success': False,
                'error': 'Nenhum avatar para remover'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Remove o avatar
        profile.delete_avatar()

        return Response({
            'success': True,
            'message': 'Avatar removido com sucesso!',
            'data': {
                'avatar_url': None,
                'has_avatar': False,
                'initial': profile.get_avatar_or_initial()
            }
        })

    except Exception as e:
        import traceback
        return Response({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def api_profile_extended(request):
    """API endpoint for extended profile management"""
    try:
        from users.models import UserProfile
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        if request.method == 'GET':
            return Response({
                'success': True,
                'data': {
                    'user': {
                        'id': request.user.id,
                        'username': request.user.username,
                        'email': request.user.email,
                        'first_name': request.user.first_name,
                        'last_name': request.user.last_name,
                        'full_name': request.user.get_full_name(),
                        'date_joined': request.user.date_joined.isoformat(),
                        'last_login': request.user.last_login.isoformat() if request.user.last_login else None,
                    },
                    'profile': {
                        'avatar_url': profile.get_avatar_url(),
                        'has_avatar': bool(profile.avatar),
                        'bio': profile.bio,
                        'location': profile.location,
                        'website': profile.website,
                        'birth_date': profile.birth_date.isoformat() if profile.birth_date else None,
                        'age': profile.age,
                        'public_profile': profile.public_profile,
                        'show_email': profile.show_email,
                        'plan': profile.plan,
                        'theme': profile.theme,
                        'email_notifications': profile.email_notifications,
                        'ai_enabled': profile.ai_enabled,
                        'ai_model_preference': profile.ai_model_preference,
                        'created_at': profile.created_at.isoformat(),
                        'updated_at': profile.updated_at.isoformat(),
                    },
                    'stats': {
                        'shortcuts_count': request.user.shortcuts.filter(is_active=True).count(),
                        'total_usage': sum(s.use_count for s in request.user.shortcuts.all()),
                        'time_saved_minutes': profile.time_saved_minutes,
                        'time_saved_hours': round(profile.time_saved_minutes / 60, 1),
                        'ai_requests_used': profile.ai_requests_used,
                        'ai_requests_remaining': max(0, profile.max_ai_requests - profile.ai_requests_used) if profile.max_ai_requests > 0 else -1,
                    }
                }
            })

        elif request.method in ['PUT', 'PATCH']:
            data = request.data
            updated_fields = []

            # Update user fields
            user_fields = ['first_name', 'last_name', 'email']
            for field in user_fields:
                if field in data:
                    # Validação especial para email
                    if field == 'email':
                        from django.contrib.auth.models import User
                        if User.objects.filter(email=data[field]).exclude(id=request.user.id).exists():
                            return Response({
                                'success': False,
                                'error': 'Este email já está em uso por outro usuário'
                            }, status=status.HTTP_400_BAD_REQUEST)

                    setattr(request.user, field, data[field])
                    updated_fields.append(field)

            # Update profile fields
            profile_fields = [
                'bio', 'location', 'website', 'birth_date',
                'public_profile', 'show_email', 'theme',
                'email_notifications', 'ai_enabled', 'ai_model_preference'
            ]

            for field in profile_fields:
                if field in data:
                    # Validação especial para bio
                    if field == 'bio' and len(data[field]) > 500:
                        return Response({
                            'success': False,
                            'error': 'Biografia deve ter no máximo 500 caracteres'
                        }, status=status.HTTP_400_BAD_REQUEST)

                    # Validação para birth_date
                    if field == 'birth_date' and data[field]:
                        from datetime import datetime
                        try:
                            birth_date = datetime.fromisoformat(data[field].replace('Z', '+00:00')).date()
                            setattr(profile, field, birth_date)
                        except ValueError:
                            return Response({
                                'success': False,
                                'error': 'Formato de data inválido para data de nascimento'
                            }, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        setattr(profile, field, data[field])

                    updated_fields.append(field)

            # Save changes
            if any(field in user_fields for field in updated_fields):
                request.user.save()

            if any(field in profile_fields for field in updated_fields):
                profile.save()

            return Response({
                'success': True,
                'message': 'Perfil atualizado com sucesso!',
                'updated_fields': updated_fields,
                'data': {
                    'user': {
                        'full_name': request.user.get_full_name(),
                        'email': request.user.email,
                    },
                    'profile': {
                        'bio': profile.bio,
                        'location': profile.location,
                        'website': profile.website,
                        'age': profile.age,
                        'public_profile': profile.public_profile,
                        'show_email': profile.show_email,
                    }
                }
            })

    except Exception as e:
        import traceback
        return Response({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
