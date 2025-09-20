from typing import Optional, Union
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()

class NotificationService:
    @staticmethod
    def create_notification(
        user_id: Union[int, User],
        title: str,
        message: str,
    ) -> Optional[Notification]:
        """
        Create a new notification for a user.

        Args:
            user_id: User ID or User instance
            title: Notification title
            message: Notification message

        Returns:
            Notification instance if successful, None otherwise
        """
        try:
            if isinstance(user_id, User):
                user = user_id
            else:
                user = User.objects.get(id=user_id)

            notification = Notification.objects.create(
                user=user,
                title=title,
                message=message
            )
            return notification
        except User.DoesNotExist:
            return None
        except Exception as e:
            print(f"Error creating notification: {str(e)}")
            return None

    @staticmethod
    def get_unread_count(user_id: Union[int, User]) -> int:
        """
        Get the count of unread notifications for a user.

        Args:
            user_id: User ID or User instance

        Returns:
            Number of unread notifications
        """
        try:
            if isinstance(user_id, User):
                user = user_id
            else:
                user = User.objects.get(id=user_id)

            return Notification.objects.filter(user=user, is_read=False).count()
        except User.DoesNotExist:
            return 0
        except Exception as e:
            print(f"Error getting unread count: {str(e)}")
            return 0

    @staticmethod
    def get_notifications(
        user_id: Union[int, User],
        limit: Optional[int] = None,
        unread_only: bool = False
    ):
        """
        Get notifications for a user.

        Args:
            user_id: User ID or User instance
            limit: Optional limit of notifications to return
            unread_only: If True, return only unread notifications

        Returns:
            QuerySet of notifications
        """
        try:
            if isinstance(user_id, User):
                user = user_id
            else:
                user = User.objects.get(id=user_id)

            notifications = Notification.objects.filter(user=user)

            if unread_only:
                notifications = notifications.filter(is_read=False)

            if limit:
                notifications = notifications[:limit]

            return notifications
        except User.DoesNotExist:
            return Notification.objects.none()
        except Exception as e:
            print(f"Error getting notifications: {str(e)}")
            return Notification.objects.none()

    @staticmethod
    def bulk_create_notifications(
        user_ids: list[Union[int, User]],
        title: str,
        message: str
    ) -> bool:
        """
        Create notifications for multiple users at once.

        Args:
            user_ids: List of User IDs or User instances
            title: Notification title
            message: Notification message

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            notifications = []
            users = []

            # Convert all user_ids to User instances
            for user_id in user_ids:
                if isinstance(user_id, User):
                    users.append(user_id)
                else:
                    try:
                        user = User.objects.get(id=user_id)
                        users.append(user)
                    except User.DoesNotExist:
                        continue

            # Create notification objects
            for user in users:
                notifications.append(
                    Notification(
                        user=user,
                        title=title,
                        message=message
                    )
                )

            # Bulk create notifications
            if notifications:
                Notification.objects.bulk_create(notifications)
                return True

            return False
        except Exception as e:
            print(f"Error in bulk notification creation: {str(e)}")
            return False
