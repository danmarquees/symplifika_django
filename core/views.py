from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
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
    return render(request, 'app.html')


@login_required
def shortcuts(request):
    """Shortcuts management page"""
    return render(request, 'app.html')


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
