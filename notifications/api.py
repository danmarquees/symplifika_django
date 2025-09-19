from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer

class NotificationListAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

from rest_framework import status

class MarkAllReadAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'detail': 'Todas as notificações marcadas como lidas.'}, status=status.HTTP_200_OK)

class NotificationDeleteAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
            notification.delete()
            return Response({'detail': 'Notificação deletada.'}, status=status.HTTP_204_NO_CONTENT)
        except Notification.DoesNotExist:
            return Response({'detail': 'Notificação não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

class NotificationMarkReadAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
            notification.is_read = True
            notification.save()
            return Response({'detail': 'Notificação marcada como lida.'})
        except Notification.DoesNotExist:
            return Response({'detail': 'Notificação não encontrada.'}, status=status.HTTP_404_NOT_FOUND)
