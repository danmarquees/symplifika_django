from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Notification
from .serializers import NotificationSerializer
from .services import NotificationService

class NotificationListAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        unread_only = request.query_params.get('unread_only', 'false').lower() == 'true'
        limit = request.query_params.get('limit')

        if limit:
            try:
                limit = int(limit)
            except ValueError:
                limit = None

        notifications = NotificationService.get_notifications(
            user_id=request.user,
            limit=limit,
            unread_only=unread_only
        )
        unread_count = NotificationService.get_unread_count(request.user)

        serializer = NotificationSerializer(notifications, many=True)
        return Response({
            'notifications': serializer.data,
            'unread_count': unread_count
        })

    def post(self, request):
        title = request.data.get('title')
        message = request.data.get('message')

        if not title or not message:
            return Response(
                {'detail': 'Title and message are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        notification = NotificationService.create_notification(
            user_id=request.user,
            title=title,
            message=message
        )

        if notification:
            serializer = NotificationSerializer(notification)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {'detail': 'Failed to create notification.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

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
