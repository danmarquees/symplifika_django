from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router para ViewSets
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'profile', views.UserProfileViewSet, basename='profile')

app_name = 'users'

urlpatterns = [
    # Autenticação (HTML Templates)
    path('auth/register/', views.register_template_view, name='register'),
    path('auth/login/', views.login_template_view, name='login'),
    path('auth/logout/', views.logout_template_view, name='logout'),

    # Plan Management (HTML Templates)
    path('plan/upgrade/', views.plan_upgrade_view, name='plan_upgrade'),
    path('plan/upgrade/payment/<int:upgrade_id>/', views.plan_upgrade_payment_view, name='plan_upgrade_payment'),
    path('subscription/', views.subscription_management_view, name='subscription_management'),
    path('subscription-success/', views.subscription_success_view, name='subscription_success'),

    # Autenticação (API)
    path('api/auth/register/', views.register, name='api-register'),
    path('api/auth/login/', views.login_view, name='api-login'),
    path('api/auth/logout/', views.logout_view, name='api-logout'),

    # Reset de senha
    path('auth/password-reset/', views.password_reset_request, name='password-reset'),
    path('auth/password-reset-confirm/', views.password_reset_confirm, name='password-reset-confirm'),

    # Dashboard
    path('dashboard/', views.dashboard_data, name='dashboard'),

    # URLs do router
    path('api/', include(router.urls)),

    # URLs customizadas para usuários
    path('api/users/me/', views.UserViewSet.as_view({'get': 'me'}), name='user-me'),
    path('api/users/update-profile/', views.UserViewSet.as_view({'put': 'update_profile', 'patch': 'update_profile'}), name='user-update-profile'),
    path('api/users/change-password/', views.UserViewSet.as_view({'post': 'change_password'}), name='user-change-password'),
    path('api/users/stats/', views.UserViewSet.as_view({'get': 'stats'}), name='user-stats'),
    path('api/users/delete-account/', views.UserViewSet.as_view({'post': 'delete_account'}), name='user-delete-account'),

    # URLs customizadas para perfil
    path('api/profile/upgrade-plan/', views.UserProfileViewSet.as_view({'post': 'upgrade_plan'}), name='profile-upgrade-plan'),
    path('api/profile/plan-pricing/', views.UserProfileViewSet.as_view({'get': 'plan_pricing'}), name='profile-plan-pricing'),
    path('api/profile/subscription-info/', views.UserProfileViewSet.as_view({'get': 'subscription_info'}), name='profile-subscription-info'),
    path('api/profile/payment-methods/', views.UserProfileViewSet.as_view({'get': 'payment_methods'}), name='profile-payment-methods'),
    path('api/profile/payment-history/', views.UserProfileViewSet.as_view({'get': 'payment_history'}), name='profile-payment-history'),
    path('api/profile/cancel-subscription/', views.UserProfileViewSet.as_view({'post': 'cancel_subscription'}), name='profile-cancel-subscription'),
    path('api/profile/process-payment/', views.UserProfileViewSet.as_view({'post': 'process_payment'}), name='profile-process-payment'),
    path('api/profile/reset-monthly-counters/', views.UserProfileViewSet.as_view({'post': 'reset_monthly_counters'}), name='profile-reset-counters'),
]
