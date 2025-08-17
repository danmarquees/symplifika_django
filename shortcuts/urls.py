from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router para ViewSets
router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'shortcuts', views.ShortcutViewSet, basename='shortcut')
router.register(r'usage', views.ShortcutUsageViewSet, basename='usage')
router.register(r'ai-logs', views.AIEnhancementLogViewSet, basename='ai-logs')

app_name = 'shortcuts'

urlpatterns = [
    # URLs do router
    path('api/', include(router.urls)),

    # URLs customizadas adicionais se necessário
    path('api/shortcuts/search/', views.ShortcutViewSet.as_view({'post': 'search'}), name='shortcut-search'),
    path('api/shortcuts/stats/', views.ShortcutViewSet.as_view({'get': 'stats'}), name='shortcut-stats'),
    path('api/shortcuts/most-used/', views.ShortcutViewSet.as_view({'get': 'most_used'}), name='shortcut-most-used'),
    path('api/shortcuts/bulk-action/', views.ShortcutViewSet.as_view({'post': 'bulk_action'}), name='shortcut-bulk-action'),
    path('api/shortcuts/<int:pk>/use/', views.ShortcutViewSet.as_view({'post': 'use'}), name='shortcut-use'),
    path('api/shortcuts/<int:pk>/regenerate-ai/', views.ShortcutViewSet.as_view({'post': 'regenerate_ai'}), name='shortcut-regenerate-ai'),
    path('api/shortcuts/<int:pk>/usage-history/', views.ShortcutViewSet.as_view({'get': 'usage_history'}), name='shortcut-usage-history'),
    path('api/categories/<int:pk>/shortcuts/', views.CategoryViewSet.as_view({'get': 'shortcuts'}), name='category-shortcuts'),
]
