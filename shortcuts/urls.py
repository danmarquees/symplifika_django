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
    # URLs customizadas específicas (devem vir ANTES do router)
    path('shortcuts/search/', views.ShortcutViewSet.as_view({'post': 'search'}), name='shortcut-search'),
    path('shortcuts/stats/', views.ShortcutViewSet.as_view({'get': 'stats'}), name='shortcut-stats'),
    path('shortcuts/most-used/', views.ShortcutViewSet.as_view({'get': 'most_used'}), name='shortcut-most-used'),
    path('shortcuts/bulk-action/', views.ShortcutViewSet.as_view({'post': 'bulk_action'}), name='shortcut-bulk-action'),
    path('shortcuts/<int:pk>/use/', views.ShortcutViewSet.as_view({'post': 'use'}), name='shortcut-use'),
    path('shortcuts/<int:pk>/regenerate-ai/', views.ShortcutViewSet.as_view({'post': 'regenerate_ai'}), name='shortcut-regenerate-ai'),
    path('shortcuts/<int:pk>/usage-history/', views.ShortcutViewSet.as_view({'get': 'usage_history'}), name='shortcut-usage-history'),
    path('categories/<int:pk>/shortcuts/', views.CategoryViewSet.as_view({'get': 'shortcuts'}), name='category-shortcuts'),
    
    # URLs do router (API) - incluir depois das URLs específicas
    path('', include(router.urls)),
]
