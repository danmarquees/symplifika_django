from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import template_views

# Router para ViewSets
router = DefaultRouter()
router.register(r"users", views.UserViewSet, basename="user")
router.register(r"profile", views.UserProfileViewSet, basename="profile")

app_name = "users"

urlpatterns = [
    # Autenticação (HTML Templates)
    path("auth/register/", views.register_template_view, name="register"),
    path("auth/login/", views.login_template_view, name="login"),
    path("auth/logout/", views.logout_template_view, name="logout"),
    # Plan Management (HTML Templates)
    path("plan/upgrade/", views.plan_upgrade_view, name="plan_upgrade"),
    path(
        "plan/upgrade/payment/<int:upgrade_id>/",
        views.plan_upgrade_payment_view,
        name="plan_upgrade_payment",
    ),
    path("subscription/", views.subscription_management_view, name="subscription"),
    path(
        "subscription/management/",
        views.subscription_management_view,
        name="subscription_management",
    ),
    path(
        "subscription-success/",
        views.subscription_success_view,
        name="subscription_success",
    ),
    # Autenticação (API)
    path("api/auth/register/", views.register, name="api-register"),
    path("api/auth/login/", views.login_view, name="api-login"),
    path("api/auth/logout/", views.logout_view, name="api-logout"),
    # Reset de senha (HTML Template)
    path(
        "auth/password-reset/",
        views.password_reset_template_view,
        name="password-reset",
    ),
    path(
        "auth/password-reset-confirm/",
        views.password_reset_confirm,
        name="password-reset-confirm",
    ),
    # Reset de senha (API)
    path(
        "api/auth/password-reset/",
        views.password_reset_request,
        name="api-password-reset",
    ),
    path(
        "api/auth/password-reset-confirm/",
        views.password_reset_confirm,
        name="api-password-reset-confirm",
    ),
    # Dashboard
    path("dashboard/", views.dashboard_data, name="dashboard"),
    # URLs do router
    path("api/", include(router.urls)),
    # Template views
    path("profile/", template_views.profile_view, name="profile"),
    path("profile/<int:user_id>/", template_views.profile_view, name="profile-user"),
    path("settings/", template_views.settings_view, name="settings"),
    path("edit-profile/", template_views.edit_profile_view, name="edit-profile"),
    path("change-avatar/", template_views.change_avatar_view, name="change-avatar"),
    path("delete-avatar/", template_views.delete_avatar_view, name="delete-avatar"),
    # Template API endpoints
    path(
        "api/profile/update/",
        template_views.api_update_profile,
        name="api-update-profile",
    ),
    path("api/user/stats/", template_views.api_user_stats, name="api-user-stats"),
    path(
        "api/user/menu-data/",
        template_views.api_user_menu_data,
        name="api-user-menu-data",
    ),
    path("api/theme/toggle/", template_views.api_toggle_theme, name="api-toggle-theme"),
    # Authentication URLs (template views)
    path("login/", template_views.login_view, name="login"),
    path("register/", template_views.register_view, name="register"),
    path("logout/", template_views.logout_view, name="logout"),
    # URLs customizadas para usuários
    path("api/users/me/", views.UserViewSet.as_view({"get": "me"}), name="user-me"),
    path(
        "api/users/update-profile/",
        views.UserViewSet.as_view({"put": "update_profile", "patch": "update_profile"}),
        name="user-update-profile",
    ),
    path(
        "api/users/change-password/",
        views.UserViewSet.as_view({"post": "change_password"}),
        name="user-change-password",
    ),
    path(
        "api/users/stats/",
        views.UserViewSet.as_view({"get": "stats"}),
        name="user-stats",
    ),
    path(
        "api/users/delete-account/",
        views.UserViewSet.as_view({"post": "delete_account"}),
        name="user-delete-account",
    ),
    # URLs customizadas para perfil
    path(
        "api/profile/upgrade-plan/",
        views.UserProfileViewSet.as_view({"post": "upgrade_plan"}),
        name="profile-upgrade-plan",
    ),
    path(
        "api/profile/plan-pricing/",
        views.UserProfileViewSet.as_view({"get": "plan_pricing"}),
        name="profile-plan-pricing",
    ),
    path(
        "api/profile/subscription-info/",
        views.UserProfileViewSet.as_view({"get": "subscription_info"}),
        name="profile-subscription-info",
    ),
    path(
        "api/profile/payment-methods/",
        views.UserProfileViewSet.as_view({"get": "payment_methods"}),
        name="profile-payment-methods",
    ),
    path(
        "api/profile/payment-history/",
        views.UserProfileViewSet.as_view({"get": "payment_history"}),
        name="profile-payment-history",
    ),
    path(
        "api/profile/cancel-subscription/",
        views.UserProfileViewSet.as_view({"post": "cancel_subscription"}),
        name="profile-cancel-subscription",
    ),
    path(
        "api/profile/process-payment/",
        views.UserProfileViewSet.as_view({"post": "process_payment"}),
        name="profile-process-payment",
    ),
    path(
        "api/profile/reset-monthly-counters/",
        views.UserProfileViewSet.as_view({"post": "reset_monthly_counters"}),
        name="profile-reset-counters",
    ),
    # Sistema de Indicação (API)
    path("api/referral/create/", views.create_referral, name="api-create-referral"),
    path(
        "api/referral/dashboard/",
        views.referral_dashboard,
        name="api-referral-dashboard",
    ),
    path(
        "api/referral/generate-code/",
        views.generate_referral_code,
        name="api-generate-referral-code",
    ),
    path(
        "api/referral/leaderboard/",
        views.referral_leaderboard,
        name="api-referral-leaderboard",
    ),
    path(
        "api/auth/register-with-referral/",
        views.register_with_referral,
        name="api-register-with-referral",
    ),
    # Sistema de Indicação (HTML Templates)
    path("referral/", views.referral_template_view, name="referral"),
    # Chrome Extension Auto-Auth
    path(
        "api/auth/check-session/",
        views.check_session_auth,
        name="api-check-session-auth",
    ),
    path(
        "api/auth/extension-heartbeat/",
        views.extension_heartbeat,
        name="api-extension-heartbeat",
    ),
]
