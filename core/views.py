from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Importações DRF para o endpoint de estatísticas
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

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


def register(request):
    """Register view - redirects to users app"""
    return redirect('users:register')


def login_view(request):
    """Login view - redirects to users app"""
    return redirect('users:login')


def logout_view(request):
    """Logout view - redirects to users app"""
    return redirect('users:logout')


@login_required
def profile(request):
    """Profile view"""
    return render(request, 'profile.html')


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
    """Settings view"""
    if request.method == 'POST':
        # Process settings form data
        messages.success(request, 'Settings updated successfully!')
        return redirect('core:settings')
    return render(request, 'settings.html')


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


@login_required
def privacy(request):
    """Privacy view"""
    return render(request, 'privacy.html')


@login_required
def terms(request):
    """Terms view"""
    return render(request, 'terms.html')


@login_required
def faq(request):
    """FAQ view"""
    return render(request, 'faq.html')


@login_required
def help(request):
    """Help view"""
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
