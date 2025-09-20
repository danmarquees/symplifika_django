from django.urls import path
from .api import (
    NotificationListAPI,
    MarkAllReadAPI,
    NotificationDeleteAPI,
    NotificationMarkReadAPI,
)

urlpatterns = [
    path('', NotificationListAPI.as_view(), name='notification-list'),
    path('create/', NotificationListAPI.as_view(), name='notification-create'),
    path('unread-count/', NotificationListAPI.as_view(), name='notification-unread-count'),
    path('mark-all-read/', MarkAllReadAPI.as_view(), name='notification-mark-all-read'),
    path('<int:pk>/', NotificationDeleteAPI.as_view(), name='notification-delete'),
    path('<int:pk>/read/', NotificationMarkReadAPI.as_view(), name='notification-mark-read'),
]
