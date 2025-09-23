from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Main pages
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('shortcuts/', views.shortcuts, name='shortcuts'),
    path('dashboard/buscar/', views.search_view, name='search_bar'),

    # Search functionality
    path('search/', views.search_view, name='search'),
    path('api/search/suggestions/', views.search_suggestions_api, name='search-suggestions'),

    # API endpoints
    path('api/status/', views.api_status, name='api-status'),
    path('api/health/', views.health_check, name='health-check'),
    path('api/statistics/', views.statistics_view, name='api-statistics'),
    path('api/dashboard/stats/', views.dashboard_stats, name='api-dashboard-stats'),
    path('api/plan/status/', views.plan_status, name='api-plan-status'),
    path('api/users/<int:user_id>/activity/', views.user_activity_api, name='user-activity-api'),
    path('api/users/<int:user_id>/categories/', views.user_categories_api, name='user-categories-api'),
    path('api/users/usage-stats/', views.usage_stats_api, name='usage-stats-api'),
    path('api/payments/billing-history/', views.billing_history_api, name='billing-history-api'),

    # Settings API endpoints
    path('api/profile/', views.api_profile, name='api-profile'),
    path('api/account/', views.api_account, name='api-account'),
    path('api/change-password/', views.api_change_password, name='api-change-password'),
    path('api/notifications-preferences/', views.api_notifications_preferences, name='api-notifications-preferences'),
    path('api/settings/config/', views.api_settings_config, name='api-settings-config'),

    # Extended Profile Management APIs
    path('api/profile/extended/', views.api_profile_extended, name='api-profile-extended'),
    path('api/profile/avatar/upload/', views.api_upload_avatar, name='api-upload-avatar'),
    path('api/profile/avatar/delete/', views.api_delete_avatar, name='api-delete-avatar'),

    # Authentication handled by users app

    # Profile management
    path('profile/', views.profile_view, name='profile'),
    path('profile/<int:user_id>/', views.profile_view, name='profile-user'),
    path('profile/edit/', views.edit_profile, name='edit-profile'),
    path('profile/edit/password/', views.change_password, name='change-password'),
    path('profile/edit/avatar/', views.change_avatar, name='change-avatar'),
    path('profile/edit/avatar/delete/', views.delete_avatar, name='delete-avatar'),
    path('profile/edit/avatar/upload/', views.upload_avatar, name='upload-avatar'),
    path('profile/edit/avatar/upload/delete/', views.delete_uploaded_avatar, name='delete-uploaded-avatar'),
    path('profile/edit/avatar/upload/delete/<int:avatar_id>/', views.delete_uploaded_avatar, name='delete-uploaded-avatar-id'),

    # App pages
    path('support/', views.support, name='support'),
    path('feedback/', views.feedback_view, name='feedback'),
    path('settings/', views.settings_view, name='settings'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('privacy/', views.privacy_policy_view, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('faq/', views.faq, name='faq'),
    path('help/', views.help, name='help'),
    path('pricing/', views.pricing, name='pricing'),

    # Template component APIs
    path('api/notifications/', views.notifications_api, name='notifications-api'),
    path('api/notifications/mark-read/', views.mark_notification_read_api, name='mark-notification-read'),
    path('api/user-menu/', views.user_menu_data_api, name='user-menu-data'),

    # Static files
    path('favicon.ico', views.favicon_view, name='favicon'),
]
