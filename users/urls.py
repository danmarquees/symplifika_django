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
    path('api/profile/reset-monthly-counters/', views.UserProfileViewSet.as_view({'post': 'reset_monthly_counters'}), name='profile-reset-counters'),
]
