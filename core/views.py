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
    
    return Response({
        'total_shortcuts': total_shortcuts,
        'active_shortcuts': active_shortcuts,
        'categories_count': categories_count,
        'monthly_usage': monthly_usage,
        'time_saved': f"{time_saved_hours}h",
        'time_saved_minutes': time_saved_minutes,
        'ai_requests_used': profile.ai_requests_used,
        'ai_requests_remaining': max(0, profile.max_ai_requests - profile.ai_requests_used),
        'plan': profile.get_plan_display(),
    })


@login_required
def shortcuts(request):
    """Shortcuts management page"""
    return render(request, 'dashboard.html')


# Authentication views moved to users app - no redirects needed


@login_required
def profile(request, user_id=None):
    """Profile view - shows user profile with stats and activity"""
    from django.shortcuts import get_object_or_404
    from django.contrib.auth.models import User
    from django.db.models import Sum, Count

    # If user_id is provided, show that user's profile, otherwise show current user's profile
    if user_id:
        profile_user = get_object_or_404(User, id=user_id)
    else:
        profile_user = request.user

    # Calculate statistics
    shortcuts_count = profile_user.shortcuts.filter(is_active=True).count()
    total_usage = profile_user.shortcuts.aggregate(total=Sum('use_count'))['total'] or 0
    time_saved = profile_user.userprofile.time_saved_minutes / 60 if hasattr(profile_user, 'userprofile') else 0

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
        messages.success(request, 'Thank you for your feedback!')
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
                shortcuts = Shortcut.objects.filter(user=request.user)
            else:
                shortcuts = Shortcut.objects.filter(is_public=True)

            shortcuts = shortcuts.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(command__icontains=query)
            )[:limit//2 if filter_type == 'all' else limit]

            for shortcut in shortcuts:
                suggestions.append({
                    'text': shortcut.title,
                    'type': 'shortcut',
                    'description': shortcut.description[:100] if shortcut.description else None,
                    'url': reverse('shortcuts:detail', args=[shortcut.id]) if hasattr(shortcut, 'get_absolute_url') else None
                })

        # Get categories suggestions
        if filter_type in ['all', 'categories']:
            categories = Category.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )[:limit//2 if filter_type == 'all' else limit]

            for category in categories:
                suggestions.append({
                    'text': category.name,
                    'type': 'category',
                    'description': category.description[:100] if category.description else None,
                    'url': reverse('shortcuts:category', args=[category.id]) if hasattr(category, 'get_absolute_url') else None
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

    # Simple context for testing
    context = {
        'profile_user': profile_user,
        'profile': profile,
        'shortcuts_count': 0,
        'categories_count': 0,
        'favorites_count': 0,
        'recent_shortcuts': [],
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

    return render(request, 'users/settings.html', context)


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
    """List user's favorite shortcuts"""
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
