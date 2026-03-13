from datetime import datetime
from typing import List, TypedDict
from uuid import UUID

from ..exceptions import NotificationNotFoundException
from ..models import Notification
from ..repositories import NotificationRepository


class NotificationResDict(TypedDict):
    id: int
    type: str
    sent_at: datetime
    is_read: bool
    sender_email: str | None
    application_name: str | None
    application_uuid: UUID | None
    request_uuid: UUID | None
    processing_context_uuid: UUID | None
    payload: dict | None


class NotificationService:
    @staticmethod
    def get_notifications_by_user_id(current_user_id: int, only_unread: bool, limit: int, offset: int) -> List[NotificationResDict]:
        iterator = NotificationRepository.get_notifications_by_user_id(current_user_id, only_unread, limit, offset)
        return [
            {
                "id": notification.id,
                "type": notification.type.value,
                "sent_at": notification.sent_at,
                "is_read": is_read,
                "sender_email": notification.sender_email,
                "application_name": application_name,
                "application_uuid": application_uuid,
                "request_uuid": request_uuid,
                "processing_context_uuid": processing_context_uuid,
                "payload": notification.payload,
            }
            for notification, is_read, application_name, application_uuid, request_uuid, processing_context_uuid in iterator
        ]

    @staticmethod
    def get_unread_notifications_count_by_user_id(current_user_id: int) -> int:
        return NotificationRepository.get_unread_notifications_count_by_user_id(current_user_id)

    @staticmethod
    def mark_notification_as_read_by_user_id(current_user_id: int, notification_id: int) -> Notification:
        notification = NotificationRepository.mark_notification_as_read_by_user_id(current_user_id, notification_id)
        if not notification:
            raise NotificationNotFoundException(
                f"Notification with id {notification_id} not found among your notifications!"
            )
        return notification

    @staticmethod
    def mark_all_notifications_as_read_by_user_id(current_user_id: int) -> None:
        NotificationRepository.mark_all_notifications_as_read_by_user_id(current_user_id)
        return
