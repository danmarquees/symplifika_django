from django.urls import path
from . import views
from .api import MarkAllReadAPI, NotificationDeleteAPI, NotificationMarkReadAPI

app_name = 'notifications'

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='list'),
    path('settings/', views.NotificationSettingsView.as_view(), name='settings'),
    path('api/notifications/', views.NotificationListAPI.as_view(), name='api-notifications-list'),
    path('api/notifications/mark-all-read/', MarkAllReadAPI.as_view(), name='api-notifications-mark-all-read'),
    path('api/notifications/<int:pk>/', NotificationDeleteAPI.as_view(), name='api-notifications-delete'),
    path('api/notifications/<int:pk>/read/', NotificationMarkReadAPI.as_view(), name='api-notifications-mark-read'),
]
