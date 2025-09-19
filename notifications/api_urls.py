from django.urls import path
from .api import (
    NotificationListAPI,
    MarkAllReadAPI,
    NotificationDeleteAPI,
    NotificationMarkReadAPI,
)

urlpatterns = [
    path('', NotificationListAPI.as_view(), name='list'),
    path('mark-all-read/', MarkAllReadAPI.as_view(), name='mark-all-read'),
    path('<int:pk>/', NotificationDeleteAPI.as_view(), name='delete'),
    path('<int:pk>/read/', NotificationMarkReadAPI.as_view(), name='mark-read'),
]
