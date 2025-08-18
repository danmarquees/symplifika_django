from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Main pages
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # API endpoints
    path('api/status/', views.api_status, name='api-status'),
    path('api/health/', views.health_check, name='health-check'),
    path('api/statistics/', views.statistics_view, name='api-statistics'),

    # Authentication (redirects to users app)
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Profile management
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit-profile'),
    path('profile/edit/password/', views.change_password, name='change-password'),
    path('profile/edit/avatar/', views.change_avatar, name='change-avatar'),
    path('profile/edit/avatar/delete/', views.delete_avatar, name='delete-avatar'),
    path('profile/edit/avatar/upload/', views.upload_avatar, name='upload-avatar'),
    path('profile/edit/avatar/upload/delete/', views.delete_uploaded_avatar, name='delete-uploaded-avatar'),
    path('profile/edit/avatar/upload/delete/<int:avatar_id>/', views.delete_uploaded_avatar, name='delete-uploaded-avatar-id'),

    # App pages
    path('support/', views.support, name='support'),
    path('feedback/', views.feedback, name='feedback'),
    path('settings/', views.settings, name='settings'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('faq/', views.faq, name='faq'),
    path('help/', views.help, name='help'),
    path('pricing/', views.pricing, name='pricing'),

    # Static files
    path('favicon.ico', views.favicon_view, name='favicon'),
]
