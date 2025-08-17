from rest_framework import serializers
from .models import SystemStats

class SystemStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemStats
        fields = [
            'total_users',
            'active_users',
            'total_shortcuts',
            'total_shortcut_uses',
            'total_ai_requests',
            'date',
        ]
